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

DAPPnamelist = ["TimeSynch"]

for ele in DAPPnamelist:
    localIP = socket.gethostbyname(socket.gethostname())
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((localIP, 10083))
    data = {
        "key": "newtask",
        "DAPPname": ele,
        "DebugMode": False, 
        "DatabaseInfo": [],
        "ObservedVariable": []
    }
    sendall_length(s, data)
    s.close()