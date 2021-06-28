import json
import socket
import sys
import time
import threading
import traceback
import importlib
import os
import codecs
import copy
sys.path.insert(1,".")  # 把上一级目录加入搜索路径
from DASP.module import DaspFuncMixin

class Task(DaspFuncMixin):
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

    ### 类变量，直接通过Task.维护
    GUIinfo = ["localhost",0]
    adjID = []
    adjDirection = []
    IPlist = []

    def __init__(self, nodeID, tasknum, taskname = "default"):
        self.nodeID = nodeID
        self.tasknum = tasknum
        self.taskname = taskname

        
    def load(self):
        """
        加载任务运行所需信息
        """
        # 加载question文件
        question = importlib.import_module("DASP.task_info.{}.question".format(str(self.tasknum)))
        question = importlib.reload(question)
        self.taskfunc = question.taskFunction

        # 加载topology文件
        ID = []
        AllAdjID = []
        AllDatalist = []
        AllAdjDirection = []
        path = os.getcwd() + "/DASP/task_info/{}/topology.txt".format(str(self.tasknum))
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
        if self.nodeID in self.TaskID:
            order = ID.index(self.nodeID)
            selfAdjID = AllAdjID[order]
            selfAdjDirection = AllAdjDirection[order]
            selfDatalist = AllDatalist[order]
            selfIPlist = []

            ### 如果节点已经掉线了，那初始化的任务节点ID不包含这个节点
            for i in range(len(selfAdjID)-1,-1,-1):
                if selfAdjID[i] not in Task.adjID:
                    selfAdjID.remove(selfAdjID[i])
                    selfAdjDirection.remove(selfAdjDirection[i])
            for i in range(len(selfAdjID)):
                selfIPlist.append([])
                for ele in Task.IPlist:
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

        self.taskthreads = threading.Thread(target=self.run, args=())

    def run(self):
        """
        任务服务器开始运行
        """
        try:
            while 1:
                time.sleep(0.01)
                if self.taskBeginFlag == 1:
                    if self.nodeID in self.TaskID: #如果在任务列表中
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
                            print(traceback.format_exc())
                            self.sendtoGUI(traceback.format_exc())
                    else:
                        self.resultinfo["value"] = ""
                    self.taskBeginFlag = 0 
                    self.taskEndFlag = 1
                    self.data_collec()
                    # print("resultinfo：", self.resultinfo)
                    
                    self.reset()
                    self.resetadjData()
                    return 0
        except SystemExit:
            self.sendtoGUI("任务"+ str(self.tasknum) +" 停止执行")

    def data_collec(self):
        """
        收集算法程序运行结果
        """
        self.syncNode() #收集数据前同步一次，防止父节点算法先计算结束，等待子节点超时
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
                time.sleep(0.01)
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
                        print ("与邻居节点"+id+"连接失败")
                        self.sendtoGUI("与邻居节点"+id+"连接失败")
                        self.deleteadjID(id)
                    break

    def sendData(self, data):
        """
        通过TCP的形式将信息发送至所有邻居
        """
        for ele in reversed(self.TaskIPlist):
            if ele != []:
                self.send(ele[4], data)

    def sendtoGUI(self, info):
        """
        通过UDP的形式将信息发送至GUI
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            addr = (Task.GUIinfo[0], Task.GUIinfo[1])
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

    def sendDataToID(self, id, data):
        """
        通过TCP的形式将信息发送至指定ID的邻居
        """
        data = {
            "key": "questionData",
            "type": "value",
            "tasknum": self.tasknum,
            "id": self.nodeID,
            "data": data
        }
        ndata = json.dumps(data)
        for ele in self.TaskIPlist[0]:
            if ele != []:
                if ele[4] == id:
                    self.send(ele[4], ndata)

    def sendDataToDirection(self, direction, data):
        """
        通过TCP的形式将信息发送至指定方向的邻居
        """
        data = {
            "key": "questionData",
            "type": "value",
            "tasknum": self.tasknum,
            "id": self.nodeID,
            "data": data
        }
        ndata = json.dumps(data)
        for i in range(len(self.TaskadjID)):
            if self.TaskadjDirection[i] ==  direction:
                for ele in self.TaskIPlist[0]:
                    if ele != []:
                        if ele[4] == self.TaskadjID[i]:
                            self.send(ele[4], ndata)

    def sendDataToDirectionAnother(self, direction, data):
        """
        通过TCP的形式将信息发送至指定方向的邻居，为了避免与sendDataToDirection在一个轮次中发生冲突
        """
        data = {
            "key": "questionData",
            "type": "value2",
            "tasknum": self.tasknum,
            "id": self.nodeID,
            "data": data
        }
        ndata = json.dumps(data)
        for i in range(len(self.TaskadjID)):
            if self.TaskadjDirection[i] ==  direction:
                for ele in self.TaskIPlist[0]:
                    if ele != []:
                        if ele[4] == self.TaskadjID[i]:
                            self.send(ele[4], ndata)

    def deleteadjID(self, id):  
        """
        删除本节点和指定id邻居节点的所有连接
        """
        if id in Task.adjID:
            index = Task.adjID.index(id)      
            del Task.adjID[index]
            del Task.adjDirection[index]

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
            self.parentID = self.nodeID
            self.parentDirection = 0
        else:
            if id in self.sonID:
                index = self.sonID.index(id) 
                del self.sonID[index]     
                del self.sonDirection[index]
                del self.sonData[index]

        self.sendtoGUI("已删除和邻居节点"+str(id)+"的连接") 
                    
    def transmitData(self,direclist,datalist):
        """
        同步通信函数，将datalist中的数据分别发到direclist的邻居方向
        """
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
        if self.SyncTurnFlag == 0:   
            self.SyncTurnFlag = 1 - self.SyncTurnFlag
            data = {
                "key": "sync",
                "id": self.nodeID,
                "tasknum": self.tasknum
            }
            ndata = json.dumps(data)      
            self.sendData(ndata)
            # 全部非空才能继续
            while (not all(self.adjSyncStatus)):   
                time.sleep(0.01)
            for i in range(len(self.adjSyncStatus)):
                self.adjSyncStatus[i] = 0

        elif self.SyncTurnFlag == 1:
            self.SyncTurnFlag = 1 - self.SyncTurnFlag
            data = {
                "key": "sync2",
                "id": self.nodeID,
                "tasknum": self.tasknum
            }
            ndata = json.dumps(data)
            self.sendData(ndata)
            while (not all(self.adjSyncStatus2)):   
                time.sleep(0.01)
            for i in range(len(self.adjSyncStatus2)):
                self.adjSyncStatus2[i] = 0

if __name__ == '__main__':

    nodeID = "room_1"
    Task.GUIinfo = ["localhost", 10000]

    task=Task(nodeID, 8)
    task.load()


    task.taskthreads.start()
    task.taskBeginFlag = 1
    t = 1
    # TaskDict = {}
    # task = Task(nodeID, 8)
    # TaskDict[0] = task
    # task2 = Task(nodeID, 1)
    # TaskDict.update({1:task2})

    # print (task.GUIinfo,TaskDict[1].GUIinfo)