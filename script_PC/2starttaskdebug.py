import json
import socket
import struct
headformat = "!2I"
headerSize = 8
DatabaseInfo = {
    'host': "127.0.0.1",
    'port': 3306,
    'user': 'root',
    'password': 'DSPadmin',
 }
ObservedVariable = ["m","adjData_fb","data"]

def sendall_length(socket, jsondata, methods = 1):
    '''
    为发送的json数据添加methods和length报头
        POST：methods = 1: 
    '''
    body = json.dumps(jsondata)
    header = [methods, body.__len__()]
    headPack = struct.pack(headformat , *header)
    socket.sendall(headPack+body.encode())

DAPPnamelist = ["CreatBFStree"]

for ele in DAPPnamelist:
    localIP = socket.gethostbyname(socket.gethostname())
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((localIP, 10006))
    data = {
        "key": "newtask",
        "DAPPname": ele,
        "DebugMode": True, 
        "DatabaseInfo": DatabaseInfo,
        "ObservedVariable": ObservedVariable
    }
    sendall_length(s, data)
    s.close()