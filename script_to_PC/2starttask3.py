import os
import json
import socket

def sendall_length(s, head, data):
    length = "content-length:"+str(len(data)) + "\r\n\r\n"
    message = head + length + data
    s.sendall(str.encode(message))
    
tasknumlist = [4]
delaylist = [0]

for i in range(len(tasknumlist)):
    localIP = socket.gethostbyname(socket.gethostname())
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((localIP, 10006))
    GUIinfo = [localIP, 50000]
    data = {
        "key": "newtask",
        "GUIinfo": GUIinfo,
        "tasknum": tasknumlist[i],
        "delay": delaylist[i]
    }
    data = json.dumps(data)
    head = "POST / HTTP/1.1\r\n"
    sendall_length(s, head, data)
    s.close()