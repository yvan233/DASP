import json
import socket
import struct
import os
import codecs
import csv
class ControlMixin():
    '''DASP控制函数混合

    mode = "Pc":Pc上仿真运行
    mode = "PI":树莓派上实际运行
    '''
    headformat = "!2I"
    headerSize = 8
    Databaseinfo = {
        'host': "127.0.0.1",
        'port': 3306,
        'user': 'root',
        'password': 'DSPadmin',
    }
    
    def __init__(self, mode):
        
        path = os.getcwd() + "/DASP/task_info/system/topology.txt"
        path = path.replace('\\', '/')  
        text = codecs.open(path, 'r', 'utf-8').read()
        js = json.loads(text)
        self.localIP = socket.gethostbyname(socket.gethostname())
        self.TaskPortDict = {}
        self.IPDict = {}
        for ele in js:
            if "ID" in ele:
                self.TaskPortDict[ele["ID"]] = ele["PORT"][6]
                self.IPDict[ele["ID"]] = self.localIP
        if mode == "PI":
            path = os.getcwd() + "/DASP/system/binding.csv"
            # 读取节点信息
            with open(path,'r')as f:
                data = csv.reader(f)
                for ele in data:
                    self.TaskPortDict[ele[0]] = 10006
                    self.IPDict[ele[0]] = ele[1]
                    

    def sendall_length(self, socket, jsondata, methods = 1):
        '''为发送的json数据添加methods和length报头
            POST：methods = 1: 
        '''
        body = json.dumps(jsondata)
        header = [methods, body.__len__()]
        headPack = struct.pack(self.headformat , *header)
        socket.sendall(headPack+body.encode())

    def RunSystem(self, nodeID):
        '''
        以nodeID为根节点启动系统，运行系统自检算法
        '''
        GUIinfo = [self.localIP, 50000]
        data = {
            "key": "startsystem",
            "GUIinfo": GUIinfo,
            "DebugMode": False, 
            "DatabaseInfo": [],
            "ObservedVariable": []
        }
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.IPDict[nodeID], self.TaskPortDict[nodeID]))
        self.sendall_length(s, data)
        s.close()

    def StartTask(self, DAPPname, nodeID):
        '''
        以nodeID为根节点运行指定名称的DAPP
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(((self.IPDict[nodeID], self.TaskPortDict[nodeID])))
        data = {
            "key": "newtask",
            "DAPPname": DAPPname,
            "DebugMode": False, 
            "DatabaseInfo": [],
            "ObservedVariable": []
        }
        self.sendall_length(s, data)
        s.close()

    def StartTaskList(self, DAPPnamelist, nodeID):
        '''
        以nodeID为根节点运行指定名称的DAPP列表
        '''
        if DAPPnamelist:
            for ele in DAPPnamelist:
                self.StartTask(ele, nodeID)

    def StartTaskDebug(self, DAPPname, nodeID, DatabaseInfo = Databaseinfo, ObservedVariable = []):
        '''
        以nodeID为根节点调试模式运行指定名称的DAPP
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.IPDict[nodeID], self.TaskPortDict[nodeID]))
        data = {
            "key": "newtask",
            "DAPPname": DAPPname,
            "DebugMode": True, 
            "DatabaseInfo": DatabaseInfo,
            "ObservedVariable": ObservedVariable
        }
        self.sendall_length(s, data)
        s.close()

    def PauseTask(self, DAPPname, nodeID):
        '''
        以nodeID为根节点暂停运行指定名称的DAPP
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.IPDict[nodeID], self.TaskPortDict[nodeID]))
        data = {
            "key": "pausetask",
            "DAPPname": DAPPname
        }
        self.sendall_length(s, data)
        s.close()

    def ResumeTask(self, DAPPname, nodeID):
        '''
        以nodeID为根节点恢复运行指定名称的DAPP
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.IPDict[nodeID], self.TaskPortDict[nodeID]))
        data = {
            "key": "resumetask",
            "DAPPname": DAPPname
        }
        self.sendall_length(s, data)
        s.close()

    def StopTask(self, DAPPname, nodeID):
        '''
        以nodeID为根节点停止运行指定名称的DAPP
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.IPDict[nodeID], self.TaskPortDict[nodeID]))
        data = {
            "key": "shutdowntask",
            "DAPPname": DAPPname
        }
        self.sendall_length(s, data)
        s.close()

    def reconnect(self, nodeID):
        '''
        使断开连接的nodeID重连到系统中
        '''
        GUIinfo = [self.localIP, 50000]
        data = {
            "key": "restart",
            "GUIinfo": GUIinfo,
            "DebugMode": False, 
            "DatabaseInfo": [],
            "ObservedVariable": []
        }
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.IPDict[nodeID], self.TaskPortDict[nodeID]))
        self.sendall_length(s, data)
        s.close()

if __name__ == '__main__':
    ControlMixin = ControlMixin(mode = "Pc")
    print(ControlMixin.IPDict)