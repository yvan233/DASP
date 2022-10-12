import codecs
import copy
import importlib
import json
import os
import queue
import socket
import threading
import time
import traceback

from ..pysnooperdb.tracer import Tracer as snoop
from . import DaspCommon,TcpSocket

class Task(DaspCommon):
    """任务类
    
    用于任务具体计算
    
    属性:
        nodeID: 节点ID
        adjID:邻居ID
        leader: 领导节点(根节点)
        childID: 子节点ID
        parentID: 父节点ID,根节点与nodeID相同
        parentDirection 父节点方向,根节点为-1
        childDirection  子节点方向
        taskIPlist: 邻居IP及端口列表
        adjData: 邻居数据
        adjData2: 同步通信函数中另一个邻居变量
        adjDirection: 邻居方向
        adjAsynchData: 异步邻居数据
        adjAlstData: 异步邻居数据(Alst)
        childData: 子节点数据
        rootData: 根节点数据(队列)
        descendantData: 后代节点数据(队列)

        DappName: 任务名称
        GUIinfo: UI界面IP及端口
        taskfunc: 从算法文件中加载的算法程序
        taskAdjDirection: 当前任务邻居方向
        taskDatalist: 当前任务初始数据
        taskAdjID:当前任务邻居ID
        taskID: 当前任务参与的节点ID
        resultinfo: 运行结果数据
        resultinfoQue: 运行结果数据队列
        taskthreads :多线程

        commTreeFlag: 当前节点是否被加进通信树标志
        treeFlag: 通信树建立完成标志
        taskBeginFlag: 任务启动标志
        taskEndFlag: 任务结束标志
        dataEndFlag: 根节点数据收集结束标志
        childDataEndFlag: 子节点数据收集结束标志   
        runFlag: 用于暂停的标志，threading.Event()
            .set()设置为True
            .clear()设置为False
            .wait()  当为True时pass，当为False时阻塞等到到为True时pass
        timeFlag: 用于timesleep

        SyncTurnFlag: 同步函数轮训标志
        SyncTurnFlag2: 同步通信函数轮训标志
        adjSyncStatus: 同步函数邻居状态
        adjSyncStatus2: 同步函数邻居状态2(轮训)    

        DebugMode: 调试模式是否启用标志
        DatabaseInfo: 数据库连接信息
        DBname: 调试数据库名称（默认Daspdb）
        ObservedVariable: 观察变量列表
        """
    def __init__(self, DappName):
        self.DappName = DappName
        self.commTreeFlag = 1
        self.dataEndFlag = 0
        self.loadflag = 0 
        self.leader = None
        self.commThread = None
        self.timesleepFlag = threading.Event()
        self.runFlag = threading.Event()
        self.runFlag.set()
        
    def load(self):
        """
        加载任务运行所需信息,启动run线程,等待任务启动标志
        """
        # 加载topology文件
        ID = []
        AllAdjID = []
        AllDatalist = []
        AllAdjDirection = []
        path = f"{os.getcwd()}/Dapp/{self.DappName}/topology.json"
        # 如果没有就用基本拓扑
        if not os.path.exists(path):
            path = os.getcwd() + "/Dapp/Base/topology.json"
        text = codecs.open(path, 'r', 'utf-8').read()
        js = json.loads(text)
        for ele in js:
            if "ID" in ele:
                ID.append(ele["ID"])
                AllAdjID.append(ele["adjID"])
                AllAdjDirection.append(ele["adjDirection"])
                AllDatalist.append(ele["datalist"])
        self.taskID = ID

        ## 如果当前节点在任务中
        if DaspCommon.nodeID in self.taskID:
            # 加载question文件
            try:
                question = importlib.import_module(f"Dapp.{self.DappName}.question")
                question = importlib.reload(question)
                self.taskfunc = question.taskFunction
            except Exception as e:
                self.sendDatatoGUI("导入出错")
                print(traceback.format_exc())
                self.sendDatatoGUI(traceback.format_exc())

            # 加载debug信息
            debugpath = f"{os.getcwd()}/Dapp/{self.DappName}/debug.json"
            self.load_debuginfo(debugpath)

            order = ID.index(DaspCommon.nodeID)
            selfAdjID = AllAdjID[order]
            selfAdjDirection = AllAdjDirection[order]
            selfDatalist = AllDatalist[order]
            selfIPlist = []

            ### 如果节点已经掉线了，那初始化的任务节点ID不包含这个节点
            for i in range(len(selfAdjID)-1,-1,-1):
                if selfAdjID[i] not in DaspCommon.adjID:
                    selfAdjID.remove(selfAdjID[i])
                    selfAdjDirection.remove(selfAdjDirection[i])
            for i in range(len(selfAdjID)):
                selfIPlist.append([])
                for ele in DaspCommon.IPlist:
                    if ele[4] == selfAdjID[i]:
                        selfIPlist[i] = ele
                        break
            self.taskAdjDirection = selfAdjDirection
            self.taskAdjID = selfAdjID
            self.taskDatalist = selfDatalist
            self.taskIPlist = selfIPlist

            # 初始化各属性
            self.taskBeginFlag = 0
            self.taskEndFlag = 0
            self.dataEndFlag = 0
            self.resultinfo = {}
            self.resultinfoQue = []
            self.childData = []
            self.childDataEndFlag = 0
            self.treeFlag = 0
            self.parentID = DaspCommon.nodeID
            self.parentDirection = -1

            self.childID= []
            self.childDirection = []
            self.adjData = []
            self.adjAsynchData = []
            self.adjAlstData = []
            self.adjData2= []
            self.rootData = queue.Queue() 
            self.descendantData = queue.Queue() 

            self.SyncTurnFlag = 0
            self.SyncTurnFlag2 = 0
            self.adjSyncStatus = []
            self.adjSyncStatus2 = []

            while len(self.adjData) < len(self.taskAdjDirection):
                self.adjData.append([])
                self.adjAsynchData.append(queue.Queue())
                self.adjAlstData.append(queue.Queue())
                self.adjData2.append([])
                self.adjSyncStatus.append(0)
                self.adjSyncStatus2.append(0)

            self.taskthreads = threading.Thread(target=self.run, args=())
            self.taskthreads.start()
        self.loadflag = 1 

    def load_debuginfo(self, debugpath):
        """
        加载调试模式信息
        """
        self.DBname = 'Daspdb'
        if not os.path.exists(debugpath):
            self.DebugMode = False
            self.DatabaseInfo = []
            self.ObservedVariable = []
        else:
            text = codecs.open(debugpath, 'r', 'utf-8').read()
            jdata = json.loads(text)
            self.DebugMode = jdata["DebugMode"]
            self.DatabaseInfo = jdata["DatabaseInfo"]
            self.ObservedVariable = jdata["ObservedVariable"]

    def run(self):
        """
        任务服务器开始运行,等待任务启动标志
        """
        while 1:
            time.sleep(0.01)
            if self.taskBeginFlag == 1:
                try:
                    if self.DebugMode:
                        tablename = "{}_{}".format(self.DappName, self.nodeID)
                        taskfunc = snoop(config = self.DatabaseInfo, db = self.DBname, tablename = tablename, \
                            observelist = self.ObservedVariable)(self.taskfunc)
                        self.sendDatatoGUI("启动调试模式，开始执行")
                    else:
                        taskfunc = self.taskfunc
                        self.sendDatatoGUI("开始执行")
                    print("DAPP:{} start".format(self.DappName))
                    value = taskfunc(self, DaspCommon.nodeID, self.taskAdjDirection, self.taskDatalist)
                    self.resultinfo["value"] = value
                    self.sendDatatoGUI("执行完毕")
                    # time.sleep(1)  # 防止该节点任务结束，其他节点的同步函数出错
                    print ("Calculation complete")
                    self.taskBeginFlag = 0
                    self.taskEndFlag = 1
                    self.data_collec()
                except SystemExit as e:
                    self.sendDatatoGUI("停止执行")
                    print("DAPP:{} stop".format(self.DappName))
                except Exception as e:
                    # self.resultinfo["value"] = "执行出错"
                    self.sendDatatoGUI("执行出错")
                    print(traceback.format_exc())
                    self.sendDatatoGUI(traceback.format_exc())
                finally:
                    self.reset()
                return 0

    def pause(self):
        """
        暂停运行任务服务器
        """
        self.runFlag.clear()     # 设置为False, 阻塞
        self.sendtoGUIbase("开始暂停", "RunData", self.DappName) # 防止阻塞，不用sendDatatoGUI
        print("DAPP:{} pause".format(self.DappName))

    def resume(self):
        """
        恢复运行任务服务器
        """
        self.runFlag.set()    # 设置为True, 停止阻塞
        self.sendtoGUIbase("开始恢复", "RunData", self.DappName) # 防止阻塞，不用sendDatatoGUI
        print("DAPP:{} resume".format(self.DappName))

    def shutdown(self):
        """
        终止运行任务服务器
        """
        try:
            # 停止所有timesleep
            self.timesleepFlag.set()
            self.stop_thread(self.taskthreads)
        # 此时任务线程已退出
        except ValueError:
            self.sendDatatoGUI("停止执行")
            print("DAPP:{} has stopped".format(self.DappName))
        self.reset()

    def data_collec(self):
        """
        收集算法程序运行结果
        """
        # 叶子结点
        self.syncNode() #收集数据前同步一次，防止父节点算法先计算结束，等待子节点超时
        if self.childID == []:
            # 根节点
            if self.parentID == DaspCommon.nodeID:
                sdata = {
                    "id": DaspCommon.nodeID,
                    "info": self.resultinfo
                }
                self.resultinfoQue.append(sdata)
                self.dataEndFlag = 1
                print ("The whole data has been transmitted!")
            else:
                sdata = {
                    "id": DaspCommon.nodeID,
                    "info": self.resultinfo
                }
                self.resultinfoQue.append(sdata)
                data = {
                    "key": "data",
                    "DappName": self.DappName,
                    "id": DaspCommon.nodeID,
                    "data": self.resultinfoQue
                }
                self.send(self.parentID, data)

        # 非叶子结点
        else:
            print ("wait childDataEndFlag")
            while self.childDataEndFlag == 0:
                time.sleep(0.01)
            print ("childDataEndFlag complete")
            sdata = {
                "id": DaspCommon.nodeID,
                "info": self.resultinfo
            }
            self.resultinfoQue.append(sdata)
            for ele in self.childData:
                for ele2 in ele:
                    self.resultinfoQue.append(ele2)
            if self.parentID != DaspCommon.nodeID:
                data = {
                    "key": "data",
                    "DappName": self.DappName,
                    "id": DaspCommon.nodeID,
                    "data": self.resultinfoQue
                }
                self.send(self.parentID, data=data)
                self.resultinfoQue = []
            else:
                self.dataEndFlag = 1
                print ("The whole data has been transmitted!")

    def reset(self):
        """
        重置当前节点
        """
        self.commTreeFlag = 0
    
    def resetadjData(self):
        """
        清空邻居数据
        """
        for i in range(len(self.adjData)):
            self.adjAsynchData[i] = []
            self.adjAlstData[i] = []
            self.adjData[i] = []
            self.adjData2[i] = []

    def send(self,id,data):
        """
        通过TCP的形式将信息发送至指定ID的节点
        """
        self.runFlag.wait()  #系统运行标志
        # 如果之前没建立连接，则建立长连接
        if id not in DaspCommon.adjSocket: 
            try:
                for ele in DaspCommon.IPlist:
                    if ele[4] == id:
                        ip = ele[2]
                        port = ele[3]
                        break
                print (f"connecting to {ip}:{port}")
                remote_ip = socket.gethostbyname(ip)
                DaspCommon.adjSocket[id] = TcpSocket(id,remote_ip,port,self)
            except:
                self.deleteTaskAdjID(id)
                return 0

        # 向相应的套接字发送消息
        try:
            DaspCommon.adjSocket[id].sendall(data)
        except:
            DaspCommon.adjSocket[id].do_fail()
        else:
            DaspCommon.adjSocket[id].do_pass()

    def sendData(self, data):
        """
        通过TCP的形式将信息发送至所有邻居
        """
        for ele in reversed(self.taskIPlist):
            if ele != []:
                self.send(ele[4], data)

    def deleteTaskAdjID(self, id):  
        """
        删除本节点和指定id邻居节点的所有连接
        """
        self.deleteadjID(id)
        for ele in self.taskIPlist:
            if ele != []:
                if ele[4] == id:
                    self.taskIPlist.remove(ele)

        if id in self.taskAdjID:
            index = self.taskAdjID.index(id)      
            del self.taskAdjID[index]
            del self.taskAdjDirection[index]   
            del self.adjSyncStatus[index] 
            del self.adjSyncStatus2[index]     
            del self.adjData[index]
            del self.adjAsynchData[index]
            del self.adjAlstData[index]
            del self.adjData2[index]

        if self.parentID == id:
            self.parentID = DaspCommon.nodeID
            self.parentDirection = -1
        else:
            if id in self.childID:
                index = self.childID.index(id) 
                del self.childID[index]     
                del self.childDirection[index]
                del self.childData[index]

    def startCommPattern(self):
        """
        start comm pattern
        """
        self.commThread = threading.Thread(target=self.commPattern, args=())
        self.commThread.start()

    def floodLeaderElection(self):
        """
        领导人选举
        """
        self.leader = None
        min_id = DaspCommon.nodeID
        for m in range(len(self.taskID)-1):  # 迭代节点数量的轮次数
            _, adjData = self.transmitData(self.taskAdjDirection, [min_id]*len(self.taskAdjDirection))      
            for ele in adjData:
                if ele < min_id:
                    min_id = ele
        self.leader = min_id
        if self.leader == DaspCommon.nodeID:
            self.sendDatatoGUI("This is the leader")

    def commPattern(self):
        """
        communication pattern
        """
        def reset():
            flag = False
            parent = -1
            child = []    
            edgesFlag = [False] * len(adjDirection)
            edges = dict(zip(adjDirection,edgesFlag))
            return flag,parent,child,edges
        def alst(adjDirection,nodeID,flag,parent,child,edges,min_uid,j,data,token):
            """
            Asynchronous Leaderless Spanning Tree algorithm 
            """
            while True:
                if token <= min_uid:
                    if token < min_uid:
                        min_uid = token
                        flag,parent,child,edges = reset()
                    edges[j] = True
                    if data == "end" and j == parent:
                        for ele in child:
                            self.sendAlstData(ele,["end",min_uid]) 
                        break
                    elif data == "join":
                        if j not in child:
                            child.append(j)
                    elif data == "search":
                        if flag == False:
                            flag = True
                            parent = j 
                            for ele in adjDirection:
                                if ele != j:
                                    self.sendAlstData(ele,["search",min_uid])
                    if all(edges.values()):
                        if min_uid == nodeID:
                            leader_state = "leader"
                            for ele in child:
                                self.sendAlstData(ele,["end",min_uid]) 
                            break
                        else:
                            leader_state = "non-leader"  
                            self.sendAlstData(parent,["join",min_uid]) 
                j,(data,token) = self.getAlstData()
            return leader_state,parent,child
        def setTree(parent,child):
            """
            set parent,child,etc.
            """
            self.childDirection = child
            self.parentDirection = parent
            self.childID = [adjID[adjDirection.index(ele)] for ele in child]
            self.parentID = adjID[adjDirection.index(parent)] if parent != -1 else nodeID
            self.childData = [[]]*len(child)
            self.treeFlag = True
        adjDirection = self.taskAdjDirection
        adjID = self.taskAdjID
        nodeID = DaspCommon.nodeID
        flag,parent,child,edges = reset()
        min_uid = nodeID
        flag = True
        step = 1
        for ele in adjDirection:
            self.sendAlstData(ele,["search",min_uid])
        j,(data,token) = self.getAlstData()
        while True:
            if step == 1:
                __,parent,child = alst(adjDirection,nodeID,flag,parent,child,edges,min_uid,j,data,token)
                step = 2
                # generate complete
                setTree(parent,child)
                self.starttask()
            if step == 2:
                break

    def starttask(self):
        # if not self.taskAdjID: #只有一个节点的情况
        #     self.treeFlag = 1   
        if self.parentDirection == -1:
            self.sendDatatoGUI("The communication spanning tree is established.")
            self.resultThread = threading.Thread(target=self.forwardResult, args=())
            self.resultThread.start()
        self.taskBeginFlag = 1
            
                
    def forwardResult(self):
        """
        根节点等待所有任务的数据收集结束标志，随后将计算结果转发到GUI界面
        """
        while 1:
            time.sleep(0.1)
            if self.dataEndFlag == 1:
                self.sendDatatoGUI("任务数据收集完毕")
                info = []
                content = ""
                Que = self.resultinfoQue
                for i in range(len(Que)):
                    if Que[i]["info"]:
                        info.append({})
                        info[-1]["ID"] = Que[i]["id"]
                        info[-1]["value"] = str(Que[i]["info"]["value"])
                
                infojson = json.dumps(info, indent=2)  #格式化输出，更便于查看
                content =  "Nodes number:{}\nInfo:{}\n\n".format(len(Que), infojson)
                self.sendEndDatatoGUI(content)
                self.taskEndFlag = 0
                self.dataEndFlag = 0
                self.resultinfoQue = []
                self.resultinfo = {}
                    
    ##################################
    ###   下面为提供给用户的接口函数   ###
    ##################################

    def forward2childID(self, data):
        """
        将json消息转发给子节点
        """
        if self.childID:
            for ele in reversed(self.taskIPlist):
                if ele:
                    if ele[4] in self.childID:
                        self.send(ele[4], data=data)

    def timesleep(self, timeout = 0):
        self.timesleepFlag.wait(timeout)

    def sendDatatoGUI(self, info):
        """
        通过UDP的形式将运行信息发送至GUI
        """
        self.runFlag.wait()  #系统运行标志
        self.sendtoGUIbase(info, "RunData", self.DappName)

    def sendEndDatatoGUI(self, info):
        """
        通过UDP的形式将结束信息发送至GUI
        """
        self.sendtoGUIbase(info, "EndData",self.DappName)

    def sendDataToID(self, id, data):
        """
        通过TCP的形式将信息发送至指定ID的邻居
        """
        data = {
            "key": "questionData",
            "type": "value",
            "DappName": self.DappName,
            "id": DaspCommon.nodeID,
            "data": data
        }
        for ele in self.taskIPlist:
            if ele != []:
                if ele[4] == id:
                    self.send(ele[4], data)

    def sendDataToRoot(self, data):
        """将消息发送至根节点

        通过邻居不断转发，同时将自己的id和路径上的id加进path
        """

        if self.parentID == DaspCommon.nodeID:
            err = "Error! This node is the root node!"
            self.sendDatatoGUI(err)
            return err
        else:
            data = {
                "key": "RootData",
                "DappName": self.DappName,
                "path": [DaspCommon.nodeID],
                "data": data
            }
            self.send(self.parentID, data)

    def sendDataToDescendant(self, data, path = None):
        """将消息发送至后代节点
        
        根据path将消息回馈到发送的节点，若path为空则进行广播
        path中目标节点在第0位，所以用pop的方法从后取出元素
        """
        data = {
            "key": "DescendantData",
            "DappName": self.DappName,
            "path": copy.deepcopy(path),
            "data": data
        }
        # 如果指定了路径
        if path != None:  
            if path:
                nextnode = data["path"].pop()
                self.send(nextnode, data)
            else:
                err = "Error! Please enter a valid path."
                self.sendDatatoGUI(err)
                return err
        # 否则进行广播
        else:
            for ele in self.childID:
                self.send(ele, data)


    def sendDataToDirection(self, direction, data):
        """
        通过TCP的形式将信息发送至指定方向的邻居
        """
        data = {
            "key": "questionData",
            "type": "value",
            "DappName": self.DappName,
            "id": DaspCommon.nodeID,
            "data": data
        }
        for i in range(len(self.taskAdjID)):
            if self.taskAdjDirection[i] ==  direction:
                for ele in self.taskIPlist:
                    if ele:
                        if ele[4] == self.taskAdjID[i]:
                            self.send(ele[4], data)

    def sendDataToDirection2(self, direction, data):
        """
        通过TCP的形式将信息发送至指定方向的邻居，为了避免与sendDataToDirection在一个轮次中发生冲突
        """
        data = {
            "key": "questionData",
            "type": "value2",
            "DappName": self.DappName,
            "id": DaspCommon.nodeID,
            "data": data
        }
        for i in range(len(self.taskAdjID)):
            if self.taskAdjDirection[i] ==  direction:
                for ele in self.taskIPlist:
                    if ele:
                        if ele[4] == self.taskAdjID[i]:
                            self.send(ele[4], data)

    def sendAsynchData(self, direction, data):
        """
        通过TCP的形式将信息发送至指定方向的邻居
        """
        data = {
            "key": "AsynchData",
            "DappName": self.DappName,
            "id": DaspCommon.nodeID,
            "data": data
        }
        for i in range(len(self.taskAdjID)):
            if self.taskAdjDirection[i] == direction:
                for ele in self.taskIPlist:
                    if ele:
                        if ele[4] == self.taskAdjID[i]:
                            self.send(ele[4], data)

    def sendAlstData(self, direction, data):
        """
        通过TCP的形式将信息发送至指定方向的邻居
        """
        data = {
            "key": "AlstData",
            "DappName": self.DappName,
            "id": DaspCommon.nodeID,
            "data": data
        }
        for i in range(len(self.taskAdjID)):
            if self.taskAdjDirection[i] == direction:
                for ele in self.taskIPlist:
                    if ele:
                        if ele[4] == self.taskAdjID[i]:
                            self.send(ele[4], data)

    def getAsynchData(self):
        """
        获取邻居发过来的数据
        """
        while True:
            for i,que in enumerate(self.adjAsynchData):
                if not que.empty():
                    # 非阻塞性地获取数据
                    data = que.get_nowait()
                    return (self.taskAdjDirection[i],data)
            time.sleep(0.01)

    def getAlstData(self):
        """
        获取邻居发过来的alst数据
        """
        while True:
            for i,que in enumerate(self.adjAlstData):
                if not que.empty():
                    data = que.get_nowait()
                    return (self.taskAdjDirection[i],data)
            time.sleep(0.01)

    def transmitData(self,direclist,datalist):
        """
        同步通信函数，将datalist中的数据分别发到direclist的邻居方向
        """
        self.runFlag.wait()  #系统运行标志
        if (self.SyncTurnFlag2 == 0):
            self.SyncTurnFlag2 = 1 - self.SyncTurnFlag2
            for i in reversed(range(len(direclist))):
                self.sendDataToDirection(direclist[i],datalist[i])
            self.syncNode() 
            ans = copy.deepcopy([self.taskAdjDirection, self.adjData])
            for i in range(len(self.adjData)):
                self.adjData[i] = []
        else:
            self.SyncTurnFlag2 = 1 - self.SyncTurnFlag2
            for i in reversed(range(len(direclist))):
                self.sendDataToDirection2(direclist[i],datalist[i])
            self.syncNode() 
            ans = copy.deepcopy([self.taskAdjDirection, self.adjData2])
            for i in range(len(self.adjData2)):
                self.adjData2[i] = []    
        return ans

    def syncNode(self):
        """
        同步函数，所有节点同步一次
        """
        self.runFlag.wait()  #系统运行标志
        if self.SyncTurnFlag == 0:   
            self.SyncTurnFlag = 1 - self.SyncTurnFlag
            data = {
                "key": "sync",
                "id": DaspCommon.nodeID,
                "DappName": self.DappName
            }  
            self.sendData(data)
            # 全部非空才能继续
            while (not all(self.adjSyncStatus)):   
                time.sleep(0.01)
            for i in range(len(self.adjSyncStatus)):
                self.adjSyncStatus[i] = 0

        elif self.SyncTurnFlag == 1:
            self.SyncTurnFlag = 1 - self.SyncTurnFlag
            data = {
                "key": "sync2",
                "id": DaspCommon.nodeID,
                "DappName": self.DappName
            }
            self.sendData(data)
            while (not all(self.adjSyncStatus2)):   
                time.sleep(0.01)
            for i in range(len(self.adjSyncStatus2)):
                self.adjSyncStatus2[i] = 0


if __name__ == '__main__':

    DaspCommon.GUIinfo = ["172.23.96.1", 50000]
    DaspCommon.nodeID = "room_1"

    task = Task("debugDAPP")
    task.load()

    task2 = Task("debugDAPP")
    task2.load()

    task.taskBeginFlag = 1
    task2.taskBeginFlag = 1

    # TaskDict = {}
    # task = Task(nodeID, 8)
    # TaskDict[0] = task
    # task2 = Task(nodeID, 1)
    # TaskDict.update({1:task2})
    # print (task.GUIinfo,TaskDict[1].GUIinfo)
