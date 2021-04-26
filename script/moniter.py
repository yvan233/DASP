import socket
import json

def recv_length(conn):
    request = conn.recv(1024)
    message = bytes.decode(request)
    message_split = message.split('\r\n')
    content_length = message_split[1][15:]
    message_length =  len(message_split[0]) + len(message_split[1]) \
        + 2*(len(message_split)-1) + int(content_length)
    while True:
        if len(message) < message_length:
            request = conn.recv(1024)
            message += bytes.decode(request)
        else:
            break
    return message
    
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
localIP = socket.gethostbyname(socket.gethostname())
s.bind((localIP, 50000))
while 1:
    try:
        data, addr = s.recvfrom(100000000)
        jdata = json.loads(data)
    except Exception:
        print ("接收数据出错")
    else:
        if jdata["key"] == "runData":
            print("task"+str(jdata["tasknum"]) + "-Node " + str(jdata["id"]) + ": " + jdata["info"])
        elif jdata["key"] == "endData":
            print(jdata["info"])
        elif jdata["key"] == "runFlag":
            # print(str(jdata["tasknum"]) +str(jdata["info"]))
            pass
        else:
            print ("数据有误")
s.close()

