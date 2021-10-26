# 测试任务的暂停和恢复功能
# 另外需要运行.\script_to_PC\moniter.py   
# .\DASP\start.bat 12
# .\script_to_PC\1run.py

import json
import socket
import time 
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

print("开始任务")
localIP = socket.gethostbyname(socket.gethostname())
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((localIP, 10006))
data = {
    "key": "newtask",
    "DAPPname": "testpause",
    "DebugMode": False, 
    "DatabaseInfo": [],
    "ObservedVariable": []
}
sendall_length(s, data)
s.close()

time.sleep(5)
print("发送pause信号")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((localIP, 10006))
data = {
    "key": "pausetask",
    "DAPPname": "testpause",
}

sendall_length(s, data)
s.close()


time.sleep(5)
print("发送resume信号")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((localIP, 10006))
data = {
    "key": "resumetask",
    "DAPPname": "testpause",
}
sendall_length(s, data)
s.close()

time.sleep(5)
print("发送终止信号")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((localIP, 10006))
data = {
    "key": "shutdowntask",
    "DAPPname": "testpause",
}
sendall_length(s, data)
s.close()