import socket
class DspFuncMixin():
    '''
    Dsp基础方法混合
    '''
    def __init__(self):
        pass
    def sendall_length(self, s, head, data):
        '''
        为发送数据添加length报头
        '''
        length = "content-length:"+str(len(data)) + "\r\n\r\n"
        message = head + length + data
        s.sendall(str.encode(message))

    def recv_length(self, conn):
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