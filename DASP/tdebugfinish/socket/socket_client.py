
import socket
import time
host = 'localhost'
port = 8084

def sendall_length(socket, head, data):
    '''
    为发送数据添加length报头
    '''
    length = "content-length:"+str(len(data)) + "\r\n\r\n"
    message = head + length + data
    socket.sendall(str.encode(message))


from struct import pack
a = pack('i',12)
print("i12".encode())

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1) #在客户端开启心跳维护
client.ioctl(socket.SIO_KEEPALIVE_VALS,(1,60*1000,30*1000)) #开始保活机制，60s后没反应开始探测连接，30s探测一次，一共探测10次，失败则断开
client.connect((host, port))
i = 0
while True:
    i = i+1
    data = [str(i)]*2000
    data = "".join(data)
    client.sendall('{}'.format(data).encode())
    # client.sendall('{}\r\n'.format(i).encode())
    print('{}\r\n'.format(i))
    # time.sleep(i)
client.close()