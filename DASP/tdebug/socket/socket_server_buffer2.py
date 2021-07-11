# 短连接测试收数


import socket
import json
import struct
headformat = "!2I"
# 自定义消息头的长度
headerSize = 8



def sendall_length(socket, jsondata, methods = 1):
    '''
    为发送数据添加methods和length报头
    methods: 1:POST
    '''
    body = json.dumps(jsondata)
    header = [methods, body.__len__()]
    headPack = struct.pack(headformat , *header)
    socket.sendall(headPack+body.encode())


def dataHandle(headPack, body):

    if headPack[0] == 1:
        print(body)
        pass
    else:
        print("非POST方法")



def recv_short_conn(host, port):
    '''
    短连接循环接收数据框架
    '''   

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(100) #接收的连接数

    while 1:
        conn, addr = server.accept()
        print('Connected by', addr)
        # Byte消息
        dataBuffer = bytes()
        body = None
        with conn:
            while True:
                data = conn.recv(1024)
                if data:
                    dataBuffer += data
                    while True:
                        if len(dataBuffer) < headerSize:
                            break  #数据包小于消息头部长度，跳出小循环
                        # 读取包头
                        headPack = struct.unpack(headformat, dataBuffer[:headerSize])
                        bodySize = headPack[1]
                        if len(dataBuffer) < headerSize+bodySize :
                            break  #数据包不完整，跳出小循环
                        # 读取消息正文的内容
                        body = dataBuffer[headerSize:headerSize+bodySize]
                        body = body.decode()
                        dataHandle(headPack, body)
                        break
                if body != None:
                    break
                        

host = 'localhost'
port = 8084
recv_short_conn(host,port)