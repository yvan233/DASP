import socket
import ctypes
import inspect
import json
import sys
import time
import threading

class DaspFuncMixin():
    '''
    Dsp基础方法混合
    '''
    def __init__(self):
        pass

    def sendall_length(self, socket, head, data):
        '''
        为发送数据添加length报头
        '''
        length = "content-length:"+str(len(data)) + "\r\n\r\n"
        message = head + length + data
        socket.sendall(str.encode(message))

    def recv_length(self, conn):
        '''
        循环接收数据，直到收完报头中length长度的数据
        '''
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

    def _async_raise(self, tid, exctype):
        '''
        主动抛出异常
        '''
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
        '''
        强制停止某个线程
        '''
        self._async_raise(thread.ident, SystemExit)


class BaseServer(DaspFuncMixin):
    '''基础服务器

    Dsp基础服务器

    '''
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


class TaskServer(BaseServer):
    """外部交互服务器
    
    用于节点和外部交互
    
    属性:
        host: 绑定IP
        port: 绑定port
        GUIinfo: GUI的ip和端口
    """
    host = "127.0.0.1"
    port = 10000
    GUIinfo = ["127.0.0.1",50000] 

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
        print ("TaskServer: " + self.host + ":" + str(self.port))

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
                            self.GUIinfo = jdata["GUIinfo"]
                            self.sendUDP("接收任务请求")
                        except KeyError:
                            print ("非来自GUI的任务请求")
                        self.startsystem()

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
                        self.taskthreads[num].startsystem()
                        starttaskthread = threading.Thread(target=self.starttask,args=(num, delay ,))
                        starttaskthread.startsystem()

                        if self.waitflag == 0:
                            waitend = threading.Thread(target=self.waitforend,args=())
                            waitend.startsystem()
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
                        waitend.startsystem()
                        self.waitflag = 1

                    else:
                        conn.send(str.encode(head + "您输入的任务信息有误！"))
            else:
                conn.send(str.encode(head + "暂未提供POST以外的接口"))
            conn.close()

    def startsystem(self):
        """
        启动系统
        """
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
            "key": "startsystem",
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
        head = """HTTP/1.1 200 OK\r\n"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(100)
        print ("Server on " + self.host + ":" + str(self.port))

        while 1:
            conn, addr = sock.accept()
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
                            self.sendall_length(conn, head, ndata)
                            
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
                            self.sendall_length(conn, head, mdata)

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

                    # startsystem Distribution
                    elif jdata["key"] == "startsystem":
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
                        self.taskthreads[num].startsystem()
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
                            conn.send(str.encode(head + "节点"+str(self.sensorID)+"方向"+str(jdata["applydirection"])+"已被占用，请选择其他方向！"))

                    else:
                        conn.send(str.encode(head+"请不要直接访问通信服务器"))
            else:
                conn.send(str.encode(head + "请不要直接访问通信服务器"))
            conn.close()


if __name__ == '__main__':
    IP = "localhost"
    PORT = 10000