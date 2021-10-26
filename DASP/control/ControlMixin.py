import json
import socket
import struct
import os
import codecs
class ControlMixin():
    '''DASP控制函数混合
    '''
    headformat = "!2I"
    headerSize = 8
    Databaseinfo = {
        'host': "127.0.0.1",
        'port': 3306,
        'user': 'root',
        'password': 'DSPadmin',
    }
    
    def __init__(self):
        path = os.getcwd() + "/DASP/task_info/system/topology.txt"
        path = path.replace('\\', '/')  
        text = codecs.open(path, 'r', 'utf-8').read()
        js = json.loads(text)
        self.TaskPort = {}
        for ele in js:
            if "ID" in ele:
                self.TaskPort[ele["ID"]] = ele["PORT"][6]


    def sendall_length(self, socket, jsondata, methods = 1):
        '''
        为发送的json数据添加methods和length报头
            POST：methods = 1: 
        '''
        body = json.dumps(jsondata)
        header = [methods, body.__len__()]
        headPack = struct.pack(self.headformat , *header)
        socket.sendall(headPack+body.encode())

    def RunSystem(self, nodeID):
        '''
        启动系统，运行系统自检算法
        '''
        localIP = socket.gethostbyname(socket.gethostname())
        GUIinfo = [localIP, 50000]
        data = {
            "key": "startsystem",
            "GUIinfo": GUIinfo,
            "DebugMode": False, 
            "DatabaseInfo": [],
            "ObservedVariable": []
        }
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((localIP, 10006))
        self.sendall_length(s, data)
        s.close()

    def StartTask(self, DAPPname):
        '''
        运行指定名称的DAPP
        '''
        localIP = socket.gethostbyname(socket.gethostname())
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((localIP, 10006))
        data = {
            "key": "newtask",
            "DAPPname": DAPPname,
            "DebugMode": False, 
            "DatabaseInfo": [],
            "ObservedVariable": []
        }
        self.sendall_length(s, data)
        s.close()

    def StartTaskList(self, DAPPnamelist = []):
        '''
        运行指定名称的DAPP列表
        '''
        if DAPPnamelist:
            for ele in DAPPnamelist:
                self.StartTask(ele)

    def StartTaskDebug(self, DAPPname, DatabaseInfo = Databaseinfo, ObservedVariable = []):
        '''
        调试模式运行指定名称的DAPP
        '''
        localIP = socket.gethostbyname(socket.gethostname())
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((localIP, 10006))
        data = {
            "key": "newtask",
            "DAPPname": DAPPname,
            "DebugMode": True, 
            "DatabaseInfo": DatabaseInfo,
            "ObservedVariable": ObservedVariable
        }
        self.sendall_length(s, data)
        s.close()

    def StopTask(self, DAPPname):
        '''
        停止运行指定名称的DAPP
        '''
        localIP = socket.gethostbyname(socket.gethostname())
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((localIP, 10006))
        data = {
            "key": "shutdowntask",
            "DAPPname": DAPPname
        }
        self.sendall_length(s, data)
        s.close()

    def reconnect(self):
        localIP = socket.gethostbyname(socket.gethostname())
        GUIinfo = [localIP, 50000]
        data = {
            "key": "restart",
            "GUIinfo": GUIinfo,
            "DebugMode": False, 
            "DatabaseInfo": [],
            "ObservedVariable": []
        }
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((localIP, 10013))
        self.sendall_length(s, data)
        s.close()

