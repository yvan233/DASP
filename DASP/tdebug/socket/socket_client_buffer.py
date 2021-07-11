# 测试多线程用长链接发消息
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


def recv_func(conn):
    '''
    print('Connected by', addr)
    循环接收数据框架
    '''
    # FIFO消息队列
    dataBuffer = bytes()
    with conn:
        while True:
            data = conn.recv(1024)
            if data:
                # 把数据存入缓冲区，类似于push数据
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
                    # 数据处理
                    dataHandle(headPack, body)

                    # 数据出列
                    dataBuffer = dataBuffer[headerSize+bodySize:] # 获取下一个数据包，类似于把数据pop出


def sendone(sock, i):
    data = [str(i)]*2000
    data = "".join(data)
    data = {"data":data}
    sendall_length(sock,data)
    print('{}'.format(i))
    # client.close()

host = 'localhost'
port = 8084
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1) #在客户端开启心跳维护
client.ioctl(socket.SIO_KEEPALIVE_VALS,(1,60*1000,30*1000)) #开始保活机制，60s后没反应开始探测连接，30s探测一次，一共探测10次，失败则断开
client.connect((host, port))
threads = []
for i in range(100):
    t = threading.Thread(target=sendone, args=(client,i))
    threads.append(t)
for ele in threads:
    ele.start()
# while True:
#     i = i+30
#     client.sendall('{}\r\n'.format(i).encode())
#     print('{}s\r\n'.format(i))
#     time.sleep(i)
# client.close()