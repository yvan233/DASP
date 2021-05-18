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
# import pysnooper

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


    def createServer(self,host, port):
        cont = """HTTP/1.1 200 OK\r\n"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(100)
        print ("Server on " + host + ":" + str(port))

        while 1:
            conn, addr = s.accept()
            request = self.recv_length(conn)
            method = request.split(' ')[0]
            if method == 'POST':
                form = request.split('\r\n')
                data = form[-1]
                try:
                    jdata = json.loads(data)
                except Exception:
                    self.sendUDP("通信JSON数据格式错误")
                else:
                #Comunication Topology Construction
                    if jdata["key"] == "connect":
                        num = int(jdata["tasknum"])
                        if num > 0:
                            if len(self.flag) > num:
                                if self.flag[num] == 0:
                                    self.loadNewTask(num)
                                    self.createNewTask(num)
                            else:
                                self.loadNewTask(num)
                                self.createNewTask(num)
                        if self.flag[num] == 0:
                            self.flag[num] = 1
                            self.parentID[num] = jdata["id"]
                            indext = self.adjID.index(jdata["id"])
                            self.parentDirection[num] = self.adjDirection[indext]
                            print (host + ":" + str(port) + " connected to " + jdata["host"] + ":" + str(jdata["port"]))
                            self.GUIinfo = jdata["GUIinfo"]
                            data = {
                                "key": "connect",
                                "host": host,
                                "port": port,
                                "id": self.sensorID,
                                "GUIinfo": self.GUIinfo,
                                "tasknum": num
                            }
                            ndata = json.dumps(data)
                            self.sendall_length(conn, cont, ndata)
                            
                            deleteID = []
                            for ele in self.TASKIPLIST[num]:
                                if ele != []:
                                    if ele[4] != self.parentID[num]:
                                        returnID = self.connect(ele[0], ele[1], ele[2], ele[3], ele[4], num)
                                        if returnID:
                                            deleteID.append(returnID)
                            for k in range(len(deleteID)):
                                self.deleteadjID(deleteID[k])

                            #leaf?
                            if len(self.sonID[num]) == 0:
                                data = {
                                    "key": "OK",
                                    "id": self.sensorID,
                                    "tasknum": num
                                }
                                ndata = json.dumps(data)
                                self.send(jdata["id"], data=ndata)
                                for i in range(len(self.sonFlagCreate[num])):
                                    self.sonFlagCreate[num][i] = 0
                            # print(self.parentID,self.sonID)
                        else:
                            data = {
                                "key": "connected",
                                "host": host,
                                "port": port,
                                "id": self.sensorID,
                                "tasknum": num
                            }
                            mdata = json.dumps(data)
                            self.sendall_length(conn, cont, mdata)

                    elif jdata["key"] == "OK":
                        num = int(jdata["tasknum"])
                        data = {
                            "key": "OK",
                            "id": self.sensorID,
                            "tasknum": num
                        }
                        ndata = json.dumps(data)
                        for i in range(len(self.sonID[num])):
                            if self.sonID[num][i] == jdata["id"]:
                                self.sonFlagCreate[num][i] = 1
                        nflag = 1
                        # print("sonflagcreate",self.sonFlagCreate[num])
                        for ele in self.sonFlagCreate[num]:
                            if ele == 0:
                                nflag = 0
                        if nflag == 1:
                            if self.parentID[num] != self.sensorID:
                                for ele in self.TASKIPLIST[num]:
                                    if ele != []:
                                        if ele[4] == self.parentID[num]:
                                            self.send(ele[4], data=ndata)
                            else:
                                self.treeFlag[num] = 1
                                print ("The whole tree has been constructed!")
                            for i in range(len(self.sonFlagCreate[num])):
                                self.sonFlagCreate[num][i] = 0

                    # Task Distribution
                    elif jdata["key"] == "task":
                        if self.sonID[0] != 0:
                            for ele in reversed(self.TASKIPLIST[0]):
                                if ele != []:
                                    if ele[4] in self.sonID[0]:
                                        sjdata = json.dumps(jdata)
                                        self.send(ele[4], data=sjdata)
                        for i in range(len(self.taskBeginFlag)):
                            self.taskBeginFlag[i] = 1

                    elif jdata["key"] == "newtask":
                        num = int(jdata["tasknum"])
                        if len(self.sonID[num]) != 0:
                            for ele in reversed(self.TASKIPLIST[num]):
                                if ele != []:
                                    if ele[4] in self.sonID[num]:
                                        sjdata = json.dumps(jdata)
                                        self.send(ele[4], data=sjdata)
                        # self.createNewTask(num)
                        # self.sendUDP("并行任务"+str(num+1)+"已建立",num + 1)

                    elif jdata["key"] == "starttask":
                        num = int(jdata["tasknum"])
                        if len(self.sonID[num]) != 0:
                            for ele in reversed(self.TASKIPLIST[num]):
                                if ele != []:
                                    if ele[4] in self.sonID[num]:
                                        sjdata = json.dumps(jdata)
                                        self.send(ele[4], data=sjdata)
                        self.taskthreads[num].start()
                        self.taskBeginFlag[num] = 1
                        # self.sendUDP("并行任务"+str(num+1)+"开始执行")


                    elif jdata["key"] == "shutdowntask":
                        num = int(jdata["tasknum"])
                        if len(self.sonID[num]) != 0:
                            for ele in reversed(self.TASKIPLIST[num]):
                                if ele != []:
                                    if ele[4] in self.sonID[num]:
                                        sjdata = json.dumps(jdata)
                                        self.send(ele[4], data=sjdata)
                        if self.sensorID in self.TASKID[num]:
                            self.stop_thread(self.taskthreads[num])
                        self.reset(num)
                    # Data Collection
                    elif jdata["key"] == "data":
                        mdata = jdata["data"]
                        num = jdata["tasknum"]
                        for i in range(len(self.sonID[num])):
                            if self.sonID[num][i] == jdata["id"]:
                                self.sonData[num][i] = mdata
                                self.sonFlag[num][i] = 1

                        nflag = 1
                        for ele in self.sonData[num]:
                            if ele == []:
                                nflag = 0
                        if nflag == 1:
                            self.sonFlag2[num] = 1

                    # question
                    elif jdata["key"] == "questionData":
                        num = jdata["tasknum"]
                        if jdata["type"] == "value":
                            for i in range(len(self.TASKadjID[num])):
                                if(self.TASKadjID[num][i] == jdata["id"]):
                                    self.adjData[num][i] = jdata["data"]
                                    # self.adjDataList[i].append(jdata["data"])

                        elif jdata["type"] == "feedback":
                            for i in range(len(self.TASKadjID[num])):
                                if (self.TASKadjID[num][i] == jdata["id"]):
                                    self.adjFeedback[num][i] = jdata["data"]
                                    # self.adjDataList[i].append(jdata["data"])
                          
                    elif jdata["key"] == "sync":
                        num = jdata["tasknum"]
                        for i in range(len(self.TASKadjID[num])):
                            if(self.TASKadjID[num][i] == jdata["id"]):
                                self.adjSyncStatus[num][i] = 1

                    
                    elif jdata["key"] == "sync2":
                        num = jdata["tasknum"]
                        for i in range(len(self.TASKadjID[num])):
                            if(self.TASKadjID[num][i] == jdata["id"]):
                                self.adjSyncStatus2[num][i] = 1

                    elif jdata["key"] == "newNode":
                        if jdata["applydirection"] not in self.adjDirection:
                            self.adjID.append(jdata["id"])
                            self.adjDirection.append(jdata["applydirection"])
                            direction = jdata["applydirection"] - 1
                            self.sonDirection[0].append(jdata["applydirection"])
                            self.sonID[0].append(jdata["id"])
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
                            conn.send(str.encode(cont + "节点"+str(self.sensorID)+"方向"+str(jdata["applydirection"])+"已被占用，请选择其他方向！"))

                    else:
                        conn.send(str.encode(cont+"请不要直接访问通信服务器"))
            else:
                conn.send(str.encode(cont + "请不要直接访问通信服务器"))
            conn.close()


    def taskServer(self,host,port):
        cont = """HTTP/1.1 200 OK\r\n"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(100)
        print ("TaskServer: " + host + ":" + str(port))

        while 1:
            conn, addr = s.accept()
            request = self.recv_length(conn)
            method = request.split(' ')[0]
            if method == "POST":
                form = request.split('\r\n')
                data = form[-1]
                try:
                    jdata = json.loads(data)
                except (ValueError, KeyError, TypeError):
                    conn.send(str.encode(cont + "请输入JSON格式的数据！"))
                else:
                    if jdata["key"] == "task":
                        try:
                            self.GUIinfo = jdata["GUIinfo"]
                            self.sendUDP("接收任务请求")
                        except KeyError:
                            print ("非来自GUI的任务请求")
                        self.flag[0] = 1
                        sum = 0
                        deleteID = []
                        for ele in self.TASKIPLIST[0]:
                            if ele != []:
                                returnID = self.connect(ele[0], ele[1], ele[2], ele[3], ele[4], 0)
                                if returnID:
                                    deleteID.append(returnID)
                                sum += 1
                        for k in range(len(deleteID)):
                            self.deleteadjID(deleteID[k])
                        if(sum == 0): self.treeFlag[0] = 1
                        while (self.treeFlag[0] == 0): {time.sleep(0.01)}
                        self.sendUDP("通信树建立完成")
                        sdata = {
                            "key": "task",
                            "GUIinfo": self.GUIinfo
                        }
                        sjdata = json.dumps(sdata)
                        for ele in reversed(self.TASKIPLIST[0]):
                            if ele != []:
                                if ele[4] in self.sonID[0]:
                                    self.send(ele[4], data=sjdata)

                        self.taskBeginFlag[0] = 1
                        self.sendUDPflag(2,0)

                        waitend = threading.Thread(target=self.waitforend,args=())
                        waitend.start()
                        self.waitflag = 1

                    elif jdata["key"] == "newtask":
                        num = int(jdata["tasknum"])
                        try:
                            self.GUIinfo = jdata["GUIinfo"]
                            self.sendUDP("接收任务请求",num)
                        except KeyError:
                            print ("非来自GUI的任务请求")

                        self.loadNewTask(num)
                        self.createNewTask(num)
                        self.sendUDPflag(1,num)
                        self.reset(num)

                        self.flag[num] = 1
                        sum = 0
                        deleteID = []
                        for ele in self.TASKIPLIST[num]:
                            if ele != []:
                                returnID = self.connect(ele[0], ele[1], ele[2], ele[3], ele[4], num)
                                if returnID:
                                    deleteID.append(returnID)
                                sum += 1
                        for k in range(len(deleteID)):
                            self.deleteadjID(deleteID[k])

                        if(sum == 0): self.treeFlag[num] = 1
                        while (self.treeFlag[num] == 0): {time.sleep(0.01)}
                        self.sendUDP("通信树建立完成")
                        for ele in reversed(self.TASKIPLIST[num]):
                            if ele != []:
                                if ele[4] in self.sonID[num]:
                                    sdata = {
                                        "key": "newtask",
                                        "GUIinfo": self.GUIinfo,
                                        "tasknum": jdata["tasknum"]
                                    }
                                    sjdata = json.dumps(sdata)
                                    self.send(ele[4], data=sjdata)

                        delay = jdata["delay"]
                        if delay > 0:
                            self.sendUDP("任务"+str(num)+"将于"+str(jdata["delay"])+"秒后开始",num)
                        self.taskthreads[num].start()
                        starttaskthread = threading.Thread(target=self.starttask,args=(num, delay ,))
                        starttaskthread.start()

                        if self.waitflag == 0:
                            waitend = threading.Thread(target=self.waitforend,args=())
                            waitend.start()
                            self.waitflag = 1

                    elif jdata["key"] == "shutdowntask":
                        num = int(jdata["tasknum"])
                        for ele in reversed(self.TASKIPLIST[num]):
                            if ele != []:
                                if ele[4] in self.sonID[num]:
                                    sdata = {
                                        "key": "shutdowntask",
                                        "tasknum": jdata["tasknum"]
                                    }
                                    sjdata = json.dumps(sdata)
                                    self.send(ele[4], data=sjdata)
                        if self.sensorID in self.TASKID[num]:
                            self.stop_thread(self.taskthreads[num])
                        self.sendUDPflag(0,num)
                        self.reset(num)

                    elif jdata["key"] == "restart":
                        try:
                            self.GUIinfo = jdata["GUIinfo"]
                            self.sendUDP("接收任务请求")
                        except KeyError:
                            print ("非来自GUI的任务请求")
                        self.flag[0] = 1
                        deleteID = []
                        for ele in self.TASKIPLIST[0]:
                            if ele != []:
                                index = self.adjID.index(ele[4])
                                returnID = self.reconnect(ele[0], ele[1], ele[2], ele[3], ele[4], self.AdjOtherSideDirection[index])
                                if returnID:
                                    deleteID.append(returnID)
                        for k in range(len(deleteID)):
                            self.deleteadjID(deleteID[k])                        
                        self.taskBeginFlag[0] = 1
                        self.sendUDPflag(2,0)

                        waitend = threading.Thread(target=self.waitforend,args=())
                        waitend.start()
                        self.waitflag = 1

                    else:
                        conn.send(str.encode(cont + "您输入的任务信息有误！"))
            else:
                conn.send(str.encode(cont + "暂未提供GET接口返回数据"))
            conn.close()

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

    # @pysnooper.snoop("sever_connect.log")
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

    # @pysnooper.snoop("sever_send.log")  
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

    # @pysnooper.snoop("sever_task.log")
    def taskFunction(self,tasknum = 0):
        try:
            num = tasknum
            while 1:
                time.sleep(0.01)
                if self.taskBeginFlag[num] == 1:
                    try:
                        taskfunc = self.taskFuncList[num]
                        self.sendUDP("任务"+ str(tasknum) +" 开始执行",tasknum)
                        value = taskfunc(self, self.sensorID, self.TASKadjDirection[num], self.TASKDATALIST[num], tasknum)
                        self.sensorInfo[num]["value"] = value
                        self.sendUDP("任务"+ str(tasknum) +" 执行完毕",tasknum)
                        # time.sleep(1)  # 防止该节点任务结束，其他节点的同步函数出错
                        print ("value:", value)
                    except Exception as e:
                        self.sensorInfo[num]["value"] = ""
                        self.sendUDP("任务"+ str(tasknum) +" 执行出错",tasknum)
                        self.sendUDP(traceback.format_exc(),tasknum)

                    self.taskFlag[num] = 1
                    if self.sonID[num] == []:
                        if self.parentID[num] == self.sensorID:
                            sdata = {
                                "id": self.sensorID,
                                "info": self.sensorInfo[num]
                            }
                            self.mesQue[num].append(sdata)
                            self.dataFlag[num] = 1
                            print ("The whole data has been transmitted!")
                        else:
                            sdata = {
                                "id": self.sensorID,
                                "info": self.sensorInfo[num]
                            }
                            self.mesQue[num].append(sdata)
                            data = {
                                "key": "data",
                                "tasknum": tasknum,
                                "id": self.sensorID,
                                "data": self.mesQue[num]
                            }
                            ndata = json.dumps(data)
                            self.send(self.parentID[num], ndata)
                            self.mesQue[num] = []
                    else:
                        print ("wait sonflag2")
                        ii = 0
                        while self.sonFlag2[tasknum] == 0 and ii < 1000:
                            time.sleep(0.01)
                            ii = ii + 1
                        if ii == 1000:
                            print ("timeout!")
                            deleteID = []
                            for k in range(len(self.sonData[tasknum])):
                                if not self.sonData[tasknum][k]:
                                    deleteID.append(self.sonID[tasknum][k])
                            for k in range(len(deleteID)):   
                                self.sendUDP("邻居节点"+deleteID[k]+"连接不上")
                                print ("与邻居节点"+deleteID[k]+"连接失败")
                                self.deleteadjID(deleteID[k])  
                                self.sendUDP("已删除和邻居节点"+(deleteID[k])+"的连接") 

                        print ("sonflag2 complete")
                        sdata = {
                            "id": self.sensorID,
                            "info": self.sensorInfo[num]
                        }
                        self.mesQue[num].append(sdata)
                        for ele in self.sonData[tasknum]:
                            for ele2 in ele:
                                self.mesQue[num].append(ele2)
                        if self.parentID[num] != self.sensorID:
                            data = {
                                "key": "data",
                                "tasknum": tasknum,
                                "id": self.sensorID,
                                "data": self.mesQue[num]
                            }
                            ndata = json.dumps(data)
                            self.send(self.parentID[num], data=ndata)
                            self.mesQue[num] = []
                        else:
                            self.dataFlag[num] = 1
                            print ("The whole data has been transmitted!")
                    
                    # print("sensorInfo", self.sensorInfo)
                    self.taskBeginFlag[num] = 0
                    self.reset(num)
                    self.resetadjData(num)
                    return 0
                
        except SystemExit:
            self.sendUDP("任务"+ str(tasknum) +" 停止执行",tasknum)


    def dataFunction(self,tasknum = 0):
        try:
            num = tasknum
            self.taskFlag[num] = 1
            time.sleep(1)
            if self.sonID[num] == []:
                if self.parentID[num] == self.sensorID:
                    sdata = {
                        "id": self.sensorID,
                        "info": self.sensorInfo[num]
                    }
                    self.mesQue[num].append(sdata)
                    self.dataFlag[num] = 1
                    print ("The whole data has been transmitted!")
                else:
                    sdata = {
                        "id": self.sensorID,
                        "info": self.sensorInfo[num]
                    }
                    self.mesQue[num].append(sdata)
                    data = {
                        "key": "data",
                        "tasknum": tasknum,
                        "id": self.sensorID,
                        "data": self.mesQue[num]
                    }
                    ndata = json.dumps(data)
                    self.send(self.parentID[num], ndata)
                    self.mesQue[num] = []

            else:
                ii = 0
                while self.sonFlag2[tasknum] == 0 and ii < 1000:
                    time.sleep(0.01)
                    ii = ii + 1
                if ii == 1000:
                    print ("timeout!")
                    deleteID = []
                    for k in range(len(self.sonData[tasknum])):
                        if not self.sonData[tasknum][k]:
                            deleteID.append(self.sonID[tasknum][k])
                    for k in range(len(deleteID)):   
                        self.deleteadjID(deleteID[k])  

                sdata = {
                    "id": self.sensorID,
                    "info": self.sensorInfo[num]
                }
                self.mesQue[num].append(sdata)
                for ele in self.sonData[tasknum]:
                    for ele2 in ele:
                        self.mesQue[num].append(ele2)
                if self.parentID[num] != self.sensorID:
                    data = {
                        "key": "data",
                        "tasknum": tasknum,
                        "id": self.sensorID,
                        "data": self.mesQue[num]
                    }
                    ndata = json.dumps(data)
                    self.send(self.parentID[num], data=ndata)
                    self.mesQue[num] = []
                else:
                    self.dataFlag[num] = 1
                    print ("The whole data has been transmitted!")
            self.reset(num)
            self.resetadjData(num)
        except SystemExit:
            self.sendUDP("任务"+ str(tasknum) +" 停止执行",tasknum)


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


    def shutdown(self):
        sys.exit(0)

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

    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop_thread(self, thread):
        self._async_raise(thread.ident, SystemExit)

    def sendall_length(self, s, head, data):
        length = "content-length:"+str(len(data)) + "\r\n\r\n"
        message = head + length + data
        s.sendall(str.encode(message))

    def recv_length(self, conn):
        request = conn.recv(1024)
        message = bytes.decode(request)
        message_split = message.split('\r\n')
        content_length = message_split[1][15:]
        message_length =  len(message_split[0]) + len(message_split[1]) + 2*(len(message_split)-1) + int(content_length)
        while True:
            if len(message) < message_length:
                request = conn.recv(1024)
                message += bytes.decode(request)
            else:
                break
        return message