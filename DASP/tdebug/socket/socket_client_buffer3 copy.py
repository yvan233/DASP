# 长连接断开检测

import socket
import struct
import time
import threading
import json
# 自定义消息头的形式，两个无符号整形，共8字节
headformat = "!2I"
# 自定义消息头的长度
headerSize = 8


def sendall_length(socket, jsondata, methods = 1):
    """
    为发送数据添加methods和length报头
    methods: 1:POST
    """
    body = json.dumps(jsondata)
    header = [methods, body.__len__()]
    headPack = struct.pack(headformat , *header)
    socket.sendall(headPack+body.encode())

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

def sendone(sock, i):
    data = [str(i)]*2000
    data = "".join(data)
    data = {"data":data}
    print('{}'.format(i))
    sendall_length(sock,data)
    # client.close()

print ("非心跳机制")
host = 'localhost'
port = 8085
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1) #在客户端开启心跳维护
# client.ioctl(socket.SIO_KEEPALIVE_VALS,(1,1*1000,1*1000)) #开始保活机制，60s后没反应开始探测连接，30s探测一次，一共探测10次，失败则断开
client.connect((host, port))
threads = []
print("connect")
sendone(client,1)
headPack,body = recv_length(client)
print(body)
time.sleep(10)
# sendone(client,2)