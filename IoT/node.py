import codecs
import copy
import ctypes
import importlib
import inspect
import json
import os
import socket
import sys
import threading
import time
import traceback

sys.path.insert(1,".")  # 把上一级目录加入搜索路径
from IoT.system.common import DaspFuncMixin

class Sensor(object):
    taskFuncList = []
    sensorID = 0
    IP = ""
    PORT = []
    IPlist = []
    sensorInfo = []
    adjID = []
    adjDirection = []
    AdjOtherSideDirection = []
    datalist = []
    GUIinfo = [0,0]

    parentID = [0]
    sonID = [[]]
    parentDirection = [0]
    sonDirection = [[]]
    sonFlagCreate = [[]]
    flag = [0]
    treeFlag = [0]

    mesQue = []
    threads = []
    taskthreads = []

    dataFlag = []
    taskFlag = []
    taskBeginFlag = []

    adjDataList = []

    waitflag = 0

    # parallel
    taskcounter = 1
    sonFlag = []
    sonData = []
    sonFlag2 = []
    tk = []
    tk2 = []
    adjData = []
    adjFeedback = []
    adjSyncStatus = []
    adjSyncFlag = []
    adjSyncStatus2 = []
    adjSyncFlag2 = []

    TASKID = []
    TASKIPLIST = []
    TASKDATALIST = []
    TASKadjDirection = []
    TASKadjID = []

    def __init__(self, ID, adjID, adjDirection, AdjOtherSideDirection, IPlist,IP,PORT,datalist):

        self.taskFuncList = []
        question = importlib.import_module("task.question0")
        question = importlib.reload(question)
        self.taskFuncList.append(question.taskFunction)

        self.sensorID = ID
        self.parentID[0] = ID
        self.parentDirection[0] = 0
        self.IP = IP
        self.PORT = PORT
        self.adjID = adjID
        self.adjDirection = adjDirection
        self.AdjOtherSideDirection = AdjOtherSideDirection
        self.IPlist = IPlist
        self.datalist = datalist
        self.IP = socket.gethostbyname(self.IP)

        self.TASKDATALIST.append(datalist)
        self.TASKadjDirection.append(adjDirection)
        self.TASKadjID.append(adjID)
        self.TASKID.append([])
        self.TASKIPLIST.append(IPlist)

        ###############################
        self.taskcounter = 1
        # for i in range(self.taskcounter):
        self.taskBeginFlag.append(0)
        self.taskFlag.append(0)
        self.dataFlag.append(0)
        self.sensorInfo.append({})
        self.mesQue.append([])

        self.sonFlag.append([])
        self.sonData.append([])
        self.sonFlag2.append(0)

        self.tk.append(0)
        self.tk2.append(0)
        self.adjData.append([])
        self.adjFeedback.append([])
        self.adjSyncStatus.append([])
        self.adjSyncFlag.append(0)
        self.adjSyncStatus2.append([])
        self.adjSyncFlag2.append(0)

        for i in range(len(self.adjID)):
            for j in range(len(self.adjData)):
                self.adjData[j].append([])
                # self.adjDataList[j].append([])
                self.adjFeedback[j].append([])
                self.adjSyncStatus[j].append(0)
                self.adjSyncStatus2[j].append(0)


    def starttask(self, num, delay):
        time.sleep(delay)
        sdata = {
            "key": "starttask",
            "tasknum": num
        }
        for ele in reversed(self.TASKIPLIST[num]):
            if ele != []:
                if ele[4] in self.sonID[num]:
                    sjdata = json.dumps(sdata)
                    self.send(ele[4], data=sjdata)
        self.taskBeginFlag[num] = 1
        self.sendUDPflag(2,num)

    def deleteadjID(self, adjID):  
        if adjID in self.adjID:
            index = self.adjID.index(adjID)      
            del self.adjID[index]
            del self.adjDirection[index]
        for m in range(len(self.TASKIPLIST)):
            for ele in self.TASKIPLIST[m]:
                if ele != []:
                    if ele[4] == adjID:
                        self.TASKIPLIST[m].remove(ele)
                        break
            if adjID in self.TASKadjID[m]:
                index = self.TASKadjID[m].index(adjID)      
                del self.TASKadjID[m][index]
                del self.TASKadjDirection[m][index]   
                del self.adjSyncStatus[m][index]    #同步标志位  
                del self.adjSyncStatus2[m][index]     
                del self.adjData[m][index]
                del self.adjFeedback[m][index]
        for m in range(len(self.sonID)):
            if self.parentID[m] == adjID:
                self.parentID[m] = self.sensorID
                self.parentDirection[m] = 0
            else:
                if adjID in self.sonID[m]:
                    index = self.sonID[m].index(adjID) 
                    del self.sonID[m][index]     
                    del self.sonDirection[m][index]
                    del self.sonData[m][index]
                    del self.sonFlag[m][index]

    def connect(self,host1,port1,host2,port2,adjID,tasknum):
        data = {
            "key": "connect",
            "host": host1,
            "port": port1,
            "id": self.sensorID,
            "GUIinfo": self.GUIinfo,
            "tasknum": tasknum
        }
        try:
            print (host1 + ":" + str(port1) + " connecting to " + host2 + ":" + str(port2))
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_ip = socket.gethostbyname(host2)
            s.connect((remote_ip, port2))
            cont = "POST / HTTP/1.1\r\n"
            jsondata = json.dumps(data)
            self.sendall_length(s, cont, jsondata)
            reply = self.recv_length(s)
            res = reply.split('\r\n')[-1]
            jres = json.loads(res)
            # print (str(res))
            if jres['key'] == 'connect':
                self.sonID[tasknum].append(jres["id"])
                indext = self.adjID.index(jres["id"])
                self.sonDirection[tasknum].append(self.adjDirection[indext])
                self.sonFlagCreate[tasknum].append(0)
                self.sonFlag[tasknum].append(0)
                self.sonData[tasknum].append([])
        except Exception as e:
            self.sendUDP("邻居节点"+adjID+"连接不上",tasknum)
            # print(traceback.format_exc())
            print ("与邻居节点"+adjID+"连接失败")
            return adjID
                   
            
    def reconnect(self,host1,port1,host2,port2,adjID,direction):
        data = {
            "key": "newNode",
            "host": host1,
            "port": port1,
            "id": self.sensorID,
            "applydirection": direction
        }
        try:
            print (host1 + ":" + str(port1) + " connecting to " + host2 + ":" + str(port2))
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_ip = socket.gethostbyname(host2)
            s.connect((remote_ip, port2))
            cont = "POST / HTTP/1.1\r\n"
            jsondata = json.dumps(data)
            self.sendall_length(s, cont, jsondata)
            s.close()
        except Exception as e:
            self.sendUDP("邻居节点"+adjID+"连接不上")
            # print(traceback.format_exc())
            print ("与邻居节点"+adjID+"连接失败")
            return adjID
  
    def send(self,id,data):
        for ele in self.TASKIPLIST[0]:
            if ele!=[]:
                if ele[4] == id:
                    try:
                        host = ele[2]
                        port = ele[3]
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        remote_ip = socket.gethostbyname(host)
                        s.connect((remote_ip, port))
                        cont = "POST / HTTP/1.1\r\n"
                        self.sendall_length(s, cont, data)
                        s.close()
                    except Exception as e:
                        self.sendUDP("邻居节点"+id+"连接不上")
                        print ("与邻居节点"+id+"连接失败")
                        self.deleteadjID(id)
                        self.sendUDP("已删除和邻居节点"+(id)+"的连接") 
                    break

    def sendDataToID(self, id, data, tasknum = 1):
        data = {
            "key": "questionData",
            "type": "value",
            "tasknum": tasknum,
            "id": self.sensorID,
            "data": data
        }
        ndata = json.dumps(data)
        for ele in self.TASKIPLIST[0]:
            if ele != []:
                if ele[4] == id:
                    self.send(ele[4], ndata)

    def sendDataToDirection(self, direction, data, tasknum = 1):
        data = {
            "key": "questionData",
            "type": "value",
            "tasknum": tasknum,
            "id": self.sensorID,
            "data": data
        }
        ndata = json.dumps(data)
        for i in range(len(self.adjID)):
            if self.adjDirection[i] ==  direction:
                for ele in self.TASKIPLIST[0]:
                    if ele != []:
                        if ele[4] == self.adjID[i]:
                            self.send(ele[4], ndata)

    def sendDataToDirectionfeedback(self, direction, data, tasknum = 1):
        data = {
            "key": "questionData",
            "type": "feedback",
            "tasknum": tasknum,
            "id": self.sensorID,
            "data": data
        }
        ndata = json.dumps(data)
        for i in range(len(self.adjID)):
            if self.adjDirection[i] ==  direction:
                for ele in self.TASKIPLIST[0]:
                    if ele != []:
                        if ele[4] == self.adjID[i]:
                            self.send(ele[4], ndata)

    def sendData(self, data):
        data = {
            "key": "questionData",
            "type": "value",
            "id": self.sensorID,
            "data": data
        }
        ndata = json.dumps(data)
        for ele in reversed(self.TASKIPLIST[0]):
            if ele != []:
                self.send(ele[4], ndata)

    def receive(self,tasknum = 0):
        return self.adjData[tasknum]

    def sendUDP(self, info, tasknum = 0):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            addr = (self.GUIinfo[0], self.GUIinfo[1])
            data = {
                "key": "runData",
                "id": self.sensorID,
                "tasknum":tasknum,
                "info": info
            }
            s.sendto(json.dumps(data).encode('utf-8'), addr)
            s.close()
        except Exception as e:
            print (info)

    def sendUDPEnd(self, info, tasknum = 0):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            addr = (self.GUIinfo[0], self.GUIinfo[1])
            data = {
                "key": "endData",
                "id": self.sensorID,
                "tasknum": tasknum,
                "info": info
            }
            s.sendto(json.dumps(data).encode('utf-8'), addr)
            s.close()
        except Exception as e:
            print (info)

    def sendUDPflag(self, info, tasknum = 0):
        #0 未启动
        #1 启动未运行
        #2 运行中
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            addr = (self.GUIinfo[0], self.GUIinfo[1])
            data = {
                "key": "runFlag",
                "id": self.sensorID,
                "tasknum":tasknum,
                "info": info
            }
            s.sendto(json.dumps(data).encode('utf-8'), addr)
            s.close()
        except Exception as e:
            print (info)

    def waitforend(self):
        while 1:
            time.sleep(0.01)
            for j in range(len(self.taskFlag)):
                if self.dataFlag[j] == 1:
                    time.sleep(1)   # 防止结果显示超前其他节点
                    self.sendUDP("任务"+str(j)+" 数据收集完毕", j)
                    info = []
                    content = ""
                    for i in range(len(self.mesQue[j])):
                        if self.mesQue[j][i]["info"]:
                            info.append({})
                            info[-1]["value"] = self.mesQue[j][i]["info"]["value"]
                            info[-1]["ID"] = self.mesQue[j][i]["id"]
                    content =  "task " + str(j) + "\n" + "dataNum:" + str(len(self.mesQue[j])) + "\nInfo:" + str(info) + "\n\n"
                    self.sendUDPEnd(content,j)
                    self.sendUDPflag(0,j)
                    self.taskFlag[j] = 0
                    self.dataFlag[j] = 0
                    self.mesQue[j] = []
                    self.sensorInfo[j] = {}
                    
    def loadNewTask(self,tasknum):
        num = tasknum
        # question
        while len(self.taskFuncList) <= tasknum:
            self.taskFuncList.append([])
        while len(self.TASKID) <= tasknum:
            self.TASKDATALIST.append([])
            self.TASKadjID.append([])
            self.TASKadjDirection.append([])
            self.TASKID.append([])
            self.TASKIPLIST.append([])

        question = importlib.import_module("task.question"+str(num))
        question = importlib.reload(question)
        self.taskFuncList[num] = question.taskFunction
        # topology
        ID = []
        adjID = []
        datalist = []
        adjDirection = []
        path = os.getcwd() + "\\IoT\\task\\topology"+str(num)+".txt"
        # path = "/home/pi/zhongdy/IoT/task/topology"+str(num)+".txt"
        text = codecs.open(path, 'r', 'utf-8').read()
        js = json.loads(text)
        for ele in js:
            if "ID" in ele:
                ID.append(ele["ID"])
                adjID.append(ele["adjID"])
                adjDirection.append(ele["adjDirection"])
                datalist.append(ele["datalist"])
        self.TASKID[num] = ID
        # 如果在任务中
        if self.sensorID in self.TASKID[num]:
            order = ID.index(self.sensorID)
            selfID = ID[order]
            selfAdjID = adjID[order]
            selfAdjDirection = adjDirection[order]
            selfDatalist = datalist[order]
            selfIPList = []

            for i in range(len(selfAdjID)-1,-1,-1):
                if selfAdjID[i] not in self.adjID:
                    selfAdjID.remove(selfAdjID[i])
                    selfAdjDirection.remove(selfAdjDirection[i])

            for i in range(len(selfAdjID)):
                selfIPList.append([])
                for ele in self.IPlist:
                    if ele[4] == selfAdjID[i]:
                        selfIPList[i] = ele
                        break
            self.TASKadjDirection[num] = selfAdjDirection
            self.TASKadjID[num] = selfAdjID
            self.TASKDATALIST[num] = selfDatalist
            self.TASKIPLIST[num] = selfIPList


    def createNewTask(self,tasknum):
        num = tasknum
        while len(self.taskthreads) <= tasknum:
            self.taskthreads.append([])
            # init
            self.taskcounter = self.taskcounter + 1

            self.taskBeginFlag.append(0)
            self.taskFlag.append(0)
            self.dataFlag.append(0)
            self.sensorInfo.append({})
            self.mesQue.append([])

            self.sonFlag.append([])
            self.sonData.append([])
            self.sonFlag2.append(0)

            self.tk.append(0)
            self.tk2.append(0)
            self.adjData.append([])
            self.adjFeedback.append([])
            self.adjSyncStatus.append([])
            self.adjSyncFlag.append(0)
            self.adjSyncStatus2.append([])
            self.adjSyncFlag2.append(0)

            self.flag.append(0)
            self.treeFlag.append(0)
            self.parentID.append(0)
            self.parentDirection.append(0)
            self.sonID.append([])
            self.sonDirection.append([])
            self.sonFlagCreate.append([])


        while len(self.adjData[num]) < len(self.TASKadjDirection[num]):
            self.adjData[num].append([])
            self.adjFeedback[num].append([])
            self.adjSyncStatus[num].append(0)
            self.adjSyncStatus2[num].append(0)


        # while len(self.sonFlag[num]) < len(self.sonFlag[0]) :
        #     self.sonFlag[num].append(0)
        # while len(self.sonData[num]) < len(self.sonData[0]) :
        #     self.sonData[num].append([])

            # 给其他节点开线程的时间，防止换数据的时候其他节点线程还没开
            # time.sleep(1)
        if self.sensorID in self.TASKID[num]:
            t = threading.Thread(target=self.taskFunction, args=(num,))
            self.taskthreads[num] = t
        else:
            t = threading.Thread(target=self.dataFunction, args=(num,))
            self.taskthreads[num] = t

    def run(self):
        #创建接口服务器
        for i in range(6):
            t = threading.Thread(target=self.createServer,args=(self.IP,self.PORT[i],))
            self.threads.append(t)
        taskServerthread = threading.Thread(target=self.taskServer,args=(self.IP,self.PORT[6],))
        t = threading.Thread(target=self.taskFunction, args=(0,))
        self.taskthreads.append(t)

        for i in range(6):
            self.threads[i].start()
        taskServerthread.start()
        self.taskthreads[0].start()

    def reset(self, tasknum = 0):
        self.flag[tasknum] = 0
        self.treeFlag[tasknum] = 0
        self.parentID[tasknum] = self.sensorID
        self.parentDirection[tasknum] = 0
        self.sonID[tasknum] = []
        self.sonDirection[tasknum] = []
        self.sonFlagCreate[tasknum] = []

        # self.mesQue[tasknum] = []
        self.sonFlag[tasknum] = []
        self.sonFlag2[tasknum] = 0
        self.sonData[tasknum] = []
    
    def resetadjData(self, tasknum = 0):
        for i in range(len(self.adjData[tasknum])):
            self.adjData[tasknum][i] = []
            self.adjFeedback[tasknum][i] = []

    def transmitData(self,direclist,datalist,tasknum = 0):
        '''
        同步通信函数
        '''
        num = tasknum
        if (self.tk[num] % 2 == 0):
            self.tk[num] += 1
            for i in reversed(range(len(direclist))):
                self.sendDataToDirection(direclist[i],datalist[i], num)
            self.syncNode(num) 
            ans = copy.deepcopy([self.TASKadjDirection[num], self.adjData[num]])
            for i in range(len(self.adjData[num])):
                self.adjData[num][i] = []
        else:
            self.tk[num] += 1
            for i in reversed(range(len(direclist))):
                self.sendDataToDirectionfeedback(direclist[i],datalist[i], num)
            self.syncNode(num) 
            ans = copy.deepcopy([self.TASKadjDirection[num], self.adjFeedback[num]])
            for i in range(len(self.adjFeedback[num])):
                self.adjFeedback[num][i] = []    
        return ans
    
    def syncNode(self, tasknum = 0):
        '''
        异步通信的同步函数
        '''
        num = tasknum
        if self.tk2[num] == 0:   
            self.tk2[num] = 1 - self.tk2[num]
            data = {
                "key": "sync",
                "id": self.sensorID,
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
        elif self.tk2[num] == 1:
            self.tk2[num] = 1 - self.tk2[num]
            data = {
                "key": "sync2",
                "id": self.sensorID,
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
