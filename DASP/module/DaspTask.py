import json
import socket
import sys
import time
import threading


class TaskFunction():
    """
    外部交互服务器，用于节点和外部交互
    """
    host = "locolhost"
    port = 10000
    def __init__(self,host,port):
        self.host = host
        self.port = port


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


class DataFunction():
    """
    外部交互服务器，用于节点和外部交互
    """
    host = "locolhost"
    port = 10000

    def __init__(self,host,port):
        self.host = host
        self.port = port


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
