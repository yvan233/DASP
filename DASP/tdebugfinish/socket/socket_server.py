import socket
def recv_length(conn):
    '''
    循环接收数据，直到收完报头中length长度的数据
    '''
    request = conn.recv(1024)
    message = bytes.decode(request)
    message_split = message.split('\r\n')
    content_length = message_split[1][15:]
    message_length =  len(message_split[0]) + len(message_split[1]) + 2*(len(message_split)-1) + int(content_length)
    while True:
        if len(message) < message_length:
            request = conn.recv(1024)
            message += bytes.decode(request)
        else:
            break
    return message
    
host = 'localhost'
port = 8084
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(1) #接收的连接数
client, address = server.accept() #因为设置了接收连接数为1，所以不需要放在循环中接收
while True: #循环收发数据包，长连接
    data = client.recv(1024)
    if data:
        print(data.decode()) #python3 要使用decode
    # client.close() #连接不断开，长连接