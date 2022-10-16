import sys
import codecs
import json
import os
import socket
import system
if __name__ == '__main__':
    IP = []
    Port = []
    ID = []
    nbrID = [] 
    datalist = []
    nbrDirection = []
    localIP = socket.gethostbyname(socket.gethostname())
    path = os.getcwd() + "/Dapp/Base/topology.json"
    text = codecs.open(path, 'r', 'utf-8').read()
    js = json.loads(text)
    for ele in js:
        if "ID" in ele:
            ID.append(ele["ID"])
            IP.append(localIP)
            Port.append(ele["Port"])
            nbrID.append(ele["nbrID"])
            nbrDirection.append(ele["nbrDirection"])
            datalist.append(ele["datalist"])

    order = int(sys.argv[1])
    selfID = ID[order]
    selfAdjID = nbrID[order]
    selfAdjDirection = nbrDirection[order]
    selfIP = IP[order]
    selfPort = Port[order]
    selfDatalist = datalist[order]
    selfRouteTable = []
    selfAdjDirectionOtherSide = {}
    n = len(IP)
    for i in range(len(selfAdjID)):
        selfRouteTable.append([])
        direction = selfAdjDirection[i]
        selfRouteTable[i].append(selfIP)
        selfRouteTable[i].append(selfPort[direction])
        for j in range(n):
            if ID[j] == selfAdjID[i]:
                selfRouteTable[i].append(IP[j])
                for k in range(len(nbrID[j])):
                    if nbrID[j][k] == selfID:
                        selfRouteTable[i].append(Port[j][nbrDirection[j][k]])
                        selfAdjDirectionOtherSide[ID[j]] = nbrDirection[j][k]
                        break
                selfRouteTable[i].append(ID[j])
                break
    
    selfRouteTableprint = [str(ele) for ele in selfRouteTable]
    print("RouteTable: "+ json.dumps(selfRouteTableprint, indent=2))

    GuiInfo = [localIP, 50000]
    server = system.Server(selfID, GuiInfo, selfAdjID, selfAdjDirection, selfAdjDirectionOtherSide, selfRouteTable, selfIP, selfPort, selfDatalist)
    server.run()
    server.runSystemTask()