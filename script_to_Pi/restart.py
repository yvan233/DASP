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

localIP = socket.gethostbyname(socket.gethostname())
GUIinfo = [localIP, 50000]
data = {
    "key": "restart",
    "GUIinfo": GUIinfo
}
data = json.dumps(data)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((remoteIP, 10006))
message = "POST / HTTP/1.1\r\n\r\n"
message += data
s.sendall(str.encode(message))
s.close()