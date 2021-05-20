import json
import socket
import sys
import time
import threading

sys.path.insert(1,".")  # 把上一级目录加入搜索路径
from IoT.system.common import DaspFuncMixin

class CommServer(DaspFuncMixin):
    """
    通信服务器，用于节点和其他节点通信
    """
    host = "locolhost"
    port = 10000

    def __init__(self,host,port):
        self.host = host
        self.port = port

    def run(self):
        cont = """HTTP/1.1 200 OK\r\n"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(100)
        print ("Server on " + self.host + ":" + str(self.port))

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
                            print (self.host + ":" + str(self.port) + " connected to " + jdata["host"] + ":" + str(jdata["port"]))
                            self.GUIinfo = jdata["GUIinfo"]
                            data = {
                                "key": "connect",
                                "host": self.host,
                                "port": self.port,
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
                                "host": self.host,
                                "port": self.port,
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