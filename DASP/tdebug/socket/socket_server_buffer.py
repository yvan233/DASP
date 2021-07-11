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
        print(headPack)
        pass
    else:
        print("非POST方法")


def recv_func(conn):
    '''
    print('Connected by', addr)
    循环接收数据框架
    '''
    # FIFO消息队列
    i = 0
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
                    i = i+1
                    print (i)
                    # 数据出列
                    dataBuffer = dataBuffer[headerSize+bodySize:] # 获取下一个数据包，类似于把数据pop出
    
host = 'localhost'
port = 8084
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(1) #接收的连接数
client, address = server.accept() #因为设置了接收连接数为1，所以不需要放在循环中接收
print('Connected by', address)
recv_func(client)