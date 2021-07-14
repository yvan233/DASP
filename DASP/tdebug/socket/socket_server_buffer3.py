# 长连接断开检测


from inspect import Traceback
import socket
import json
import struct
import traceback
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
    """
    数据处理函数
    """
    if headPack[0] == 1:
        print(body)
        pass
    else:
        print("非POST方法")

def DisconnectHandle(addr):
    """
    对邻居断开连接的操作函数               
    """
    print (addr , "已断开")

def recv_long_conn(host, port):
    """
    长连接循环接收数据框架
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1) #接收的连接数
    conn, addr = server.accept()
    print(addr , "已连接")
    # FIFO消息队列
    dataBuffer = bytes()
    with conn:
        while True:
            try:
                data = conn.recv(1024)
            except Exception as e:
                # 发送端进程被杀掉
                DisconnectHandle(addr)
                break

            if data == b"":
                DisconnectHandle(addr)
                break
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
    
host = 'localhost'
port = 8084
while True:
    recv_long_conn(host, port)
