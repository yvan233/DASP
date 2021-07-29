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
    else:
        print("非POST方法")

def recv_length(conn):
    '''
    循环接收数据，直到收完报头中length长度的数据
    '''
    dataBuffer = bytes()
    while True:
        data = conn.recv(1024)
        # if data == b"":
        #     break
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
                body = dataBuffer[headerSize:headerSize+bodySize]
                body = body.decode()
                return headPack,body


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
        headPack,body = recv_length(conn)
        conn.close()
        dataHandle(headPack,body)
                        

host = 'localhost'
port = 8084
recv_short_conn(host,port)