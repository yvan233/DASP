import csv
import json
import os
import socket
import struct
import threading
import time
import traceback
from datetime import datetime
from . import DaspCommon, TcpSocket, Task

SYSTEMSETTIME = 120

class BaseServer(DaspCommon):
    '''基础服务器

    Dsp基础服务器

    属性:
        TaskDict: 任务字典
    '''
    TaskDict = {}

    def __init__(self):
        pass

    def recv_short_conn(self, host, port):
        '''
        短连接循环接收数据框架
        '''   
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(100) #接收的连接数
        while True:
            conn, addr = server.accept()
            # print('Connected by', addr)
            headPack,body = TcpSocket.recv(conn)
            self.handleMessage(headPack,body,conn)
            conn.close()
               
    def recv_long_conn(self, host, port, nbrID = ""):
        """
        长连接循环接收数据框架
        """
        while True:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((host, port))
            server.listen(1) #接收的连接数
            conn, addr = server.accept()
            print('Connected by {}:{}'.format(addr[0], addr[1]))
            # FIFO消息队列
            dataBuffer = bytes()
            with conn:
                while True:
                    try:
                        data = conn.recv(1024)
                    except Exception as e:
                        # 发送端进程被杀掉
                        self.handleRecvDisconnection(addr, nbrID)
                        break
                    if data == b"":
                        # 发送端close()
                        self.handleRecvDisconnection(addr, nbrID)
                        break
                    if data:
                        # 把数据存入缓冲区，类似于push数据
                        dataBuffer += data
                        while True:
                            if len(dataBuffer) < self.headerSize:
                                break  #数据包小于消息头部长度，跳出小循环
                            # 读取包头
                            headPack = struct.unpack(self.headformat, dataBuffer[:self.headerSize])
                            bodySize = headPack[1]
                            if len(dataBuffer) < self.headerSize+bodySize :
                                break  #数据包不完整，跳出小循环
                            # 读取消息正文的内容
                            body = dataBuffer[self.headerSize:self.headerSize+bodySize]
                            body = body.decode()
                            body = json.loads(body)
                            # 数据处理
                            self.handleMessage(headPack, body, conn)
                            # 数据出列
                            dataBuffer = dataBuffer[self.headerSize+bodySize:] # 获取下一个数据包，类似于把数据pop出

    def handleMessage(self, headPack, body, conn):
        """
        数据处理函数,子类可重构该函数
        """
        if headPack[0] == 1:
            print(body)
        else:
            print("非POST方法")

    def handleRecvDisconnection(self, addr, nbrID):
        """
        对接收数据时邻居断开连接的操作函数               
        """
        print ("{}:{} 已断开".format(addr[0],addr[1]))      

    def pingID(self, host, port, nbrID, direction):
        """
        尝试通过TCP连接指定节点
        """
        data = {
            "key": "ping",
            "id": DaspCommon.nodeID,
            "host": host,
            "port": port,
            "requestdirection": direction
        }
        self.send(nbrID, data)
        
    def send(self,id,data):
        """
        通过TCP的形式将信息发送至指定ID的节点
        """
        if id not in DaspCommon.nbrSocket: 
            try:
                for ele in DaspCommon.RouteTable:
                    if ele[4] == id:
                        ip = ele[2]
                        port = ele[3]
                        break
                print (f"connecting to {ip}:{port}")
                remote_ip = socket.gethostbyname(ip)
                DaspCommon.nbrSocket[id] = TcpSocket(id,remote_ip,port,self)
            except:
                # self.sendRunDatatoGUI(f"连接{ip}:{port}失败")
                self.deleteTaskNbrID(id)
                return 0

        try:
            DaspCommon.nbrSocket[id].sendall(data)
        except:
            DaspCommon.nbrSocket[id].do_fail()
        else:
            DaspCommon.nbrSocket[id].do_pass()

    def forward2childID(self, jdata, DappName):
        """
        将json消息转发给子节点
        """
        if BaseServer.TaskDict[DappName].childID:
            for ele in reversed(BaseServer.TaskDict[DappName].taskRouteTable):
                if ele:
                    if ele[4] in BaseServer.TaskDict[DappName].childID:
                        self.send(ele[4], data=jdata)

    def deleteTaskNbrID(self, id):  
        """
        删除本节点的任务和指定id邻居节点的所有连接(任务字典中的变量)
        """
        self.deletenbrID(id)
        for key in BaseServer.TaskDict:
            BaseServer.TaskDict[key].deleteTaskNbrID(id)       
        self.sendRunDatatoGUI(f"与邻居节点{id}连接失败，已删除和{id}的连接") 

    def sendRunDatatoGUI(self, info, DappName = "system"):
        """
        通过UDP的形式将运行信息发送至GUI
        """
        self.sendtoGUIbase(info, "RunData", DappName)

    def sendFlagtoGUI(self, info, DappName = "system"):
        """
        通过UDP的形式将运行状态发送至GUI  
        #0 未启动
        #1 暂停中
        #2 运行中
        """
        self.sendtoGUIbase(info, "RunFlag", DappName)

