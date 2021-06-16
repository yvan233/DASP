import os
import json
import socket
import sys

def sendall_length(s, head, data):
    length = "content-length:"+str(len(data)) + "\r\n\r\n"
    message = head + length + data
    s.sendall(str.encode(message))
    
port = int(sys.argv[1])

localIP = socket.gethostbyname(socket.gethostname())
GUIinfo = [localIP, 50000]
data = {
    "key": "restart",
    "GUIinfo": GUIinfo
}
data = json.dumps(data)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((localIP, port))
head = "POST / HTTP/1.1\r\n"
sendall_length(s, head, data)
s.close()