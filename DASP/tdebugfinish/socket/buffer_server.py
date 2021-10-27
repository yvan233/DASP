import socket
import struct

HOST = 'localhost'
PORT = 1234





# 定义数据包的个数
sn = 0
headformat = "!2I"
# 自定义消息头的长度
headerSize = 8

# 正文数据处理
def dataHandle(headPack, body):
    global sn
    sn += 1
    print(f"第{sn}个数据包")
    print(body.decode())
    print("\n")


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if data:
                    # 把数据存入缓冲区，类似于push数据
                    dataBuffer += data
                    while True:
                        if len(dataBuffer) < headerSize:
                            print("数据包（%s Byte）小于消息头部长度，跳出小循环" % len(dataBuffer))
                            break

                        # 读取包头
                        # struct中:!代表Network order，3I代表3个unsigned int数据
                        headPack = struct.unpack(headformat, dataBuffer[:headerSize])
                        bodySize = headPack[1]

                        # 分包情况处理，跳出函数继续接收数据
                        if len(dataBuffer) < headerSize+bodySize :
                            print("数据包（%s Byte）不完整（总共%s Byte），跳出小循环" % (len(dataBuffer), headerSize+bodySize))
                            break

                        # 读取消息正文的内容
                        body = dataBuffer[headerSize:headerSize+bodySize]

                        # 数据处理
                        dataHandle(headPack, body)

                        # 数据出列
                        dataBuffer = dataBuffer[headerSize+bodySize:] # 获取下一个数据包，类似于把数据pop出