class TaskServer(BaseServer):
    """外部交互服务器
    
    用于节点和外部交互
    
    属性:
        host: 绑定IP
        port: 绑定port
        ResultThreads: 结果转发多线程
    """
    def __init__(self,host,port):
        self.host = host
        self.port = port
        self.ResultThreadsFlag = 0

    def run(self):
        """
        服务器开始运行
        """
        print ("TaskServer on: {}:{}".format(self.host,str(self.port)))
        self.recv_short_conn(self.host, self.port)

    def handleMessage(self, headPack, body, conn):
        """
        数据处理函数,子类可重构该函数
        """
        try:
            jdata = body
            if headPack[0] == 1:
                if jdata["key"] == "newtask":
                    self.newtask(jdata)

                elif jdata["key"] == "pausetask":
                    self.pausetask(jdata)

                elif jdata["key"] == "resumetask":
                    self.resumetask(jdata)
                    
                elif jdata["key"] == "shutdowntask":
                    self.shutdowntask(jdata)

                else:
                    info = "您输入的任务信息有误！"
                    self.sendall_length(conn, info, methods = 9)
            else:
                info = "暂未提供POST以外的接口"
                self.sendall_length(conn, info, methods = 9)
        except Exception as e:
            self.sendRunDatatoGUI("任务服务器执行出错")
            print(traceback.format_exc())
            self.sendRunDatatoGUI(traceback.format_exc())

    def newtask(self, jdata): 
        """
        启动DAPP，加载任务、建立通信树、启动任务、启动数据转发线程
        """
        name = jdata["DappName"]
        self.sendRunDatatoGUI("接收任务请求",name)
        task = Task(name)
        BaseServer.TaskDict[name] = task
        task.load()
        task.startCommPattern()

    def pausetask(self, jdata):
        """
        暂停DAPP
        """
        name = (jdata["DappName"])
        self.forward2childID(jdata, name)
        BaseServer.TaskDict[name].pause()
        self.sendFlagtoGUI(1,name)

    def resumetask(self, jdata):
        """
        恢复DAPP
        """
        name = (jdata["DappName"])
        self.forward2childID(jdata, name)
        BaseServer.TaskDict[name].resume()
        self.sendFlagtoGUI(2,name)

    def shutdowntask(self, jdata):
        """
        停止DAPP
        """
        name = jdata["DappName"]
        self.forward2childID(jdata,name)
        BaseServer.TaskDict[name].shutdown()
        self.sendFlagtoGUI(0,name)

    def systemtask(self):
        """
        系统任务，不断ping邻居节点，维护拓扑
        """
        i = 0
        self.sendRunDatatoGUI("{}节点启动".format(DaspCommon.nodeID))
        while(True):
            i = i + 1
            for ele in reversed(DaspCommon.RouteTable):
                if ele:
                    index = DaspCommon.nbrID.index(ele[4])
                    self.pingID(ele[0], ele[1], ele[4], DaspCommon.nbrDirectionOtherSide[index])

            if i == 1:  
                # 第一轮开启系统自启动任务进程
                self.startthreads = threading.Thread(target=self.autostarttask, args=())
                self.startthreads.start()

                # # 执行alst算法
                # task = Task("ALST")
                # task.load()
                # task.startCommPattern()
                # BaseServer.TaskDict["ALST"] = task

            self.sendRunDatatoGUI("系统第{}次自检：当前邻居节点：{}".format(i,str(DaspCommon.nbrID)))
            time.sleep(SYSTEMSETTIME)
     
    def autostarttask(self):
        """
        启动开机自启动任务
        """
        path = os.getcwd() + "/Dapp/Base/autostart.csv"
        with open(path,'r',encoding='utf-8-sig')as f:
            data = csv.reader(f)
            dapp_autostart = []
            for i in data:
                dapp_autostart.append(i)
        del dapp_autostart[0]        
        # 依据time排序
        dapp_autostart = sorted(dapp_autostart,key=(lambda x:x[2]))
        beforetime = 0
        for ele in dapp_autostart:
            time.sleep(float(ele[2]) - beforetime)
            if ele[1] == "default":  # 默认模式，以当前网络字典序最小的节点启动算法
                name = ele[0]
                BaseServer.TaskDict[name] = Task(name)
                BaseServer.TaskDict[name].load()
                BaseServer.TaskDict[name].reset()
                ## 如果当前节点在任务中
                if DaspCommon.nodeID in BaseServer.TaskDict[name].taskID:
                    # self.sendRunDatatoGUI("寻找leader节点",name)
                    BaseServer.TaskDict[name].startCommPattern()
                    while(BaseServer.TaskDict[name].leader == None): time.sleep(0.1)
                    if BaseServer.TaskDict[name].leader == DaspCommon.nodeID:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect((self.host, self.port))
                        data = {
                            "key": "newtask",
                            "DappName": ele[0],
                            "DebugMode": False, 
                            "DatabaseInfo": [],
                            "ObservedVariable": []
                        }
                        self.sendall_length(s, data)
                        s.close()

            elif ele[1] == DaspCommon.nodeID:  #本节点为根节点
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.host, self.port))
                data = {
                    "key": "newtask",
                    "DappName": ele[0],
                    "DebugMode": False, 
                    "DatabaseInfo": [],
                    "ObservedVariable": []
                }
                self.sendall_length(s, data)
                s.close()
            else:  #启动节点为其他节点
                pass

            beforetime = float(ele[2])

