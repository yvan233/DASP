import json
import socket
import sys
import time
import threading
import traceback
import importlib
import os
import codecs
sys.path.insert(1,".")  # 把上一级目录加入搜索路径

class Task():
    """任务类
    
    用于任务具体计算
    
    属性:
        nodeID: 节点ID
        adjID：邻居ID
        sonID: 子节点ID
        parentID：父节点ID,根节点与nodeID相同
        parentDirection 父节点方向,根节点为0
        sonDirection  子节点方向
        TaskIPlist: 邻居IP及端口列表
        adjData: 邻居数据
        adjData_another: 同步通信函数中另一个邻居数据变量
        sonData: 子节点数据

        tasknum: 任务编号
        taskname: 任务名称
        GUIinfo: UI界面IP及端口
        taskfunc: 从算法文件中加载的算法程序
        TaskadjDirection: 当前任务邻居方向
        TaskDatalist: 当前任务初始数据
        TaskadjID:当前任务邻居ID
        TaskID: 当前任务参与的节点ID
        resultinfo: 运行结果数据
        resultinfoQue: 运行结果数据队列
        taskthreads :多线程

        commTreeFlag: 通信树建立标志
        treeFlag: 生成树标志
        taskBeginFlag: 任务启动标志
        taskEndFlag: 任务结束标志
        dataEndFlag: 根节点数据收集结束标志
        CreateTreeSonFlag: 创建通信树子节点标志
        SonDataEndFlag: 子节点数据收集结束标志   

        SyncTurnFlag: 同步函数轮训标志
        SyncTurnFlag2: 同步通信函数轮训标志
        adjSyncStatus: 同步函数邻居状态
        adjSyncStatus2: 同步函数邻居状态2(轮训)     
        """
    parentID = [0]
    sonID = [[]]
    parentDirection = [0]
    sonDirection = [[]]
    CreateTreeSonFlag = [[]]
    commTreeFlag = [0]
    treeFlag = [0]

    resultinfoQue = []
    threads = []
    taskthreads = []

    dataEndFlag = []
    taskEndFlag = []
    taskBeginFlag = []

    adjDataList = []

    waitflag = 0

    # parallel
    taskcounter = 1
    sonData = []
    sonDataEndFlag = []
    SyncTurnFlag2 = []
    SyncTurnFlag = []
    adjData = []
    adjData_another = []
    adjSyncStatus = []
    adjSyncFlag = []
    adjSyncStatus2 = []
    adjSyncFlag2 = []

    TaskID = []
    TaskDatalist = []
    TaskadjDirection = []
    TASKadjID = []
    
    ### 类变量，直接通过Task.维护
    GUIinfo = ["localhost",0]
    adjID = []
    TaskIPlist = []

    def __init__(self, nodeID, tasknum):
        self.nodeID = nodeID
        self.tasknum = tasknum
        self.taskname = "default"

        
    def load(self):
        """
        加载任务运行所需信息
        """
        # 加载question文件
        question = importlib.import_module("DASP.task_info.question"+str(self.tasknum))
        question = importlib.reload(question)
        self.taskfunc = question.taskFunction

        # 加载topology文件
        ID = []
        selfadjID = []
        selfdatalist = []
        selfadjDirection = []
        path = os.getcwd() + "/DASP/task/topology"+str(self.tasknum)+".txt"
        path = path.replace('\\', '/') 
        text = codecs.open(path, 'r', 'utf-8').read()
        js = json.loads(text)
        for ele in js:
            if "ID" in ele:
                ID.append(ele["ID"])
                selfadjID.append(ele["adjID"])
                selfadjDirection.append(ele["adjDirection"])
                selfdatalist.append(ele["datalist"])
        self.TaskID = ID

        ## 如果当前节点在任务中
        if self.nodeID in self.TaskID:
            order = ID.index(self.nodeID)
            selfAdjID = selfadjID[order]
            selfAdjDirection = selfadjDirection[order]
            selfDatalist = selfdatalist[order]
            ### 如果节点已经掉线了，那初始化的任务节点ID不包含这个节点
            for i in range(len(selfAdjID)-1,-1,-1):
                if selfAdjID[i] not in self.adjID:
                    selfAdjID.remove(selfAdjID[i])
                    selfAdjDirection.remove(selfAdjDirection[i])
            self.TaskadjDirection = selfAdjDirection
            self.TASKadjID = selfAdjID
            self.TaskDatalist = selfDatalist

        # 初始化各属性
        self.taskBeginFlag = 0
        self.taskEndFlag = 0
        self.dataEndFlag = 0
        self.resultinfo = {}
        self.resultinfoQue = []
        self.sonData = []
        self.sonDataEndFlag = 0
        self.commTreeFlag = 0
        self.treeFlag = 0
        self.parentID = self.nodeID
        self.parentDirection = 0

        self.sonID= []
        self.sonDirection = []
        self.CreateTreeSonFlag = []
        self.adjData = []
        self.adjData_another= []

        self.SyncTurnFlag = 0
        self.SyncTurnFlag2 = 0
        self.adjSyncStatus = []
        self.adjSyncStatus2 = []

        while len(self.adjData) < len(self.TaskadjDirection):
            self.adjData.append([])
            self.adjData_another.append([])
            self.adjSyncStatus.append(0)
            self.adjSyncStatus2.append(0)

        # 给其他节点开线程的时间，防止换数据的时候其他节点线程还没开
        # time.sleep(1)
        if self.nodeID in self.TaskID:
            self.taskthreads = threading.Thread(target=self.run, args=())
        else:
            self.taskthreads = threading.Thread(target=self.dataFunction, args=())

    def run(self):
        """
        任务服务器开始运行
        """
        try:
            while 1:
                time.sleep(0.01)
                if self.taskBeginFlag == 1:
                    try:
                        self.sendtoGUI("任务"+ str(self.tasknum) +" 开始执行")
                        value = self.taskfunc(self, self.nodeID, self.TaskadjDirection, self.TaskDatalist)
                        self.resultinfo["value"] = value
                        self.sendtoGUI("任务"+ str(self.tasknum) +" 执行完毕")
                        # time.sleep(1)  # 防止该节点任务结束，其他节点的同步函数出错
                        print ("value:", value)
                    except Exception as e:
                        self.resultinfo["value"] = ""
                        self.sendtoGUI("任务"+ str(self.tasknum) +" 执行出错")
                        self.sendtoGUI(traceback.format_exc())
                    self.taskEndFlag = 1

                    self.syncNode() #收集数据前同步一次，防止父节点算法先计算结束，等待子节点超时
                    self.data_collec()
                    # print("resultinfo：", self.resultinfo)
                    self.taskBeginFlag = 0 
                    self.reset()
                    self.resetadjData()
                    return 0
        except SystemExit:
            self.sendtoGUI("任务"+ str(self.tasknum) +" 停止执行")

    def data_collec(self):
        """
        收集算法程序运行结果
        """
        # 叶子结点
        if self.sonID == []:
            # 根节点
            if self.parentID == self.nodeID:
                sdata = {
                    "id": self.nodeID,
                    "info": self.resultinfo
                }
                self.resultinfoQue.append(sdata)
                self.dataEndFlag = 1
                print ("The whole data has been transmitted!")
            else:
                sdata = {
                    "id": self.nodeID,
                    "info": self.resultinfo
                }
                self.resultinfoQue.append(sdata)
                data = {
                    "key": "data",
                    "tasknum": self.tasknum,
                    "id": self.nodeID,
                    "data": self.resultinfoQue
                }
                ndata = json.dumps(data)
                self.send(self.parentID, ndata)

        # 非叶子结点
        else:
            print ("wait sonDataEndFlag")
            ii = 0
            # 父节点结束程序后等待子节点10s
            while self.sonDataEndFlag == 0 and ii < 100:
                time.sleep(0.1)
                ii = ii + 1
            if ii == 100:
                print ("timeout!")
                sdata = {
                    "id": self.nodeID,
                    "info": {"value" : "Child node data loss"}
                }
                # deleteID = []
                # for k in range(len(self.sonData)):
                #     if not self.sonData[k]:
                #         deleteID.append(self.sonID[k])
                # for k in range(len(deleteID)):   
                #     self.sendtoGUI("邻居节点"+deleteID[k]+"连接不上")
                #     print ("与邻居节点"+deleteID[k]+"连接失败")
                #     self.deleteadjID(deleteID[k])  
                #     self.sendtoGUI("已删除和邻居节点"+(deleteID[k])+"的连接") 
            else:
                print ("sonDataEndFlag complete")
                sdata = {
                    "id": self.nodeID,
                    "info": self.resultinfo
                }
            self.resultinfoQue.append(sdata)
            for ele in self.sonData:
                for ele2 in ele:
                    self.resultinfoQue.append(ele2)
            if self.parentID != self.nodeID:
                data = {
                    "key": "data",
                    "tasknum": self.tasknum,
                    "id": self.nodeID,
                    "data": self.resultinfoQue
                }
                ndata = json.dumps(data)
                self.send(self.parentID, data=ndata)
                self.resultinfoQue = []
            else:
                self.dataEndFlag = 1
                print ("The whole data has been transmitted!")


    def reset(self):
        """
        清空运行数据
        """
        self.taskBeginFlag = 0
        self.treeFlag = 0
        self.parentID = self.nodeID
        self.parentDirection = 0
        self.sonID = []
        self.sonDirection = []
        self.CreateTreeSonFlag = []
        self.resultinfoQue = []
        self.sonDataEndFlag = 0
        self.sonData = []
    
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
        for ele in self.TaskIPlist:
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
                        self.sendUDP("邻居节点"+id+"连接不上")
                        print ("与邻居节点"+id+"连接失败")
                        self.deleteadjID(id)
                        self.sendUDP("已删除和邻居节点"+(id)+"的连接") 
                    break

    def sendtoGUI(self, info):
        """
        通过UDP的形式将信息发送至GUI
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            addr = (self.GUIinfo[0], self.GUIinfo[1])
            data = {
                "key": "runData",
                "id": self.nodeID,
                "tasknum":self.tasknum,
                "info": info
            }
            sock.sendto(json.dumps(data).encode('utf-8'), addr)
            sock.close()
        except Exception as e:
            print (info + "发送失败")


    def syncNode(self):
        """
        所有节点同步一次
        """
        num = tasknum
        if self.SyncTurnFlag[num] == 0:   
            self.SyncTurnFlag[num] = 1 - self.SyncTurnFlag[num]
            data = {
                "key": "sync",
                "id": self.nodeID,
                "tasknum": tasknum
            }
            ndata = json.dumps(data)      
            for ele in reversed(self.TASKIPLIST[num]):
                if ele != []:
                    self.send(ele[4], ndata)
            while self.adjSyncFlag[num] == 0:
                nflag1 = 1
                for ele in self.adjSyncStatus[num]:
                    if ele == 0:
                        nflag1 = 0
                if nflag1 == 1:
                    self.adjSyncFlag[num] = 1
                time.sleep(0.01)
            self.adjSyncFlag[num] = 0
            for i in range(len(self.adjSyncStatus[num])):
                self.adjSyncStatus[num][i] = 0
        elif self.SyncTurnFlag[num] == 1:
            self.SyncTurnFlag[num] = 1 - self.SyncTurnFlag[num]
            data = {
                "key": "sync2",
                "id": self.nodeID,
                "tasknum": tasknum
            }
            ndata = json.dumps(data)
            for ele in reversed(self.TASKIPLIST[num]):
                if ele != []:
                    self.send(ele[4], ndata)
            while self.adjSyncFlag2[num] == 0:
                nflag2 = 1
                for ele in self.adjSyncStatus2[num]:
                    if ele == 0:
                        nflag2 = 0
                if nflag2 == 1:
                    self.adjSyncFlag2[num] = 1
                time.sleep(0.01)
            self.adjSyncFlag2[num] = 0
            for i in range(len(self.adjSyncStatus2[num])):
                self.adjSyncStatus2[num][i] = 0
        return 0

class DataFunction():
    """
    外部交互服务器，用于节点和外部交互
    """
    host = "locolhost"
    port = 10000

    def __init__(self,host,port):
        self.host = host
        self.port = port


    def dataFunction(self, tasknum = 0):
        try:
            num = self.tasknum
            self.taskEndFlag = 1
            time.sleep(1)
            if self.sonID == []:
                if self.parentID == self.nodeID:
                    sdata = {
                        "id": self.nodeID,
                        "info": self.resultinfo
                    }
                    self.resultinfoQue.append(sdata)
                    self.dataEndFlag = 1
                    print ("The whole data has been transmitted!")
                else:
                    sdata = {
                        "id": self.nodeID,
                        "info": self.resultinfo
                    }
                    self.resultinfoQue.append(sdata)
                    data = {
                        "key": "data",
                        "tasknum": self.tasknum,
                        "id": self.nodeID,
                        "data": self.resultinfoQue
                    }
                    ndata = json.dumps(data)
                    self.send(self.parentID, ndata)
                    self.resultinfoQue = []

            else:
                ii = 0
                while self.sonDataEndFlag == 0 and ii < 1000:
                    time.sleep(0.01)
                    ii = ii + 1
                if ii == 1000:
                    print ("timeout!")
                    deleteID = []
                    for k in range(len(self.sonData)):
                        if not self.sonData[k]:
                            deleteID.append(self.sonID[k])
                    for k in range(len(deleteID)):   
                        self.deleteadjID(deleteID[k])  

                sdata = {
                    "id": self.nodeID,
                    "info": self.resultinfo
                }
                self.resultinfoQue.append(sdata)
                for ele in self.sonData:
                    for ele2 in ele:
                        self.resultinfoQue.append(ele2)
                if self.parentID != self.nodeID:
                    data = {
                        "key": "data",
                        "tasknum": self.tasknum,
                        "id": self.nodeID,
                        "data": self.resultinfoQue
                    }
                    ndata = json.dumps(data)
                    self.send(self.parentID, data=ndata)
                    self.resultinfoQue = []
                else:
                    self.dataEndFlag = 1
                    print ("The whole data has been transmitted!")
            self.reset(num)
            self.resetadjData(num)
        except SystemExit:
            self.sendtoGUI("任务"+ str(self.tasknum) +" 停止执行",self.tasknum)


if __name__ == '__main__':
    path = os.getcwd() + "/DASP/task_info/topology"+str(1)+".txt"
    path = path.replace('\\', '/')
    # path = "/home/pi/zhongdy/DASP/task/topology"+str(num)+".txt"
    text = codecs.open(path, 'r', 'utf-8').read()
    js = json.loads(text)
    print (js)

    # nodeID = "room1"
    # Task.GUIinfo = ["localhost", 10000]
    # TaskDict = {}
    # task = Task(nodeID, 0)
    # TaskDict[0] = task

    # # TaskDict[0].load()

    # task2 = Task(nodeID, 1)
    # TaskDict.update({1:task2})

    # print (task.GUIinfo,TaskDict[1].GUIinfo)