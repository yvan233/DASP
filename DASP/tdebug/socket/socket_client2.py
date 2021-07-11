# 测试多线程用长链接发消息
import socket
import time
import threading


def sendone(sock, i):
    data = [str(i)]*2000
    data = "".join(data)
    sock.sendall('{}'.format(data).encode())
    print('{}s\r\n'.format(i))
    # client.close()

host = 'localhost'
port = 8084
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1) #在客户端开启心跳维护
client.ioctl(socket.SIO_KEEPALIVE_VALS,(1,60*1000,30*1000)) #开始保活机制，60s后没反应开始探测连接，30s探测一次，一共探测10次，失败则断开
client.connect((host, port))
threads = []
for i in range(10):
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