class CommServer(BaseServer):
    """
    通信服务器，用于节点和其他节点通信
    """
    host = "locolhost"
    port = 10000

    def __init__(self,host,port):
        self.host = host
        self.port = port

    def run(self):
        """
        服务器开始运行
        """
        print ("CommServer on: {}:{}".format(self.host,str(self.port)))
        self.recv_long_conn(self.host, self.port)

    def handleMessage(self, headPack, body, conn):
        """
        数据处理函数
        """
        try:
            jdata = body
            if headPack[0] == 1:
                #建立通信树
                if jdata["key"] == "ping":
                    self.respondPing(jdata)

                elif jdata["key"] == "shutdowntask":
                    self.respondShutDownTask(jdata)

                elif jdata["key"] == "pausetask":
                    self.respondPauseTask(jdata)
                
                elif jdata["key"] == "resumetask":
                    self.respondResumeTask(jdata)

                elif jdata["key"] == "data":
                    self.respondData(jdata)

                elif jdata["key"] == "questionData":
                    self.respondQuestionData(jdata)
                    
                elif jdata["key"] == "AsynchData":
                    self.respondAsynchData(jdata)

                elif jdata["key"] == "AlstData":
                    self.respondAlstData(jdata)

                elif jdata["key"] == "RootData":
                    self.respondRootData(jdata)

                elif jdata["key"] == "DescendantData":
                    self.respondDescendantData(jdata)

                elif jdata["key"] == "sync":
                    self.respondSync(jdata,1)

                elif jdata["key"] == "sync2":
                    self.respondSync(jdata,2)

                else:
                    info = "请不要直接访问通信服务器"
                    self.sendall_length(conn, info, methods = 9)

            else:
                info = "非POST方法，请不要直接访问通信服务器"
                self.sendall_length(conn, info, methods = 9)
                
        except Exception as e:
            self.sendRunDatatoGUI("通信服务器执行出错")
            print(traceback.format_exc())
            self.sendRunDatatoGUI(traceback.format_exc())

    def respondPing(self, jdata):
        """
        回应ping信号，如果发送的节点之前不在邻居节点中 且 申请方向未被占用，则加入网络
        """
        id = jdata["id"]
        if id not in DaspCommon.nbrID:
            if jdata["requestdirection"] not in DaspCommon.nbrDirection:
                direction = jdata["requestdirection"] - 1
                DaspCommon.RouteTable.append([self.IP,self.Port[direction],jdata["host"],jdata["port"],jdata["id"]])
                DaspCommon.nbrID.append(jdata["id"])
                DaspCommon.nbrDirection.append(jdata["requestdirection"])
                self.sendRunDatatoGUI("与邻居节点{0}重连成功，已添加和{0}的连接".format(jdata["id"])) 
            else:
                info = "节点{}方向{}已被占用，请选择其他方向！".format(DaspCommon.nodeID,str(jdata["requestdirection"]))
                self.sendRunDatatoGUI(info)

        
    def respondPauseTask(self, jdata):
        """
        回应暂停任务信号，广播子节点暂停任务信号，暂停任务DAPP
        """
        name = (jdata["DappName"])
        self.forward2childID(jdata, name)
        BaseServer.TaskDict[name].pause()

    def respondResumeTask(self, jdata):
        """
        回应恢复任务信号，广播子节点恢复任务信号，恢复任务DAPP
        """
        name = (jdata["DappName"])
        self.forward2childID(jdata, name)
        BaseServer.TaskDict[name].resume()

    def respondShutDownTask(self, jdata):
        """
        回应结束任务信号，广播子节点结束任务信号，结束任务DAPP
        """
        name = (jdata["DappName"])
        self.forward2childID(jdata, name)
        BaseServer.TaskDict[name].shutdown()

    def respondData(self, jdata):
        """
        回应子节点任务结束信号，并收集数据
        """
        name = jdata["DappName"]
        index = BaseServer.TaskDict[name].childID.index(jdata["id"])
        BaseServer.TaskDict[name].childData[index] = jdata["data"]
        if all(BaseServer.TaskDict[name].childData):
            BaseServer.TaskDict[name].childDataEndFlag = 1

    def respondQuestionData(self, jdata):
        """
        回应任务发送数据信号，并存储数据
        """
        name = jdata["DappName"]
    
        index = BaseServer.TaskDict[name].taskNbrID.index(jdata["id"])
        if jdata["type"] == "value":
            BaseServer.TaskDict[name].nbrData[index] = jdata["data"]

        elif jdata["type"] == "value2":
            BaseServer.TaskDict[name].nbrData2[index] = jdata["data"]

    def respondAlstData(self, jdata):
        """
        回应任务发送数据信号，并存储数据
        """
        name = jdata["DappName"]
        if name not in BaseServer.TaskDict:
            task = Task(name)
            BaseServer.TaskDict[name] = task
            task.load()
            task.startCommPattern()
        elif BaseServer.TaskDict[name].commTreeFlag == 0:
            task = Task(name)
            BaseServer.TaskDict[name] = task
            task.load()
            task.startCommPattern()
        task = BaseServer.TaskDict[name]
        while(not hasattr(task,'loadflag')):time.sleep(0.01)
        while(task.loadflag == 0):time.sleep(0.01)
        index = task.taskNbrID.index(jdata["id"])
        task.nbrAlstData[index].put(jdata["data"])


    def respondAsynchData(self, jdata):
        """
        回应任务发送数据信号，并存储数据
        """
        name = jdata["DappName"]
        task = BaseServer.TaskDict[name]
        index = task.taskNbrID.index(jdata["id"])
        task.nbrAsynchData[index].put(jdata["data"])
            
    def respondRootData(self, jdata):
        """回应任务发送数据至根节点信号

        返回值：
            data: 后代节点数据
            path: 后代节点发送过来的路径
            recvtime: 接受到消息的时刻
        """
        task_cur = BaseServer.TaskDict[jdata["DappName"]]
        # 如果本节点是根节点则存储数据
        if task_cur.parentID == DaspCommon.nodeID:
            # 加入接收消息的时间，方便时间同步
            task_cur.descendantData.put([jdata["data"], jdata["path"], datetime.now()])
        # 否则将数据转发给父节点
        else:  
            jdata["path"].append(DaspCommon.nodeID)
            self.send(task_cur.parentID, jdata)

    def respondDescendantData(self, jdata):
        """回应任务发送数据至后代节点信号

        返回值：
            data: 根节点数据
            recvtime: 接受到消息的时刻
        """
        task_cur = BaseServer.TaskDict[jdata["DappName"]]
        # 如果指定了路径
        if jdata["path"] != None: 
            if jdata["path"]:
                nextnode = jdata["path"].pop()
                self.send(nextnode, jdata)
            # 如果目标是本节点
            else:
                task_cur.rootData.put([jdata["data"], datetime.now()])                
        # 否则进行广播
        else:
            self.forward2childID(jdata, jdata["DappName"])
            task_cur.rootData.put([jdata["data"], datetime.now()])

    def respondSync(self, jdata, type):
        """
        回应同步请求，并改变相应标志位
        """
        name = jdata["DappName"]
        while(name not in BaseServer.TaskDict):time.sleep(0.01)
        while(not hasattr(BaseServer.TaskDict[name],'loadflag')):time.sleep(0.01)
        while(BaseServer.TaskDict[name].loadflag == 0):time.sleep(0.01)
        index = BaseServer.TaskDict[name].taskNbrID.index(jdata["id"])
        if type == 1:
            BaseServer.TaskDict[name].nbrSyncStatus[index] = 1
        else:
            BaseServer.TaskDict[name].nbrSyncStatus2[index] = 1

if __name__ == '__main__':
    DaspCommon.nodeID = "room_2"
    task = Task("debugDAPP")
    task.load()
    BaseServer.TaskDict["debugDAPP"] = task
    BaseServer.TaskDict["debugDAPP"].load_debuginfo()
    BaseServer.TaskDict["debugDAPP"].taskBeginFlag = 1
