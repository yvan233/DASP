import socket
import sys
import threading
import time
sys.path.insert(1,".")  # 把上一级目录加入搜索路径
from DASP.module import DaspCommon, TaskServer, CommServer

class Server(object):
    def __init__(self, ID, GUIinfo, adjID, adjDirection, adjDirectionOtherSide, IPlist,IP,PORT,datalist):
        DaspCommon.nodeID = ID
        DaspCommon.GUIinfo = GUIinfo
        DaspCommon.IP = socket.gethostbyname(IP)
        DaspCommon.PORT = PORT
        DaspCommon.adjID = adjID
        DaspCommon.adjDirection = adjDirection
        DaspCommon.adjDirectionOtherSide = adjDirectionOtherSide
        DaspCommon.IPlist = IPlist

    def run(self):
        #创建接口服务器
        self.commServerThread = []
        for _,port in enumerate(DaspCommon.PORT[1:]):
            commserver = CommServer(DaspCommon.IP, port)
            t = threading.Thread(target=commserver.run,args=())
            self.commServerThread.append(t)

        taskserver = TaskServer(DaspCommon.IP,DaspCommon.PORT[0])
        self.taskServerThread = threading.Thread(target=taskserver.run,args=())
        self.systemTaskThread = threading.Thread(target=taskserver.systemtask,args=())

        for _,thread in enumerate(self.commServerThread):
            thread.start()
        self.taskServerThread.start()
        self.systemTaskThread.start()



        

