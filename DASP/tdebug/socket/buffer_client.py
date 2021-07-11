import socket
import time
import struct
import json

# 自定义消息头的形式，两个无符号整形，共8字节
headformat = "!2I"
# 自定义消息头的长度
headerSize = 8


host = "localhost"
port = 1234

ADDR = (host, port)
headformat = "!2I"
if __name__ == '__main__':
    client = socket.socket()
    client.connect(ADDR)

    methods = 1 # 1:POST  200: OK
    # 正常数据包定义
    body = json.dumps(dict(hello="world"))
    print(body)
    header = [methods, body.__len__()]
    headPack = struct.pack(headformat , *header)
    sendData1 = headPack+body.encode()

    # 分包数据定义
    
    body = json.dumps(dict(hello="world2"))
    print(body)
    header = [methods, body.__len__()]
    headPack = struct.pack(headformat, *header)
    sendData2_1 = headPack+body[:2].encode()
    sendData2_2 = body[2:].encode()

    # 粘包数据定义
    body1 = json.dumps(dict(hello="world3"))
    print(body1)
    cmd = 103
    header = [methods, body.__len__()]
    headPack1 = struct.pack(headformat , *header)

    body2 = json.dumps(dict(hello="world4"))
    print(body2)
    cmd = 104
    header = [methods, body.__len__()]
    headPack2 = struct.pack(headformat , *header)

    sendData3 = headPack1+body1.encode()+headPack2+body2.encode()


    # 正常数据包
    client.send(sendData1)
    time.sleep(3)

    # 分包测试
    client.send(sendData2_1)
    time.sleep(0.2)
    client.send(sendData2_2)
    time.sleep(3)

    # 粘包测试
    client.send(sendData3)
    time.sleep(3)
    client.close()
