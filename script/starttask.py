import csv
import os
import json
import socket
import sys

remoteID = sys.argv[1]
# remoteIP = sys.argv[1]
path = os.getcwd() + "\\IoT\\binding.csv"
with open(path,'r')as f:
    data = csv.reader(f)
    idiplist = []
    for i in data:
        idiplist.append(i)
for ele in idiplist[1:]:
    if ele[0] == remoteID:
        remoteIP = ele[1]
        break
tasknumlist = [int(val) for val in sys.argv[2].split(',')]
delaylist = [int(val) for val in sys.argv[3].split(',')]

for i in range(len(tasknumlist)):
    localIP = socket.gethostbyname(socket.gethostname())
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((remoteIP, 10006))
    GUIinfo = [localIP, 50000]
    data = {
        "key": "newtask",
        "GUIinfo": GUIinfo,
        "tasknum": tasknumlist[i],
        "delay": delaylist[i]
    }
    print(data)
    data = json.dumps(data)
    message = "POST / HTTP/1.1\r\n\r\n"
    message += data
    s.sendall(str.encode(message))
    s.close()