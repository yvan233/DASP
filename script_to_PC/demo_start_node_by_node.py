# 测试节点一个个启动，逐步接入网络的demo
# 需要把system.question的time改为10s，方便查看
# 另外需要运行.\script_to_PC\moniter.py
import json
import socket
import time 
import sys
sys.path.insert(1,".") 
from DASP.module import Node

def sendall_length(s, head, data):
    length = "content-length:"+str(len(data)) + "\r\n\r\n"
    message = head + length + data
    s.sendall(str.encode(message))

nodelist = []
node = Node(1, False, [])
nodelist.append(node)

print("启动系统")
localIP = socket.gethostbyname(socket.gethostname())
GUIinfo = [localIP, 50000]
data = {
    "key": "startsystem",
    "GUIinfo": GUIinfo
}
data = json.dumps(data)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((localIP, 10006))
head = "POST / HTTP/1.1\r\n"
sendall_length(s, head, data)
s.close()


time.sleep(15)
node = Node(2, False, [])
nodelist.append(node)
print("发送连接room_2信号")
data = {
    "key": "restart",
    "GUIinfo": GUIinfo
}
data = json.dumps(data)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((localIP, 10013))
head = "POST / HTTP/1.1\r\n"
sendall_length(s, head, data)
s.close()


time.sleep(15)
node = Node(3, False, [])
nodelist.append(node)
print("发送连接room_3信号")
data = {
    "key": "restart",
    "GUIinfo": GUIinfo
}
data = json.dumps(data)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((localIP, 10020))
head = "POST / HTTP/1.1\r\n"
sendall_length(s, head, data)
s.close()

"""
[room_1]system: 接收任务请求
[room_1]system: 与邻居节点room_2连接失败
[room_1]system: 与邻居节点room_4连接失败
[room_1]system: 通信树建立完成
[room_1]system: 开始执行
[room_1]system: 系统第1次自检：本节点与所有邻居通信正常，当前邻居节点：[]
[room_1]system: 系统第2次自检：本节点与所有邻居通信正常，当前邻居节点：[]
[room_2]system: 重新连入系统
[room_1]system: 与邻居节点room_2重连成功，已添加和room_2的连接
[room_2]system: 与邻居节点room_3连接失败
[room_2]system: 与邻居节点room_5连接失败
[room_2]system: 开始执行
[room_2]system: 系统第1次自检：本节点与所有邻居通信正常，当前邻居节点：['room_1']
[room_1]system: 系统第3次自检：本节点与所有邻居通信正常，当前邻居节点：['room_2']
[room_2]system: 系统第2次自检：本节点与所有邻居通信正常，当前邻居节点：['room_1']
[room_3]system: 重新连入系统
[room_2]system: 与邻居节点room_3重连成功，已添加和room_3的连接
[room_3]system: 与邻居节点room_6连接失败
[room_1]system: 系统第4次自检：本节点与所有邻居通信正常，当前邻居节点：['room_2']
[room_3]system: 与邻居节点pump_1连接失败
[room_3]system: 开始执行
[room_3]system: 系统第1次自检：本节点与所有邻居通信正常，当前邻居节点：['room_2']
[room_2]system: 系统第3次自检：本节点与所有邻居通信正常，当前邻居节点：['room_1', 'room_3'] 
"""