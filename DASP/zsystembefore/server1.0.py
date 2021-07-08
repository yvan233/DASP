# coding=utf-8

import json
import threading
import socket
import random
import sys
import time
import question
import traceback


class Sensor(object):
    sensorID = 0
    IP = ""
    PORT = []
    IPlist = []
    sensorInfo = {}
    adjID = []
    datalist = []
    GUIinfo = []

    taskID = ""
    parentID = 0
    sonID = []
    sonFlag = []
    sonData = []
    mesQue = []
    threads = []
    flag = 0
    sonFlag2 = 0
    treeFlag = 0
    dataFlag = 0
    taskFlag = 0
    taskBeginFlag = 0
    tk = 0
    tk2 = 0

    adjData = []
    adjDataList = []
    adjFeedback = []
    adjFlag = []
    adjFlag2 = 0
    adjFeedbackFlag = []
    adjFeedbackFlag2 = 0

    adjSyncStatus = []
    adjSyncStatus2 = []

    def __init__(self, ID, adjID, IPlist,IP,PORT,datalist):
        self.sensorID = int(ID)
        self.parentID = int(ID)
        self.IP = IP
        self.PORT = PORT
        self.adjID = adjID
        self.IPlist = IPlist
        self.datalist = datalist
        self.IP = socket.gethostbyname(self.IP)
        for i in range(len(self.adjID)):
            self.adjData.append([])
            # self.adjDataList.append([])
            self.adjFeedback.append([])
            self.adjFlag.append(0)
            self.adjFeedbackFlag.append(0)
            self.adjSyncStatus.append(0)
            self.adjSyncStatus2.append(0)

    def createServer(self,host, port):
        cont = """HTTP/1.1 200 OK\r\n\r\n"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(100)
        print "Server on " + host + ":" + str(port)

        while 1:
            conn, addr = s.accept()
            request = conn.recv(655350)
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
                        if self.flag == 0:
                            self.flag = 1
                            self.parentID = jdata["id"]
                            print host + ":" + str(port) + " connected to " + jdata["host"] + ":" + str(jdata["port"])
                            data = {
                                "key": "connect",
                                "host": host,
                                "port": port,
                                "id": self.sensorID
                            }
                            ndata = json.dumps(data)
                            content = cont + ndata
                            conn.sendall(content)
                            for ele in self.IPlist:
                                if ele != []:
                                    if ele[4] != self.parentID:
                                        self.connect(ele[0],ele[1],ele[2],ele[3])
                            #leaf?
                            if len(self.sonID) == 0:
                                data = {
                                    "key": "OK",
                                    "id": self.sensorID
                                }
                                ndata = json.dumps(data)
                                self.send(jdata["id"], data=ndata)
                                for i in range(len(self.sonFlag)):
                                    self.sonFlag[i] = 0
                        else:
                            data = {
                                "key": "connected",
                                "host": host,
                                "port": port,
                                "id": self.sensorID
                            }
                            mdata = json.dumps(data)
                            content = cont + mdata
                            conn.sendall(content)

                    elif jdata["key"] == "OK":
                        data = {
                            "key": "OK",
                            "id": self.sensorID
                        }
                        ndata = json.dumps(data)
                        for i in range(len(self.sonID)):
                            if self.sonID[i] == jdata["id"]:
                                self.sonFlag[i] = 1
                        nflag = 1
                        for ele in self.sonFlag:
                            if ele == 0:
                                nflag = 0
                        if nflag == 1:
                            if self.parentID != self.sensorID:
                                for ele in self.IPlist:
                                    if ele != []:
                                        if ele[4] == self.parentID:
                                            self.send(ele[4], data=ndata)
                            else:
                                self.treeFlag = 1
                                print "The whole tree has been constructed!"
                            for i in range(len(self.sonFlag)):
                                self.sonFlag[i] = 0

                    # Task Distribution
                    elif jdata["key"] == "task":
                        self.taskID = jdata["taskID"]
                        try:
                            self.GUIinfo.append(jdata["GUIinfo"][0])
                            self.GUIinfo.append(jdata["GUIinfo"][1])
                            self.sendUDP("任务开始执行")
                        except Exception, e:
                            print "非来自GUI的任务请求"
                        if self.sonID != 0:
                            for ele in self.IPlist:
                                if ele != []:
                                    if ele[4] in self.sonID:
                                        sjdata = json.dumps(jdata)
                                        self.send(ele[4], data=sjdata)
                        self.taskBeginFlag = 1

                    # Data Collection
                    elif jdata["key"] == "data":
                        mdata = jdata["data"]
                        for i in range(len(self.sonID)):
                            if self.sonID[i] == jdata["id"]:
                                self.sonData[i] = mdata
                                self.sonFlag[i] = 1
                        nflag = 1
                        for ele in self.sonData:
                            if ele == []:
                                nflag = 0
                        if nflag == 1:
                            self.sonFlag2 = 1

                    # question
                    elif jdata["key"] == "questionData":
                        if jdata["type"] == "value":
                            for i in range(len(self.adjID)):
                                if(self.adjID[i] == jdata["id"]):
                                    self.adjFlag[i] = 1
                                    self.adjData[i] = jdata["data"]
                                    # self.adjDataList[i].append(jdata["data"])
                            nflag = 1
                            for ele in self.adjFlag:
                                if ele == 0:
                                    nflag = 0
                            if nflag == 1:
                                self.adjFlag2 = 1

                        elif jdata["type"] == "feedback":
                            for i in range(len(self.adjID)):
                                if (self.adjID[i] == jdata["id"]):
                                    self.adjFeedbackFlag[i] = 1
                                    self.adjFeedback[i] = jdata["data"]
                                    # self.adjDataList[i].append(jdata["data"])
                            nflag = 1
                            for ele in self.adjFeedbackFlag:
                                if ele == 0:
                                    nflag = 0
                            if nflag == 1:
                                self.adjFeedbackFlag2 = 1
                        conn.send(cont)

                    elif jdata["key"] == "sync":
                        for i in range(len(self.adjID)):
                            if(self.adjID[i] == jdata["id"]):
                                self.adjSyncStatus[i] = 1

                    elif jdata["key"] == "sync2":
                        for i in range(len(self.adjID)):
                            if(self.adjID[i] == jdata["id"]):
                                self.adjSyncStatus2[i] = 1

                    else:
                        conn.send(cont+"请不要直接访问通信服务器")
            else:
                conn.send(cont + "请不要直接访问通信服务器")
            conn.close()

    #Task Server
    def taskServer(self,host,port):
        cont = """HTTP/1.1 200 OK\r\n\r\n"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(100)
        print "TaskServer: " + host + ":" + str(port)

        while 1:
            conn, addr = s.accept()
            request = conn.recv(10000000)
            method = request.split(' ')[0]
            if method == "POST":
                form = request.split('\r\n')
                data = form[-1]
                try:
                    jdata = json.loads(data)
                except (ValueError, KeyError, TypeError):
                    conn.send(cont + "请输入JSON格式的数据！")
                else:
                    if jdata["key"] == "task":
                        try:
                            self.GUIinfo.append(jdata["GUIinfo"][0])
                            self.GUIinfo.append(jdata["GUIinfo"][1])
                            self.sendUDP("接收任务请求")
                        except KeyError:
                            print "非来自GUI的任务请求"
                        self.flag = 1
                        self.taskID = jdata["taskID"]
                        sum = 0
                        for ele in self.IPlist:
                            if ele != []:
                                self.connect(ele[0], ele[1], ele[2], ele[3])
                                sum += 1
                        if(sum == 0): self.treeFlag = 1
                        while (self.treeFlag == 0): {time.sleep(0.01)}
                        self.sendUDP("通信树建立完成")
                        self.sendUDP("任务开始执行")
                        for ele in self.IPlist:
                            if ele != []:
                                sdata = {
                                    "key": "task",
                                    "taskID": self.taskID,
                                    "GUIinfo": self.GUIinfo
                                }
                                sjdata = json.dumps(sdata)
                                self.send(ele[4], data=sjdata)
                        self.taskBeginFlag = 1
                        while (self.taskFlag == 0):{time.sleep(0.01)}
                        while (self.dataFlag == 0):{time.sleep(0.01)}
                        self.sendUDP("数据收集完毕")
                        if self.taskID == "averageTemperature":
                            sum = 0
                            for ele in self.mesQue:
                                sum = sum + ele["info"]["temperature"]
                            content = cont + "sensorID:" + str(self.sensorID) + "\n" + "dataNum:" + str(len(self.mesQue)) + "\naverage:" + str(float(sum)/len(self.mesQue))
                        else:
                            info = []
                            for i in range(len(self.mesQue)):
                                info.append({})
                                info[i]["value"] = self.mesQue[i]["info"]["value"]
                                info[i]["ID"] = self.mesQue[i]["id"]
                            content = cont + "sensorID:" + str(self.sensorID) + "\n" + "dataNum:" + str(len(self.mesQue)) + "\nInfo:" + str(info)
                        conn.sendall(content)
                        self.reset()
                        self.treeFlag = 0
                        self.dataFlag = 0
                    elif jdata["key"] == "newNode":
                        self.IPlist = jdata["IPlist"]
                        self.adjID.append(jdata["id"])
                    elif jdata["key"] == "deleteNode":
                        self.IPlist = jdata["IPlist"]
                        self.adjID = jdata["adjID"]
                    else:
                        conn.send(cont + "您输入的任务信息有误！")
            else:
                conn.send(cont + "暂未提供GET接口返回数据")
            conn.close()

    def connect(self,host1,port1,host2,port2):
        print host1 + ":" + str(port1) + " connecting to " + host2 + ":" + str(port2)
        data = {
            "key": "connect",
            "host": host1,
            "port": port1,
            "id": self.sensorID
        }
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_ip = socket.gethostbyname(host2)
        s.connect((remote_ip, port2))
        message = "POST / HTTP/1.1\r\n\r\n"
        jsondata = json.dumps(data)
        message += jsondata
        s.sendall(message)
        reply = s.recv(10000)
        res = reply.split('\r\n')[-1]
        jres = json.loads(res)
        if jres['key'] == 'connect':
            self.sonID.append(jres["id"])
            self.sonFlag.append(0)
            self.sonData.append([])

    def send(self,id,data):
        for ele in self.IPlist:
            if ele!=[]:
                if ele[4] == id:
                    host = ele[2]
                    port = ele[3]
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    remote_ip = socket.gethostbyname(host)
                    s.connect((remote_ip, port))
                    message = "POST / HTTP/1.1\r\n\r\n"
                    message += data
                    s.sendall(message)
                    break

    def sendDataToID(self, id, data):
        data = {
            "key": "questionData",
            "type": "value",
            "id": self.sensorID,
            "data": data
        }
        ndata = json.dumps(data)
        for ele in self.IPlist:
            if ele != []:
                if ele[4] == id:
                    self.send(ele[4], ndata)

    def sendData(self, data):
        data = {
            "key": "questionData",
            "type": "value",
            "id": self.sensorID,
            "data": data
        }
        ndata = json.dumps(data)
        for ele in self.IPlist:
            if ele != []:
                self.send(ele[4], ndata)

    def receive(self):
        return self.adjData

    def sendUDP(self, info):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            addr = (self.GUIinfo[0], self.GUIinfo[1])
            data = {
                "key": "runData",
                "id": self.sensorID,
                "info": info
            }
            s.sendto(json.dumps(data), addr)
            s.close()
        except Exception, e:
            print info

    def taskFunction(self):
        while 1:
            time.sleep(0.01)
            if self.taskBeginFlag == 1:
                self.taskBeginFlag = 0
                if self.taskID == "averageTemperature":
                    self.sensorInfo["temperature"] = random.randint(20,30)
                    self.taskFlag = 1
                elif self.taskID == "sonID":
                    self.sensorInfo["value"] = self.sonID
                    self.taskFlag = 1
                elif self.taskID == "question":
                    try:
                        value = question.taskFunction(self, self.sensorID, self.datalist)
                        self.sensorInfo["value"] = value
                        self.sendUDP("任务执行完毕")
                    except Exception, e:
                        self.sensorInfo["value"] = ""
                        self.sendUDP("任务执行出错")
                        self.sendUDP(traceback.format_exc())

                self.taskFlag = 1
                if self.sonID == []:
                    if self.parentID == self.sensorID:
                        sdata = {
                            "id": self.sensorID,
                            "info": self.sensorInfo
                        }
                        self.mesQue.append(sdata)
                        self.dataFlag = 1
                        print "The whole data has been transmitted!"
                    else:
                        sdata = {
                            "id": self.sensorID,
                            "info": self.sensorInfo
                        }
                        self.mesQue.append(sdata)
                        data = {
                            "key": "data",
                            "id": self.sensorID,
                            "data": self.mesQue
                        }
                        ndata = json.dumps(data)
                        self.send(self.parentID, ndata)
                        self.reset()
                else:
                    while self.sonFlag2 == 0:{time.sleep(0.01)}
                    sdata = {
                        "id": self.sensorID,
                        "info": self.sensorInfo
                    }
                    self.mesQue.append(sdata)
                    for ele in self.sonData:
                        for ele2 in ele:
                            self.mesQue.append(ele2)
                    if self.parentID != self.sensorID:
                        data = {
                            "key": "data",
                            "id": self.sensorID,
                            "data": self.mesQue
                        }
                        ndata = json.dumps(data)
                        self.send(self.parentID, data=ndata)
                        self.reset()
                    else:
                        self.dataFlag = 1
                        print "The whole data has been transmitted!"


    def run(self):
        #创建接口服务器
        for i in range(6):
            t = threading.Thread(target=self.createServer,args=(self.IP,self.PORT[i],))
            self.threads.append(t)
        taskServerthread = threading.Thread(target=self.taskServer,args=(self.IP,self.PORT[6],))
        taskthread = threading.Thread(target=self.taskFunction, args=())

        for i in range(6):
            self.threads[i].start()
        taskServerthread.start()
        taskthread.start()

        for i in range(6):
            self.threads[i].join()
        taskServerthread.join()
        taskthread.join()

    def shutdown(self):
        sys.exit(0)

    def reset(self):
        self.parentID = self.sensorID
        self.flag = 0
        self.sonID = []
        self.mesQue = []
        self.sonFlag = []
        self.sonFlag2 = 0
        self.sonData = []

    def transmitData(self,tmp2):
        if (self.tk % 2 == 0):
            self.tk = 1 - self.tk
            data = {
                "key": "questionData",
                "type": "value",
                "id": self.sensorID,
                "data": tmp2
            }
            ndata = json.dumps(data)
            for ele in self.IPlist:
                if ele != []:
                    self.send(ele[4], ndata)
            while self.adjFlag2 == 0: {time.sleep(0.01)}
            tmp = json.loads(json.dumps([self.adjID, self.adjData]))
            self.adjFlag2 = 0
            for i in range(len(self.adjData)):
                self.adjData[i] = []
            for i in range(len(self.adjFlag)):
                self.adjFlag[i] = 0
            return tmp
        else:
            self.tk = 1 - self.tk
            data = {
                "key": "questionData",
                "type": "feedback",
                "id": self.sensorID,
                "data": tmp2
            }
            ndata = json.dumps(data)
            for ele in self.IPlist:
                if ele != []:
                    self.send(ele[4], ndata)
            while self.adjFeedbackFlag2 == 0: {time.sleep(0.01)}
            tmp = json.loads(json.dumps([self.adjID, self.adjFeedback]))
            for i in range(len(self.adjFeedback)):
                self.adjFeedback[i] = []
            for i in range(len(self.adjFeedbackFlag)):
                self.adjFeedbackFlag[i] = 0
            self.adjFeedbackFlag2 = 0
            return tmp
            
    def syncNode(self):
        if self.tk2 == 0:   
            self.tk2 = 1 - self.tk2
            data = {
                "key": "sync",
                "id": self.sensorID
            }
            ndata = json.dumps(data)      
            for ele in self.IPlist:
                if ele != []:
                    self.send(ele[4], ndata)
            adjSyncFlag = 0
            while adjSyncFlag == 0:
                nflag1 = 1
                for ele in self.adjSyncStatus:
                    if ele == 0:
                        nflag1 = 0
                if nflag1 == 1:
                    adjSyncFlag = 1
                time.sleep(0.01)
            adjSyncFlag = 0
            for i in range(len(self.adjSyncStatus)):
                self.adjSyncStatus[i] = 0
        elif self.tk2 == 1:
            self.tk2 = 1 - self.tk2
            data = {
                "key": "sync2",
                "id": self.sensorID
            }
            ndata = json.dumps(data)
            for ele in self.IPlist:
                if ele != []:
                    self.send(ele[4], ndata)
            adjSyncFlag2 = 0
            while adjSyncFlag2 == 0:
                nflag2 = 1
                for ele in self.adjSyncStatus2:
                    if ele == 0:
                        nflag2 = 0
                if nflag2 == 1:
                    adjSyncFlag2 = 1
                time.sleep(0.01)
            adjSyncFlag2 = 0
            for i in range(len(self.adjSyncStatus2)):
                self.adjSyncStatus2[i] = 0
        return 0