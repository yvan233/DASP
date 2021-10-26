# 测试节点一个个启动，逐步接入网络的demo
# 需要把system.question的time改为10s，方便查看
# 另外需要运行.\script_to_PC\moniter.py
import json
import socket
import time 
import sys
sys.path.insert(1,".") 
from DASP.module import Node
import struct
headformat = "!2I"
headerSize = 8
def sendall_length(socket, jsondata, methods = 1):
    '''
    为发送的json数据添加methods和length报头
        POST：methods = 1: 
    '''
    body = json.dumps(jsondata)
    header = [methods, body.__len__()]
    headPack = struct.pack(headformat , *header)
    socket.sendall(headPack+body.encode())

nodelist = []
node = Node(1, False, [])
nodelist.append(node)

print("启动系统")
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
sendall_length(s, data)
s.close()


time.sleep(15)
node = Node(2, False, [])
nodelist.append(node)
print("发送连接room_2信号")
data = {
    "key": "restart",
    "GUIinfo": GUIinfo,
    "DebugMode": False, 
    "DatabaseInfo": [],
    "ObservedVariable": []
}
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((localIP, 10013))
sendall_length(s, data)
s.close()


time.sleep(15)
node = Node(3, False, [])
nodelist.append(node)
print("发送连接room_3信号")
data = {
    "key": "restart",
    "GUIinfo": GUIinfo,
    "DebugMode": False, 
    "DatabaseInfo": [],
    "ObservedVariable": []
}
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((localIP, 10020))
sendall_length(s, data)
s.close()
