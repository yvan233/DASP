import sys
import codecs
import json
import os
import socket
import system
if __name__ == '__main__':
    IP = []
    PORT = []
    ID = []
    adjID = [] 
    datalist = []
    adjDirection = []
    localIP = socket.gethostbyname(socket.gethostname())
    path = os.getcwd() + "/Dapp/Base/topology.json"
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
        direction = selfAdjDirection[i]
        selfIPList[i].append(selfIP)
        selfIPList[i].append(selfPORT[direction])
        for j in range(n):
            if ID[j] == selfAdjID[i]:
                selfIPList[i].append(IP[j])
                for k in range(len(adjID[j])):
                    if adjID[j][k] == selfID:
                        selfIPList[i].append(PORT[j][adjDirection[j][k]])
                        selfAdjDirectionOtherSide.append(adjDirection[j][k])
                        break
                selfIPList[i].append(ID[j])
                break
    
    selfIPListprint = [str(ele) for ele in selfIPList]
    print("IPlist: "+ json.dumps(selfIPListprint, indent=2))

    GUIinfo = [localIP, 50000]
    server = system.Server(selfID, GUIinfo, selfAdjID, selfAdjDirection, selfAdjDirectionOtherSide, selfIPList, selfIP, selfPORT, selfDatalist)
    server.run()