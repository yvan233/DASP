# 测试多线程用短链接发消息

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


def sendone(i):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    data = [str(i)]*2000
    data = "".join(data)
    data = {"data":data}
    sendall_length(client,data)
    print('{}'.format(i))
    client.close()

host = 'localhost'
port = 8084
threads = []
for i in range(20):
    t = threading.Thread(target=sendone, args=(i,))
    threads.append(t)
for ele in threads:
    ele.start()
# while True:
#     i = i+30
#     client.sendall('{}\r\n'.format(i).encode())
#     print('{}s\r\n'.format(i))
#     time.sleep(i)
# client.close()