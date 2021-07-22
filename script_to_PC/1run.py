import json
import socket
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
