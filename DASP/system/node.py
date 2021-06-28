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
from DASP.system.common import DaspFuncMixin

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
