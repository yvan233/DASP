from os import system
import socket
import json
import sys
import time
import threading
import traceback
import struct
from datetime import datetime
# sys.path.insert(1,".")  # 把上一级目录加入搜索路径
# from DASP.module import DaspCommon, Task
from . import DaspCommon,Task
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
            headPack,body = self.recv_length(conn)
            self.MessageHandle(headPack,body,conn)
            conn.close()
               
    def recv_long_conn(self, host, port, adjID = ""):
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
                        self.RecvDisconnectHandle(addr, adjID)
                        break
                    if data == b"":
                        # 发送端close()
                        self.RecvDisconnectHandle(addr, adjID)
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
                            self.MessageHandle(headPack, body, conn)
                            # 数据出列
                            dataBuffer = dataBuffer[self.headerSize+bodySize:] # 获取下一个数据包，类似于把数据pop出

    def MessageHandle(self, headPack, body, conn):
        """
        数据处理函数,子类可重构该函数
        """
        if headPack[0] == 1:
            print(body)
        else:
            print("非POST方法")

    def RecvDisconnectHandle(self, addr, adjID):
        """
        对接收数据时邻居断开连接的操作函数               
        """
        print ("{}:{} 已断开".format(addr[0],addr[1]))      

    def PingID(self, host, port, adjID, direction):
        """
        尝试通过TCP连接指定节点
        """
        data = {
            "key": "ping",
            "id": DaspCommon.nodeID,
            "host": host,
            "port": port,
            "applydirection": direction
        }
        self.send(adjID, data)

    def connect(self, adjID, DAPPname):
        """
        发送连接请求
        如果没连上则改邻居不在线；如果连接上并收到connect回应，则加入子节点中
        """
        data = {
            "key": "connect",
            "id": DaspCommon.nodeID,
            "DAPPname": DAPPname
        }

        returnflag = self.send(adjID, data)
        if returnflag == "Communication Succeeded":
            headPack,jres = self.recv_length(DaspCommon.adjSocket[adjID])
            if jres['key'] == 'connect':
                BaseServer.TaskDict[DAPPname].sonID.append(jres["id"])
                indext = DaspCommon.adjID.index(jres["id"])
                BaseServer.TaskDict[DAPPname].sonDirection.append(self.adjDirection[indext])
                BaseServer.TaskDict[DAPPname].CreateTreeSonFlag.append(0)
                BaseServer.TaskDict[DAPPname].sonData.append([])
        return returnflag
        
    def send(self,id,data):
        """
        通过TCP的形式将信息发送至指定ID的节点
        """
        # 如果之前没建立连接，则建立长连接
        if id not in DaspCommon.adjSocket: 
            try:
                for ele in DaspCommon.IPlist:
                    if ele[4] == id:
                        host = ele[2]
                        port = ele[3]
                        break
                print ("connecting to {}:{}".format(host,str(port)))
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.set_keep_alive(sock)
                remote_ip = socket.gethostbyname(host)
                sock.connect((remote_ip, port))
                DaspCommon.adjSocket[id] = sock
            except Exception as e:
                print ("与邻居节点{}连接失败".format(id))
                self.deleteadjID(id)
                self.deleteTaskDictadjID(id)
                self.sendRunDatatoGUI("与邻居节点{0}连接失败".format(id)) 
                return id

        # 向相应的套接字发送消息
        try:
            self.sendall_length(DaspCommon.adjSocket[id], data)
            return "Communication Succeeded"
        except Exception as e:
            return self.SendDisconnectHandle(id, data)
    
    def SendDisconnectHandle(self, id, data):
        """
        对发送数据时邻居断开连接的操作函数               
        """
        times = 0
        
        for ele in DaspCommon.IPlist:
            if ele[4] == id:
                host = ele[2]
                port = ele[3]
                break
        # 失败后每隔30s共重连10次
        while times < 10:
            times += 1
            if id in DaspCommon.adjSocket:
                del DaspCommon.adjSocket[id]
            try:
                print ("reconnecting to {}:{}, times:{}".format(host,str(port),times))
                self.sendRunDatatoGUI("与邻居节点{}连接失败，第{}次重连中...".format(id,times))
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.set_keep_alive(sock)
                remote_ip = socket.gethostbyname(host)
                sock.connect((remote_ip, port))
                DaspCommon.adjSocket[id] = sock
                self.sendall_length(DaspCommon.adjSocket[id], data)
                return "Communication Succeeded"
            except Exception as e:
                time.sleep(30)
        print ("与邻居节点{0}连接失败".format(id))
        self.deleteadjID(id)
        self.deleteTaskadjID(id)
        self.sendRunDatatoGUI("与邻居节点{0}连接失败，已删除和{0}的连接".format(id)) 
        return id

    def Forward2sonID(self, jdata, DAPPname):
        """
        将json消息转发给子节点
        """
        if BaseServer.TaskDict[DAPPname].sonID:
            for ele in reversed(BaseServer.TaskDict[DAPPname].TaskIPlist):
                if ele:
                    if ele[4] in BaseServer.TaskDict[DAPPname].sonID:
                        self.send(ele[4], data=jdata)

    def deleteTaskDictadjID(self, id):  
        """
        删除本节点的任务和指定id邻居节点的所有连接(任务字典中的变量)
        """
        for key in BaseServer.TaskDict:
            BaseServer.TaskDict[key].deleteTaskadjID(id)       

    def sendRunDatatoGUI(self, info, DAPPname = "system"):
        """
        通过UDP的形式将运行信息发送至GUI
        """
        self.sendtoGUIbase(info, "RunData", DAPPname)

    def sendEndDatatoGUI(self, info, DAPPname = "system"):
        """
        通过UDP的形式将结束信息发送至GUI
        """
        self.sendtoGUIbase(info, "EndData", DAPPname)

    def sendFlagtoGUI(self, info, DAPPname = "system"):
        """
        通过UDP的形式将运行状态发送至GUI  
        #0 未启动
        #1 暂停中
        #2 运行中
        """
        self.sendtoGUIbase(info, "RunFlag", DAPPname)

    def systemtask(self):
        """
        系统任务，不断ping邻居节点，维护拓扑
        """
        i = 0
        self.sendRunDatatoGUI("{}节点启动".format(DaspCommon.nodeID))
        while(True):
            i = i + 1
            for ele in reversed(DaspCommon.IPlist):
                if ele:
                    index = DaspCommon.adjID.index(ele[4])
                    self.PingID(ele[0], ele[1], ele[4], DaspCommon.adjDirectionOtherSide[index])

            self.sendRunDatatoGUI("系统第{}次自检：当前邻居节点：{}".format(i,str(DaspCommon.adjID)))
            time.sleep(SYSTEMSETTIME)
     

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
        self.ResultThreads = threading.Thread(target=self.ResultForwarding,args=())
        self.ResultThreads.start()

    def run(self):
        """
        服务器开始运行
        """
        print ("TaskServer on: {}:{}".format(self.host,str(self.port)))
        self.recv_short_conn(self.host, self.port)

    def MessageHandle(self, headPack, body, conn):
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
        name = jdata["DAPPname"]
        self.sendRunDatatoGUI("接收任务请求",name)
        BaseServer.TaskDict[name] = Task(name)
        BaseServer.TaskDict[name].load()

        # 建立通信树
        sum = 0
        for ele in reversed(BaseServer.TaskDict[name].TaskIPlist):
            if ele:
                if self.connect(ele[4], name) == "Communication Succeeded":
                    sum += 1
                    
        if(sum == 0): BaseServer.TaskDict[name].treeFlag = 1   #只有一个节点的情况
        while (BaseServer.TaskDict[name].treeFlag == 0): {time.sleep(0.01)}
        self.sendRunDatatoGUI("通信树建立完成",name)

        #启动任务
        self.Forward2sonID(jdata,name)
        BaseServer.TaskDict[name].load_debuginfo(DebugMode = jdata["DebugMode"], 
            DatabaseInfo = jdata["DatabaseInfo"], ObservedVariable = jdata["ObservedVariable"])
        # BaseServer.TaskDict[name].LeaderElection()
        BaseServer.TaskDict[name].taskBeginFlag = 1
        
        self.sendFlagtoGUI(2,name)

    def ResultForwarding(self):
        """
        根节点等待所有任务的数据收集结束标志，随后将计算结果转发到GUI界面
        """
        while 1:
            time.sleep(0.1)
            for key in BaseServer.TaskDict:
                if BaseServer.TaskDict[key].dataEndFlag == 1:
                    # time.sleep(1)   # 防止结果显示超前其他节点
                    BaseServer.TaskDict[key].sendRunDatatoGUI("任务数据收集完毕")
                    info = []
                    content = ""
                    Que = BaseServer.TaskDict[key].resultinfoQue
                    for i in range(len(Que)):
                        if Que[i]["info"]:
                            info.append({})
                            info[-1]["ID"] = Que[i]["id"]
                            info[-1]["value"] = str(Que[i]["info"]["value"])
                    
                    infojson = json.dumps(info, indent=2)  #格式化输出，更便于查看
                    content =  "Nodes number:{}\nInfo:{}\n\n".format(len(Que), infojson)
                    self.sendEndDatatoGUI(content,BaseServer.TaskDict[key].DAPPname)
                    self.sendFlagtoGUI(0,BaseServer.TaskDict[key].DAPPname)
                    BaseServer.TaskDict[key].taskEndFlag = 0
                    BaseServer.TaskDict[key].dataEndFlag = 0
                    BaseServer.TaskDict[key].resultinfoQue = []
                    BaseServer.TaskDict[key].resultinfo = {}

    def pausetask(self, jdata):
        """
        暂停DAPP
        """
        name = (jdata["DAPPname"])
        self.Forward2sonID(jdata, name)
        BaseServer.TaskDict[name].pause()
        self.sendFlagtoGUI(1,name)

    def resumetask(self, jdata):
        """
        恢复DAPP
        """
        name = (jdata["DAPPname"])
        self.Forward2sonID(jdata, name)
        BaseServer.TaskDict[name].resume()
        self.sendFlagtoGUI(2,name)

    def shutdowntask(self, jdata):
        """
        停止DAPP
        """
        name = jdata["DAPPname"]
        self.Forward2sonID(jdata,name)
        BaseServer.TaskDict[name].shutdown()
        self.sendFlagtoGUI(0,name)

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

    def MessageHandle(self, headPack, body, conn):
        """
        数据处理函数
        """
        try:
            jdata = body
            if headPack[0] == 1:
                #建立通信树
                if jdata["key"] == "ping":
                    self.RespondPing(jdata)

                elif jdata["key"] == "connect":
                    self.RespondConnect(conn, jdata)
                    
                elif jdata["key"] == "OK":
                    self.RespondOK(jdata)

                elif jdata["key"] == "newtask":
                    self.RespondNewTask(jdata)

                elif jdata["key"] == "shutdowntask":
                    self.RespondShutDownTask(jdata)

                elif jdata["key"] == "pausetask":
                    self.RespondPauseTask(jdata)
                
                elif jdata["key"] == "resumetask":
                    self.RespondResumeTask(jdata)

                elif jdata["key"] == "data":
                    self.RespondData(jdata)

                elif jdata["key"] == "questionData":
                    self.RespondQuestionData(jdata)

                elif jdata["key"] == "RootData":
                    self.RespondRootData(jdata)

                elif jdata["key"] == "DescendantData":
                    self.RespondDescendantData(jdata)

                elif jdata["key"] == "sync":
                    self.RespondSync(jdata,1)

                elif jdata["key"] == "sync2":
                    self.RespondSync(jdata,2)

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

    def RespondPing(self, jdata):
        """
        回应ping信号，如果发送的节点之前不在邻居节点中 且 申请方向未被占用，则加入网络
        """
        id = jdata["id"]
        if id not in DaspCommon.adjID:
            if jdata["applydirection"] not in DaspCommon.adjDirection:
                direction = jdata["applydirection"] - 1
                DaspCommon.IPlist.append([self.IP,self.PORT[direction],jdata["host"],jdata["port"],jdata["id"]])
                DaspCommon.adjID.append(jdata["id"])
                DaspCommon.adjDirection.append(jdata["applydirection"])
                self.sendRunDatatoGUI("与邻居节点{0}重连成功，已添加和{0}的连接".format(jdata["id"])) 
            else:
                info = "节点{}方向{}已被占用，请选择其他方向！".format(DaspCommon.nodeID,str(jdata["applydirection"]))
                self.sendRunDatatoGUI(info)
        
    def RespondConnect(self, conn, jdata):
        """
        回应连接请求
        如果在通信树中则发送回已连接消息
        如果不在通信树中则新建一个Task实例并加入通信树，并转发连接请求
        加入通信树后如果是叶子节点向父节点发送OK信号
        """
        name = jdata["DAPPname"]
        # 如果当前节点已经在通信树中，则发回connect消息
        if name in BaseServer.TaskDict:
            if BaseServer.TaskDict[name].commTreeFlag == 1:
                data = {
                    "key": "connected",
                    "id": DaspCommon.nodeID,
                    "DAPPname": name
                }
                self.sendall_length(conn, data)
                return 0

        # 如果当前节点不在通信树中，则加入通信树
        BaseServer.TaskDict[name] = Task(name)
        BaseServer.TaskDict[name].load()
        BaseServer.TaskDict[name].parentID = jdata["id"]
        indext = DaspCommon.adjID.index(jdata["id"])
        BaseServer.TaskDict[name].parentDirection = DaspCommon.adjDirection[indext]
        data = {
            "key": "connect",
            "id": DaspCommon.nodeID,
            "DAPPname": name
        }
        self.sendall_length(conn, data)
        
        for ele in reversed(BaseServer.TaskDict[name].TaskIPlist):
            if ele:
                if ele[4] != BaseServer.TaskDict[name].parentID:
                    self.connect(ele[4], name)

        #如果是叶子结点
        if len(BaseServer.TaskDict[name].sonID) == 0:
            data = {
                "key": "OK",
                "id": DaspCommon.nodeID,
                "DAPPname": name
            }
            self.send(BaseServer.TaskDict[name].parentID, data=data)
            for i in range(len(BaseServer.TaskDict[name].CreateTreeSonFlag)):
                BaseServer.TaskDict[name].CreateTreeSonFlag[i] = 0

    def RespondOK(self, jdata):
        """
        回应OK信号，如果所有子节点都OK则向父节点发送OK信号
        如果自己是根节点则通信树建立完毕
        """
        name = jdata["DAPPname"]
        data = {
            "key": "OK",
            "id": DaspCommon.nodeID,
            "DAPPname": name
        }
        for i in range(len(BaseServer.TaskDict[name].sonID)):
            if BaseServer.TaskDict[name].sonID[i] == jdata["id"]:
                BaseServer.TaskDict[name].CreateTreeSonFlag[i] = 1

        if all(BaseServer.TaskDict[name].CreateTreeSonFlag):
            if BaseServer.TaskDict[name].parentID != DaspCommon.nodeID:
                self.send(BaseServer.TaskDict[name].parentID, data=data)
            else:
                BaseServer.TaskDict[name].treeFlag = 1
                print ("The communication tree has been constructed!")
            for i in range(len(BaseServer.TaskDict[name].CreateTreeSonFlag)):
                BaseServer.TaskDict[name].CreateTreeSonFlag[i] = 0

    def RespondNewTask(self, jdata):
        """
        回应新任务信号，广播子节点启动任务信号，启动任务DAPP
        """
        name = (jdata["DAPPname"])
        self.Forward2sonID(jdata, name)
        BaseServer.TaskDict[name].load_debuginfo(DebugMode = jdata["DebugMode"], 
            DatabaseInfo = jdata["DatabaseInfo"], ObservedVariable = jdata["ObservedVariable"])
        # BaseServer.TaskDict[name].LeaderElection()
        BaseServer.TaskDict[name].taskBeginFlag = 1
        

    def RespondPauseTask(self, jdata):
        """
        回应暂停任务信号，广播子节点暂停任务信号，暂停任务DAPP
        """
        name = (jdata["DAPPname"])
        self.Forward2sonID(jdata, name)
        BaseServer.TaskDict[name].pause()

    def RespondResumeTask(self, jdata):
        """
        回应恢复任务信号，广播子节点恢复任务信号，恢复任务DAPP
        """
        name = (jdata["DAPPname"])
        self.Forward2sonID(jdata, name)
        BaseServer.TaskDict[name].resume()

    def RespondShutDownTask(self, jdata):
        """
        回应结束任务信号，广播子节点结束任务信号，结束任务DAPP
        """
        name = (jdata["DAPPname"])
        self.Forward2sonID(jdata, name)
        BaseServer.TaskDict[name].shutdown()

    def RespondData(self, jdata):
        """
        回应子节点任务结束信号，并收集数据
        """
        name = jdata["DAPPname"]
        index = BaseServer.TaskDict[name].sonID.index(jdata["id"])
        BaseServer.TaskDict[name].sonData[index] = jdata["data"]
        if all(BaseServer.TaskDict[name].sonData):
            BaseServer.TaskDict[name].sonDataEndFlag = 1

    def RespondQuestionData(self, jdata):
        """
        回应任务发送数据信号，并存储数据
        """
        name = jdata["DAPPname"]
        index = BaseServer.TaskDict[name].TaskadjID.index(jdata["id"])
        if jdata["type"] == "value":
            BaseServer.TaskDict[name].adjData[index] = jdata["data"]

        elif jdata["type"] == "value2":
            BaseServer.TaskDict[name].adjData_another[index] = jdata["data"]

    def RespondRootData(self, jdata):
        """回应任务发送数据至根节点信号

        返回值：
            data: 后代节点数据
            path: 后代节点发送过来的路径
            recvtime: 接受到消息的时刻
        """
        task_cur = BaseServer.TaskDict[jdata["DAPPname"]]
        # 如果本节点是根节点则存储数据
        if task_cur.parentID == DaspCommon.nodeID:
            # 加入接收消息的时间，方便时间同步
            task_cur.descendantData.put([jdata["data"], jdata["path"], datetime.now()])
        # 否则将数据转发给父节点
        else:  
            jdata["path"].append(DaspCommon.nodeID)
            self.send(task_cur.parentID, jdata)

    def RespondDescendantData(self, jdata):
        """回应任务发送数据至后代节点信号

        返回值：
            data: 根节点数据
            recvtime: 接受到消息的时刻
        """
        task_cur = BaseServer.TaskDict[jdata["DAPPname"]]
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
            self.Forward2sonID(jdata, jdata["DAPPname"])
            task_cur.rootData.put([jdata["data"], datetime.now()])


    def RespondSync(self, jdata, type):
        """
        回应同步请求，并改变相应标志位
        """
        name = jdata["DAPPname"]
        index = BaseServer.TaskDict[name].TaskadjID.index(jdata["id"])
        if type == 1:
            BaseServer.TaskDict[name].adjSyncStatus[index] = 1
        else:
            BaseServer.TaskDict[name].adjSyncStatus2[index] = 1

if __name__ == '__main__':


    DaspCommon.nodeID = "room_2"
    task = Task("debugDAPP")
    task.load()
    BaseServer.TaskDict["debugDAPP"] = task
    BaseServer.TaskDict["debugDAPP"].load_debuginfo()
    BaseServer.TaskDict["debugDAPP"].taskBeginFlag = 1