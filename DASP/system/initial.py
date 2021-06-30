import system
import sys
import codecs
import json
import os
import socket

if __name__ == '__main__':
    IP = []
    PORT = []
    ID = []
    adjID = [] 
    datalist = []
    adjDirection = []
    localIP = socket.gethostbyname(socket.gethostname())
    path = os.getcwd() + "\\DASP\\task_info\\system\\topology.txt"
    path = path.replace('\\', '/')  
    text = codecs.open(path, 'r', 'utf-8').read()
    js = json.loads(text)
    for ele in js:
        if "ID" in ele:
            ID.append(ele["ID"])
            IP.append(localIP)
            PORT.append(ele["PORT"])
            adjID.append(ele["adjID"])
            adjDirection.append(ele["adjDirection"])
            datalist.append(ele["datalist"])

    order = int(sys.argv[1]) - 1
    selfID = ID[order]
    selfAdjID = adjID[order]
    selfAdjDirection = adjDirection[order]
    selfIP = IP[order]
    selfPORT = PORT[order]
    selfDatalist = datalist[order]
    selfIPList = []
    selfAdjDirectionOtherSide = []
    n = len(IP)
    for i in range(len(selfAdjID)):
        selfIPList.append([])
        direction = selfAdjDirection[i] - 1
        selfIPList[i].append(selfIP)
        selfIPList[i].append(selfPORT[direction])
        for j in range(n):
            if ID[j] == selfAdjID[i]:
                selfIPList[i].append(IP[j])
                for k in range(len(adjID[j])):
                    if adjID[j][k] == selfID:
                        selfIPList[i].append(PORT[j][adjDirection[j][k]-1])
                        selfAdjDirectionOtherSide.append(adjDirection[j][k])
                        break
                selfIPList[i].append(ID[j])
                break
    
    print(json.dumps(selfIPList, indent=2))

    server = system.Server(selfID, selfAdjID, selfAdjDirection, selfAdjDirectionOtherSide, selfIPList, selfIP, selfPORT, selfDatalist)
    server.run()