import socket
import ctypes
import inspect
import json
import sys
import time
import threading
sys.path.insert(1,".")  # 把上一级目录加入搜索路径
from DASP.module import DaspCommon, Task

class BaseServer(DaspCommon):
    '''基础服务器

    Dsp基础服务器

    属性:
        TaskDict: 任务字典
        commTreeFlag: 当前节点是否被加进通信树标志
        treeFlag: 通信树建立完成标志
    '''
    TaskDict = {}
    treeFlag = 0
    commTreeFlag = 0

    def __init__(self):
        pass

    def samlpe(self):
        '''基本描述

        详细描述

        Args:
            path (str): The path of the file to wrap
            field_storage (FileStorage): The :class:`FileStorage` instance to wrap
            temporary (bool): Whether or not to delete the file when the File instance is destructed

        Returns:
            BufferedFileStorage: A buffered writable file descriptor
        '''
        pass

    def connect(self,host1,port1,host2,port2,adjID,DAPPname):
        """
        连接
        """
        data = {
            "key": "connect",
            "host": host1,
            "port": port1,
            "id": DaspCommon.nodeID,
            "GUIinfo": DaspCommon.GUIinfo,
            "DAPPname": DAPPname
        }
        try:
            print ("{}:{} connecting to {}:{}".format(host1,str(port1),host2,str(port2)))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_ip = socket.gethostbyname(host2)
            sock.connect((remote_ip, port2))
            cont = "POST / HTTP/1.1\r\n"
            jsondata = json.dumps(data)
            self.sendall_length(sock, cont, jsondata)
            reply = self.recv_length(sock)
            res = reply.split('\r\n')[-1]
            jres = json.loads(res)
            if jres['key'] == 'connect':
                BaseServer.TaskDict[DAPPname].sonID.append(jres["id"])
                indext = DaspCommon.adjID.index(jres["id"])
                BaseServer.TaskDict[DAPPname].sonDirection.append(self.adjDirection[indext])
                BaseServer.TaskDict[DAPPname].CreateTreeSonFlag.append(0)
                BaseServer.TaskDict[DAPPname].sonData.append([])
            return 0
        except Exception as e:
            self.sendRunDatatoGUI("与邻居节点"+adjID+"连接失败", DAPPname) 
            print ("与邻居节点"+adjID+"连接失败")
            return adjID
                   
            
    def reconnect(self,host1,port1,host2,port2,adjID,direction):
        data = {
            "key": "newNode",
            "host": host1,
            "port": port1,
            "id": DaspCommon.nodeID,
            "applydirection": direction
        }
        try:
            print (host1 + ":" + str(port1) + " connecting to " + host2 + ":" + str(port2))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_ip = socket.gethostbyname(host2)
            sock.connect((remote_ip, port2))
            cont = "POST / HTTP/1.1\r\n"
            jsondata = json.dumps(data)
            self.sendall_length(sock, cont, jsondata)
            sock.close()
        except Exception as e:
            self.sendRunDatatoGUI("邻居节点"+adjID+"连接不上")
            # print(traceback.format_exc())
            print ("与邻居节点"+adjID+"连接失败")
            return adjID


    def send(self,id,data):
        """
        通过TCP的形式将信息发送至指定ID的节点
        """
        for ele in DaspCommon.IPlist:
            if ele!=[]:
                if ele[4] == id:
                    try:
                        host = ele[2]
                        port = ele[3]
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        remote_ip = socket.gethostbyname(host)
                        sock.connect((remote_ip, port))
                        cont = "POST / HTTP/1.1\r\n"
                        self.sendall_length(sock, cont, data)
                        sock.close()
                    except Exception as e:
                        print ("与邻居节点"+id+"连接失败")
                        self.sendDatatoGUI("与邻居节点"+id+"连接失败")
                        self.deleteadjID(id)
                        self.deleteTaskDictadjID(id)
                        self.sendDatatoGUI("已删除和邻居节点"+id+"的连接") 
                    break

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
        #1 运行中
        """
        self.sendtoGUIbase(info, "RunFlag", DAPPname)
            

class TaskServer(BaseServer):
    """外部交互服务器
    
    用于节点和外部交互
    
    属性:
        host: 绑定IP
        port: 绑定port
        ResultThreads: 结果转发多线程
        ResultThreadsFlag:  结果转发多线程创建标志
    """
    def __init__(self,host,port):
        self.host = host
        self.port = port
        self.ResultThreadsFlag = 0

    def run(self):
        """
        服务器开始运行
        """
        head = """HTTP/1.1 200 OK\r\n"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(100)
        print ("TaskServer on: {}:{}".format(self.host,str(self.port)))

        while 1:
            conn, addr = sock.accept()
            request = self.recv_length(conn)
            method = request.split(' ')[0]
            if method == "POST":
                data = request.split('\r\n')[-1]
                try:
                    jdata = json.loads(data)
                except (ValueError, KeyError, TypeError):
                    conn.send(str.encode(head + "请输入JSON格式的数据！"))
                else:
                    if jdata["key"] == "startsystem":
                        try:
                            DaspCommon.GUIinfo = jdata["GUIinfo"]
                            self.sendRunDatatoGUI("接收任务请求")
                        except KeyError:
                            print ("非来自GUI的任务请求")
                        self.startsystem()

                    # elif jdata["key"] == "newtask":
                    #     name = int(jdata["DAPPname"])
                    #     try:
                    #         DaspCommon.GUIinfo = jdata["GUIinfo"]
                    #         self.sendRunDatatoGUI("接收任务请求",name)
                    #     except KeyError:
                    #         print ("非来自GUI的任务请求")

                    #     self.loadNewTask(name)
                    #     self.createNewTask(name)
                    #     self.sendRunDatatoGUIflag(1,name)
                    #     self.reset(name)
                    #     BaseServer.TaskDict["system"].commTreeFlag[name] = 1
                    #     sum = 0
                    #     deleteID = []
                    #     for ele in self.TASKIPLIST[name]:
                    #         if ele != []:
                    #             returnID = self.connect(ele[0], ele[1], ele[2], ele[3], ele[4], name)
                    #             if returnID:
                    #                 deleteID.append(returnID)
                    #             sum += 1
                    #     for k in range(len(deleteID)):
                    #         self.deleteadjID(deleteID[k])

                    #     if(sum == 0): BaseServer.TaskDict["system"].treeFlag[name] = 1
                    #     while (BaseServer.TaskDict["system"].treeFlag[name] == 0): {time.sleep(0.01)}
                    #     self.sendRunDatatoGUI("通信树建立完成")
                    #     for ele in reversed(self.TASKIPLIST[name]):
                    #         if ele != []:
                    #             if ele[4] in DaspCommon.sonID[name]:
                    #                 sdata = {
                    #                     "key": "newtask",
                    #                     "GUIinfo": DaspCommon.GUIinfo,
                    #                     "DAPPname": jdata["DAPPname"]
                    #                 }
                    #                 sjdata = json.dumps(sdata)
                    #                 self.send(ele[4], data=sjdata)

                    #     delay = jdata["delay"]
                    #     if delay > 0:
                    #         self.sendRunDatatoGUI("任务"+str(name)+"将于"+str(jdata["delay"])+"秒后开始",name)
                    #     self.taskthreads[name].startsystem()
                    #     starttaskthread = threading.Thread(target=self.starttask,args=(name, delay ,))
                    #     starttaskthread.startsystem()

                    #     if self.ResultThreadsFlag == 0:
                    #         ResultThreads = threading.Thread(target=self.ResultForwarding,args=())
                    #         ResultThreads.startsystem()
                    #         self.ResultThreadsFlag = 1

                    # elif jdata["key"] == "shutdowntask":
                    #     name = int(jdata["DAPPname"])
                    #     for ele in reversed(self.TASKIPLIST[name]):
                    #         if ele != []:
                    #             if ele[4] in DaspCommon.sonID[name]:
                    #                 sdata = {
                    #                     "key": "shutdowntask",
                    #                     "DAPPname": jdata["DAPPname"]
                    #                 }
                    #                 sjdata = json.dumps(sdata)
                    #                 self.send(ele[4], data=sjdata)
                    #     if DaspCommon.nodeID in self.TASKID[name]:
                    #         self.stop_thread(self.taskthreads[name])
                    #     self.sendRunDatatoGUIflag(0,name)
                    #     self.reset(name)

                    # elif jdata["key"] == "restart":
                    #     try:
                    #         DaspCommon.GUIinfo = jdata["GUIinfo"]
                    #         self.sendRunDatatoGUI("接收任务请求")
                    #     except KeyError:
                    #         print ("非来自GUI的任务请求")
                    #     BaseServer.TaskDict["system"].commTreeFlag[0] = 1
                    #     deleteID = []
                    #     for ele in self.TASKIPLIST[0]:
                    #         if ele != []:
                    #             index = self.adjID.index(ele[4])
                    #             returnID = self.reconnect(ele[0], ele[1], ele[2], ele[3], ele[4], self.AdjOtherSideDirection[index])
                    #             if returnID:
                    #                 deleteID.append(returnID)
                    #     for k in range(len(deleteID)):
                    #         self.deleteadjID(deleteID[k])                        
                    #     self.taskBeginFlag[0] = 1
                    #     self.sendRunDatatoGUIflag(2,0)

                    #     ResultThreads = threading.Thread(target=self.ResultForwarding,args=())
                    #     ResultThreads.startsystem()
                    #     self.ResultThreadsFlag = 1

                    else:
                        conn.send(str.encode(head + "您输入的任务信息有误！"))
            else:
                conn.send(str.encode(head + "暂未提供POST以外的接口"))
            conn.close()

    def startsystem(self):
        """
        启动系统
        """
        BaseServer.TaskDict["system"] = Task("system")
        BaseServer.TaskDict["system"].load()
        BaseServer.TaskDict["system"].commTreeFlag = 1
        sum = 0
        deleteID = []
        for ele in DaspCommon.IPlist:
            if ele != []:
                returnID = self.connect(ele[0], ele[1], ele[2], ele[3], ele[4], "system")
                if returnID:
                    deleteID.append(returnID)
                sum += 1
        for ele in range(deleteID):
            self.deleteadjID(ele)
            self.deleteTaskDictadjID(ele)
        if(sum == 0): BaseServer.TaskDict["system"].treeFlag = 1   #只有一个节点的情况
        while (BaseServer.TaskDict["system"].treeFlag == 0): {time.sleep(0.01)}
        self.sendRunDatatoGUI("通信树建立完成")

        # 启动系统任务
        # sdata = {
        #     "key": "startsystem",
        #     "GUIinfo": DaspCommon.GUIinfo
        # }
        # sjdata = json.dumps(sdata)
        # for ele in reversed(DaspCommon.IPlist):
        #     if ele != []:
        #         if ele[4] in DaspCommon.sonID:
        #             self.send(ele[4], data=sjdata)
        
        # 启动随系统启动的任务
        # self.taskBeginFlag[0] = 1
        # self.sendRunDatatoGUIflag(2,0)

        # 
        self.ResultThreads = threading.Thread(target=self.ResultForwarding,args=())
        self.ResultThreads.start()
        self.ResultThreadsFlag = 1


    def ResultForwarding(self):
        """
        根节点等待所有任务的数据收集结束标志，随后将计算结果转发到GUI界面
        """
        while 1:
            time.sleep(0.01)
            for key in BaseServer.TaskDict:
                if BaseServer.TaskDict[key].dataEndFlag == 1:
                    # time.sleep(1)   # 防止结果显示超前其他节点
                    BaseServer.TaskDict[key].sendDatatoGUI("任务数据收集完毕")
                    info = []
                    content = ""
                    Que = BaseServer.TaskDict[key].resultinfoQue
                    for i in range(len(Que)):
                        if Que[i]["info"]:
                            info.append({})
                            info[-1]["value"] = Que[i]["info"]["value"]
                            info[-1]["ID"] = Que[i]["id"]
                    
                    infojson = json.dumps(info, indent=2)  #格式化输出，更便于查看
                    content =  "Nodes name:{}\nInfo:{}\n\n".format(len(Que), infojson)
                    self.sendEndDatatoGUI(content,BaseServer.TaskDict[key].DAPPname)
                    self.sendFlagtoGUI(0,BaseServer.TaskDict[key].DAPPname)
                    BaseServer.TaskDict[key].taskEndFlag = 0
                    BaseServer.TaskDict[key].dataEndFlag = 0
                    BaseServer.TaskDict[key].resultinfoQue = []
                    BaseServer.TaskDict[key].resultinfo = {}

    def newtask(): 
        pass

    def shutdowntask():
        pass

    def restart():
        pass


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
        head = """HTTP/1.1 200 OK\r\n"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(100)
        print ("CommServer on: {}:{}".format(self.host,str(self.port)))

        while 1:
            conn, addr = sock.accept()
            request = self.recv_length(conn)
            method = request.split(' ')[0]
            if method == 'POST':
                data = request.split('\r\n')[-1]
                try:
                    jdata = json.loads(data)
                except (ValueError, KeyError, TypeError):
                    self.sendRunDatatoGUI("通信JSON数据格式错误")
                else:
                    #建立通信树
                    if jdata["key"] == "connect":
                        self.RespondConnect(conn, head, jdata)

                    elif jdata["key"] == "OK":
                        self.RespondOK(jdata)
                    # startsystem Distribution
                    elif jdata["key"] == "startsystem":
                        if DaspCommon.sonID[0] != 0:
                            for ele in reversed(self.TASKIPLIST[0]):
                                if ele != []:
                                    if ele[4] in DaspCommon.sonID[0]:
                                        sjdata = json.dumps(jdata)
                                        self.send(ele[4], data=sjdata)
                        for i in range(len(self.taskBeginFlag)):
                            self.taskBeginFlag[i] = 1

                    elif jdata["key"] == "newtask":
                        name = int(jdata["DAPPname"])
                        if len(DaspCommon.sonID[name]) != 0:
                            for ele in reversed(self.TASKIPLIST[name]):
                                if ele != []:
                                    if ele[4] in DaspCommon.sonID[name]:
                                        sjdata = json.dumps(jdata)
                                        self.send(ele[4], data=sjdata)
                        # self.createNewTask(name)
                        # self.sendRunDatatoGUI("并行任务"+str(name+1)+"已建立",name + 1)

                    elif jdata["key"] == "starttask":
                        name = int(jdata["DAPPname"])
                        if len(DaspCommon.sonID[name]) != 0:
                            for ele in reversed(self.TASKIPLIST[name]):
                                if ele != []:
                                    if ele[4] in DaspCommon.sonID[name]:
                                        sjdata = json.dumps(jdata)
                                        self.send(ele[4], data=sjdata)
                        self.taskthreads[name].startsystem()
                        self.taskBeginFlag[name] = 1
                        # self.sendRunDatatoGUI("并行任务"+str(name+1)+"开始执行")

                    elif jdata["key"] == "shutdowntask":
                        name = int(jdata["DAPPname"])
                        if len(DaspCommon.sonID[name]) != 0:
                            for ele in reversed(self.TASKIPLIST[name]):
                                if ele != []:
                                    if ele[4] in DaspCommon.sonID[name]:
                                        sjdata = json.dumps(jdata)
                                        self.send(ele[4], data=sjdata)
                        if DaspCommon.nodeID in self.TASKID[name]:
                            self.stop_thread(self.taskthreads[name])
                        self.reset(name)
                    # Data Collection
                    elif jdata["key"] == "data":
                        mdata = jdata["data"]
                        name = jdata["DAPPname"]
                        for i in range(len(DaspCommon.sonID[name])):
                            if DaspCommon.sonID[name][i] == jdata["id"]:
                                self.sonData[name][i] = mdata
                                self.sonFlag[name][i] = 1

                        nflag = 1
                        for ele in self.sonData[name]:
                            if ele == []:
                                nflag = 0
                        if nflag == 1:
                            self.sonFlag2[name] = 1
                    # question
                    elif jdata["key"] == "questionData":
                        name = jdata["DAPPname"]
                        if jdata["type"] == "value":
                            for i in range(len(self.TASKadjID[name])):
                                if(self.TASKadjID[name][i] == jdata["id"]):
                                    self.adjData[name][i] = jdata["data"]
                                    # self.adjDataList[i].append(jdata["data"])

                        elif jdata["type"] == "feedback":
                            for i in range(len(self.TASKadjID[name])):
                                if (self.TASKadjID[name][i] == jdata["id"]):
                                    self.adjFeedback[name][i] = jdata["data"]
                                    # self.adjDataList[i].append(jdata["data"])
                          
                    elif jdata["key"] == "sync":
                        name = jdata["DAPPname"]
                        for i in range(len(self.TASKadjID[name])):
                            if(self.TASKadjID[name][i] == jdata["id"]):
                                self.adjSyncStatus[name][i] = 1

                    elif jdata["key"] == "sync2":
                        name = jdata["DAPPname"]
                        for i in range(len(self.TASKadjID[name])):
                            if(self.TASKadjID[name][i] == jdata["id"]):
                                self.adjSyncStatus2[name][i] = 1

                    elif jdata["key"] == "newNode":
                        if jdata["applydirection"] not in self.adjDirection:
                            self.adjID.append(jdata["id"])
                            self.adjDirection.append(jdata["applydirection"])
                            direction = jdata["applydirection"] - 1
                            self.sonDirection[0].append(jdata["applydirection"])
                            DaspCommon.sonID[0].append(jdata["id"])
                            tempiplist = []
                            tempiplist.append(self.IP)
                            tempiplist.append(self.PORT[direction])
                            tempiplist.append(jdata["host"])
                            tempiplist.append(jdata["port"])
                            tempiplist.append(jdata["id"])
                            for m in range(len(self.TASKIPLIST)):
                                self.TASKIPLIST[m].append(tempiplist)
                                self.TASKadjID[m].append(jdata["id"])
                                self.TASKadjDirection[m].append(jdata["applydirection"])
                                self.adjSyncStatus[m].append([])   #同步标志位  
                                self.adjSyncStatus2[m].append([])    
                                self.adjData[m].append([])
                                self.adjFeedback[m].append([])
                        else:
                            conn.send(str.encode(head + "节点"+str(DaspCommon.nodeID)+"方向"+str(jdata["applydirection"])+"已被占用，请选择其他方向！"))

                    else:
                        conn.send(str.encode(head+"请不要直接访问通信服务器"))
            else:
                conn.send(str.encode(head + "请不要直接访问通信服务器"))
            conn.close()


    def RespondConnect(self, conn, head, jdata):
        name = jdata["DAPPname"]
        # if name != "system":
        #     if len(BaseServer.TaskDict["system"].commTreeFlag) > name:
        #         if BaseServer.TaskDict["system"].commTreeFlag[name] == 0:
        #             self.loadNewTask(name)
        #             self.createNewTask(name)
        #     else:
        #         self.loadNewTask(name)
        #         self.createNewTask(name)
        if BaseServer.TaskDict[name].commTreeFlag == 0:
            BaseServer.TaskDict[name].commTreeFlag = 1
            BaseServer.TaskDict[name].parentID = jdata["id"]
            indext = DaspCommon.adjID.index(jdata["id"])
            BaseServer.TaskDict[name].parentDirection = DaspCommon.adjDirection[indext]
            print ("{}:{} connected to {}:{} ".format(self.host,self.port,jdata["host"],jdata["port"]))
            DaspCommon.GUIinfo = jdata["GUIinfo"]
            data = {
                "key": "connect",
                "host": self.host,
                "port": self.port,
                "id": DaspCommon.nodeID,
                "GUIinfo": DaspCommon.GUIinfo,
                "DAPPname": name
            }
            ndata = json.dumps(data)
            self.sendall_length(conn, head, ndata)
            
            deleteID = []
            for ele in BaseServer.TaskDict[name].TaskIPlist:
                if ele != []:
                    if ele[4] != BaseServer.TaskDict[name].parentID:
                        returnID = self.connect(ele[0], ele[1], ele[2], ele[3], ele[4], name)
                        if returnID:
                            deleteID.append(returnID)

            for ele in range(deleteID):
                self.deleteadjID(ele)
                self.deleteTaskDictadjID(ele)

            #如果是叶子结点
            if len(BaseServer.TaskDict[name].sonID) == 0:
                data = {
                    "key": "OK",
                    "id": DaspCommon.nodeID,
                    "DAPPname": name
                }
                ndata = json.dumps(data)
                self.send(BaseServer.TaskDict[name].parentID, data=ndata)
                for i in range(len(BaseServer.TaskDict[name].CreateTreeSonFlag)):
                    BaseServer.TaskDict[name].CreateTreeSonFlag[i] = 0
        else:
            data = {
                "key": "connected",
                "host": self.host,
                "port": self.port,
                "id": DaspCommon.nodeID,
                "DAPPname": name
            }
            mdata = json.dumps(data)
            self.sendall_length(conn, head, mdata)


    def RespondOK(self, jdata):
        name = jdata["DAPPname"]
        data = {
            "key": "OK",
            "id": DaspCommon.nodeID,
            "DAPPname": name
        }
        ndata = json.dumps(data)
        for i in range(len(BaseServer.TaskDict[name].sonID)):
            if BaseServer.TaskDict[name].sonID[i] == jdata["id"]:
                BaseServer.TaskDict[name].CreateTreeSonFlag[i] = 1

        if all(BaseServer.TaskDict[name].CreateTreeSonFlag):
            if BaseServer.TaskDict[name].parentID != DaspCommon.nodeID:
                self.send(BaseServer.TaskDict[name].parentID, data=ndata)
            else:
                BaseServer.TaskDict[name].treeFlag = 1
                print ("The communication tree has been constructed!")
            for i in range(len(BaseServer.TaskDict[name].CreateTreeSonFlag)):
                BaseServer.TaskDict[name].CreateTreeSonFlag[i] = 0


if __name__ == '__main__':

    DaspCommon.GUIinfo = ["172.23.96.1", 50000]
    DaspCommon.nodeID = "room_2"

    task = Task("debugDAPP")
    task.load()
    BaseServer.TaskDict["debugDAPP"] = task
    BaseServer.TaskDict["debugDAPP"].taskBeginFlag = 1