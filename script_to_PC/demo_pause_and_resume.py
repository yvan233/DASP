# 测试任务的暂停和恢复功能
# 另外需要运行.\script_to_PC\moniter.py   
# .\DASP\start.bat 12
# .\script_to_PC\1run.py

import json
import socket
import time 
def sendall_length(s, head, data):
    length = "content-length:"+str(len(data)) + "\r\n\r\n"
    message = head + length + data
    s.sendall(str.encode(message))


print("开始任务")
localIP = socket.gethostbyname(socket.gethostname())
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((localIP, 10006))
data = {
    "key": "newtask",
    "DAPPname": "testpause",
}
data = json.dumps(data)
head = "POST / HTTP/1.1\r\n"
sendall_length(s, head, data)
s.close()

time.sleep(5)
print("发送pause信号")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((localIP, 10006))
data = {
    "key": "pausetask",
    "DAPPname": "testpause",
}
data = json.dumps(data)
sendall_length(s, head, data)
s.close()


time.sleep(5)
print("发送resume信号")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((localIP, 10006))
data = {
    "key": "resumetask",
    "DAPPname": "testpause",
}
data = json.dumps(data)
sendall_length(s, head, data)
s.close()

time.sleep(5)
print("发送终止信号")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((localIP, 10006))
data = {
    "key": "shutdowntask",
    "DAPPname": "testpause",
}
data = json.dumps(data)
sendall_length(s, head, data)
s.close()