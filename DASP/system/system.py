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
        self.CommServerThread = []
        for i,port in enumerate(DaspCommon.PORT[1:]):
            commserver = CommServer(DaspCommon.IP, port)
            t = threading.Thread(target=commserver.run,args=())
            self.CommServerThread.append(t)

        taskserver = TaskServer(DaspCommon.IP,DaspCommon.PORT[0])
        self.TaskServerThread = threading.Thread(target=taskserver.run,args=())
        self.SystemTaskThread = threading.Thread(target=taskserver.systemtask,args=())

        for i,thread in enumerate(self.CommServerThread):
            thread.start()
        self.TaskServerThread.start()
        self.SystemTaskThread.start()



        

