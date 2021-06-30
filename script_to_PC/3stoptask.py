import os
import json
import socket

def sendall_length(s, head, data):
    length = "content-length:"+str(len(data)) + "\r\n\r\n"
    message = head + length + data
    s.sendall(str.encode(message))



localIP = socket.gethostbyname(socket.gethostname())
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((localIP, 10006))
data = {
    "key": "shutdowntask",
    "DAPPname": "CreatBFStree",
}
data = json.dumps(data)
head = "POST / HTTP/1.1\r\n"
sendall_length(s, head, data)
s.close()