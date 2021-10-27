import socket
import sys
import threading
sys.path.insert(1,".")  # 把上一级目录加入搜索路径
from DASP.module import DaspCommon, TaskServer, CommServer

class Server(object):
    def __init__(self, ID, adjID, adjDirection, adjDirectionOtherSide, IPlist,IP,PORT,datalist):
        DaspCommon.nodeID = ID
        DaspCommon.IP = socket.gethostbyname(IP)
        DaspCommon.PORT = PORT
        DaspCommon.adjID = adjID
        DaspCommon.adjDirection = adjDirection
        DaspCommon.adjDirectionOtherSide = adjDirectionOtherSide
        DaspCommon.IPlist = IPlist

    def run(self):
        #创建接口服务器
        self.CommServerThread = []
        for i in range(6):
            commserver = CommServer(DaspCommon.IP,DaspCommon.PORT[i])
            t = threading.Thread(target=commserver.run,args=())
            self.CommServerThread.append(t)

        taskserver = TaskServer(DaspCommon.IP,DaspCommon.PORT[6])
        self.TaskServerThread = threading.Thread(target=taskserver.run,args=())
        
        # t = threading.Thread(target=self.taskFunction, args=(0,))
        # self.taskthreads.append(t)

        for i in range(6):
            self.CommServerThread[i].start()
        self.TaskServerThread.start()
        # self.taskthreads[0].start()

