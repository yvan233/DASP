import json
import socket
import time
import threading
import traceback
import importlib
import os
import codecs
import copy
import queue
# import sys
# sys.path.insert(1,".")  # 把上一级目录加入搜索路径
# from DASP.module import DaspCommon
from . import DaspCommon
from ..pysnooperdb.tracer import Tracer as snoop
class Task(DaspCommon):
    """任务类
    
    用于任务具体计算
    
    属性:
        nodeID: 节点ID
        adjID：邻居ID
        sonID: 子节点ID
        parentID: 父节点ID,根节点与nodeID相同
        parentDirection 父节点方向,根节点为0
        sonDirection  子节点方向
        TaskIPlist: 邻居IP及端口列表
        adjData: 邻居数据
        adjData_another: 同步通信函数中另一个邻居数据变量
        sonData: 子节点数据
        rootData: 根节点数据(队列)
        descendantData: 后代节点数据(队列)

        DAPPname: 任务名称
        GUIinfo: UI界面IP及端口
        taskfunc: 从算法文件中加载的算法程序
        TaskadjDirection: 当前任务邻居方向
        TaskDatalist: 当前任务初始数据
        TaskadjID:当前任务邻居ID
        TaskID: 当前任务参与的节点ID
        resultinfo: 运行结果数据
        resultinfoQue: 运行结果数据队列
        taskthreads :多线程

        commTreeFlag: 当前节点是否被加进通信树标志
        treeFlag: 通信树建立完成标志
        taskBeginFlag: 任务启动标志
        taskEndFlag: 任务结束标志
        dataEndFlag: 根节点数据收集结束标志
        CreateTreeSonFlag: 创建通信树子节点标志
        SonDataEndFlag: 子节点数据收集结束标志   
        runFlag: 用于暂停的标志，threading.Event()
            .set()设置为True
            .clear()设置为False
            .wait()  当为True时pass，当为False时阻塞等到到为True时pass

        SyncTurnFlag: 同步函数轮训标志
        SyncTurnFlag2: 同步通信函数轮训标志
        adjSyncStatus: 同步函数邻居状态
        adjSyncStatus2: 同步函数邻居状态2(轮训)    

        DebugMode: 调试模式是否启用标志
        DatabaseInfo: 数据库连接信息
        DBname: 调试数据库名称（默认Daspdb）
        ObservedVariable: 观察变量列表
        """
    def __init__(self, DAPPname):
        self.DAPPname = DAPPname
        self.commTreeFlag = 1
        self.runFlag = threading.Event()
        self.runFlag.set()
        
    def load(self):
        """
        加载任务运行所需信息,启动run线程,等待任务启动标志
        """
        # 加载question文件
        try:
            question = importlib.import_module("DASP.task_info.{}.question".format(self.DAPPname))
            question = importlib.reload(question)
            self.taskfunc = question.taskFunction
        except Exception as e:
            self.sendDatatoGUI("导入出错")
            print(traceback.format_exc())
            self.sendDatatoGUI(traceback.format_exc())

        # 加载topology文件
        ID = []
        AllAdjID = []
        AllDatalist = []
        AllAdjDirection = []
        path = os.getcwd() + "/DASP/task_info/{}/topology.txt".format(self.DAPPname)
        path = path.replace('\\', '/') 
        text = codecs.open(path, 'r', 'utf-8').read()
        js = json.loads(text)
        for ele in js:
            if "ID" in ele:
                ID.append(ele["ID"])
                AllAdjID.append(ele["adjID"])
                AllAdjDirection.append(ele["adjDirection"])
                AllDatalist.append(ele["datalist"])
        self.TaskID = ID

        ## 如果当前节点在任务中
        if DaspCommon.nodeID in self.TaskID:
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
            self.TaskadjDirection = selfAdjDirection
            self.TaskadjID = selfAdjID
            self.TaskDatalist = selfDatalist
            self.TaskIPlist = selfIPlist

        # 初始化各属性
        self.taskBeginFlag = 0
        self.taskEndFlag = 0
        self.dataEndFlag = 0
        self.resultinfo = {}
        self.resultinfoQue = []
        self.sonData = []
        self.sonDataEndFlag = 0
        self.treeFlag = 0
        self.parentID = DaspCommon.nodeID
        self.parentDirection = 0

        self.sonID= []
        self.sonDirection = []
        self.CreateTreeSonFlag = []
        self.adjData = []
        self.adjData_another= []
        self.rootData = queue.Queue() 
        self.descendantData = queue.Queue() 

        self.SyncTurnFlag = 0
        self.SyncTurnFlag2 = 0
        self.adjSyncStatus = []
        self.adjSyncStatus2 = []

        while len(self.adjData) < len(self.TaskadjDirection):
            self.adjData.append([])
            self.adjData_another.append([])
            self.adjSyncStatus.append(0)
            self.adjSyncStatus2.append(0)

        self.taskthreads = threading.Thread(target=self.run, args=())
        self.taskthreads.start()

    def load_debuginfo(self, DebugMode = False, DatabaseInfo = [], DBname = 'Daspdb', ObservedVariable = []):
        """
        加载调试模式信息
        """
        self.DebugMode = DebugMode
        self.DatabaseInfo = DatabaseInfo
        self.DBname = DBname
        self.ObservedVariable = ObservedVariable

    def run(self):
        """
        任务服务器开始运行,等待任务启动标志
        """
        try:
            while 1:
                time.sleep(0.01)
                if self.taskBeginFlag == 1:
                    if DaspCommon.nodeID in self.TaskID: #如果在任务列表中
                        try:
                            if self.DebugMode:
                                tablename = "{}_{}".format(self.DAPPname, self.nodeID)
                                taskfunc = snoop(config = self.DatabaseInfo, db = self.DBname, tablename = tablename, \
                                    observelist = self.ObservedVariable)(self.taskfunc)
                                self.sendDatatoGUI("启动调试模式，开始执行")
                            else:
                                taskfunc = self.taskfunc
                                self.sendDatatoGUI("开始执行")
                            print("DAPP:{} start".format(self.DAPPname))
                            value = taskfunc(self, DaspCommon.nodeID, self.TaskadjDirection, self.TaskDatalist)
                            self.resultinfo["value"] = value
                            self.sendDatatoGUI("执行完毕")
                            # time.sleep(1)  # 防止该节点任务结束，其他节点的同步函数出错
                            print ("Calculation complete")
                        except Exception as e:
                            self.resultinfo["value"] = ""
                            self.sendDatatoGUI("执行出错")
                            print(traceback.format_exc())
                            self.sendDatatoGUI(traceback.format_exc())
                    else:
                        self.resultinfo["value"] = ""
                    self.taskBeginFlag = 0
                    self.taskEndFlag = 1
                    self.data_collec()
                    # print("resultinfo：", self.resultinfo)
                    self.reset()
                    return 0
        except SystemExit:
            self.sendDatatoGUI("停止执行")
            print("DAPP:{} stop".format(self.DAPPname))

    def pause(self):
        """
        暂停运行任务服务器
        """
        self.runFlag.clear()     # 设置为False, 阻塞
        self.sendtoGUIbase("开始暂停", "RunData", self.DAPPname) # 防止阻塞，不用sendDatatoGUI
        print("DAPP:{} pause".format(self.DAPPname))

    def resume(self):
        """
        恢复运行任务服务器
        """
        self.runFlag.set()    # 设置为True, 停止阻塞
        self.sendtoGUIbase("开始恢复", "RunData", self.DAPPname) # 防止阻塞，不用sendDatatoGUI
        print("DAPP:{} resume".format(self.DAPPname))

    def shutdown(self):
        """
        终止运行任务服务器
        """
        try:
            self.stop_thread(self.taskthreads)
        # 此时任务线程已退出
        except ValueError:
            # self.sendDatatoGUI("已执行完毕")
            print("DAPP:{} has stopped".format(self.DAPPname))
        self.reset()

    def data_collec(self):
        """
        收集算法程序运行结果
        """
        # 叶子结点
        self.syncNode() #收集数据前同步一次，防止父节点算法先计算结束，等待子节点超时
        if self.sonID == []:
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
                    "DAPPname": self.DAPPname,
                    "id": DaspCommon.nodeID,
                    "data": self.resultinfoQue
                }
                self.send(self.parentID, data)

        # 非叶子结点
        else:
            print ("wait sonDataEndFlag")
            while self.sonDataEndFlag == 0:
                time.sleep(0.01)
            print ("sonDataEndFlag complete")
            sdata = {
                "id": DaspCommon.nodeID,
                "info": self.resultinfo
            }
            self.resultinfoQue.append(sdata)
            for ele in self.sonData:
                for ele2 in ele:
                    self.resultinfoQue.append(ele2)
            if self.parentID != DaspCommon.nodeID:
                data = {
                    "key": "data",
                    "DAPPname": self.DAPPname,
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
            self.adjData[i] = []
            self.adjData_another[i] = []

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
                self.deleteTaskadjID(id)
                self.sendDatatoGUI("与邻居节点{0}连接失败".format(id)) 
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
            try:
                print ("reconnecting to {}:{}, times:{}".format(host,str(port),times))
                self.sendDatatoGUI("与邻居节点{}连接失败，第{}次重连中...".format(id,times))
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
        self.sendDatatoGUI("与邻居节点{0}连接失败，已删除和{0}的连接".format(id)) 
        return id

    def sendData(self, data):
        """
        通过TCP的形式将信息发送至所有邻居
        """
        for ele in reversed(self.TaskIPlist):
            if ele != []:
                self.send(ele[4], data)

    def deleteTaskadjID(self, id):  
        """
        删除本节点和指定id邻居节点的所有连接
        """
        for ele in self.TaskIPlist:
            if ele != []:
                if ele[4] == id:
                    self.TaskIPlist.remove(ele)

        if id in self.TaskadjID:
            index = self.TaskadjID.index(id)      
            del self.TaskadjID[index]
            del self.TaskadjDirection[index]   
            del self.adjSyncStatus[index] 
            del self.adjSyncStatus2[index]     
            del self.adjData[index]
            del self.adjData_another[index]

        if self.parentID == id:
            self.parentID = DaspCommon.nodeID
            self.parentDirection = 0
        else:
            if id in self.sonID:
                index = self.sonID.index(id) 
                del self.sonID[index]     
                del self.sonDirection[index]
                del self.sonData[index]

 
    ##################################
    ###   下面为提供给用户的接口函数   ###
    ##################################

    def sendDatatoGUI(self, info):
        """
        通过UDP的形式将运行信息发送至GUI
        """
        self.runFlag.wait()  #系统运行标志
        self.sendtoGUIbase(info, "RunData", self.DAPPname)

    def sendDataToID(self, id, data):
        """
        通过TCP的形式将信息发送至指定ID的邻居
        """
        data = {
            "key": "questionData",
            "type": "value",
            "DAPPname": self.DAPPname,
            "id": DaspCommon.nodeID,
            "data": data
        }
        for ele in self.TaskIPlist:
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
                "DAPPname": self.DAPPname,
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
            "DAPPname": self.DAPPname,
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
            for ele in self.sonID:
                self.send(ele, data)


    def sendDataToDirection(self, direction, data):
        """
        通过TCP的形式将信息发送至指定方向的邻居
        """
        data = {
            "key": "questionData",
            "type": "value",
            "DAPPname": self.DAPPname,
            "id": DaspCommon.nodeID,
            "data": data
        }
        for i in range(len(self.TaskadjID)):
            if self.TaskadjDirection[i] ==  direction:
                for ele in self.TaskIPlist:
                    if ele != []:
                        if ele[4] == self.TaskadjID[i]:
                            self.send(ele[4], data)

    def sendDataToDirectionAnother(self, direction, data):
        """
        通过TCP的形式将信息发送至指定方向的邻居，为了避免与sendDataToDirection在一个轮次中发生冲突
        """
        data = {
            "key": "questionData",
            "type": "value2",
            "DAPPname": self.DAPPname,
            "id": DaspCommon.nodeID,
            "data": data
        }
        for i in range(len(self.TaskadjID)):
            if self.TaskadjDirection[i] ==  direction:
                for ele in self.TaskIPlist:
                    if ele != []:
                        if ele[4] == self.TaskadjID[i]:
                            self.send(ele[4], data)
                    
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
            ans = copy.deepcopy([self.TaskadjDirection, self.adjData])
            for i in range(len(self.adjData)):
                self.adjData[i] = []
        else:
            self.SyncTurnFlag2 = 1 - self.SyncTurnFlag2
            for i in reversed(range(len(direclist))):
                self.sendDataToDirectionAnother(direclist[i],datalist[i])
            self.syncNode() 
            ans = copy.deepcopy([self.TaskadjDirection, self.adjData_another])
            for i in range(len(self.adjData_another)):
                self.adjData_another[i] = []    
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
                "DAPPname": self.DAPPname
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
                "DAPPname": self.DAPPname
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