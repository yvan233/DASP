import json
import socket
import sys
import time
import threading

sys.path.append(".")  # 把上一级目录加入搜索路径
from IoT.system.common import DspFuncMixin
class TaskServer(DspFuncMixin):
    """
    外部交互服务器，用于节点和外部交互
    """
    host = "locolhost"
    port = 0
    def __init__(self,host,port):
        self.host = host
        self.port = port

    def run(self):
        cont = """HTTP/1.1 200 OK\r\n"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(100)
        print ("TaskServer: " + self.host + ":" + str(self.port))

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