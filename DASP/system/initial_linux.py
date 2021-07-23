import csv
import codecs
import json
import subprocess
import time
import os
# 设置当前工作目录
os.chdir('/home/pi/yanhu')
import system
if __name__ == '__main__':
    time.sleep(2)
    path = "/home/pi/yanhu/DASP/system/binding.csv"
    with open(path,'r')as f:
        data = csv.reader(f)
        idiplist = []
        for i in data:
            idiplist.append(i)

    p = subprocess.Popen("hostname -I", shell=True, stdout=subprocess.PIPE)
    nodeIP = p.stdout.read()
    nodeIP = str(nodeIP,encoding = 'UTF-8').strip(' \n')
    selfID = 0
    for ele in idiplist:
        if ele[1] == nodeIP:
            selfID = ele[0]
            break
    if selfID:
        IP = []
        PORT = []
        ID = []
        adjID = []
        datalist = []
        adjDirection = []
        path = "/home/pi/yanhu/DASP/task_info/system/topology.txt"
        text = codecs.open(path, 'r', 'utf-8').read()
        js = json.loads(text)
        for ele in js:
            if "ID" in ele:
                ID.append(ele["ID"])
                tmpIP = ""
                for ele2 in idiplist:
                    if ele2[0] == ele["ID"]:
                        tmpIP = ele2[1]
                        break
                IP.append(tmpIP)
                PORT.append([10000, 10001, 10002, 10003, 10004, 10005, 10006])
                adjID.append(ele["adjID"])
                adjDirection.append(ele["adjDirection"])
                datalist.append(ele["datalist"])
                
        order = ID.index(selfID)
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
                
        selfIPListprint = [str(ele) for ele in selfIPList]
        print("IPlist: "+ json.dumps(selfIPListprint, indent=2))
        server = system.Server(selfID, selfAdjID, selfAdjDirection, selfAdjDirectionOtherSide, selfIPList, selfIP, selfPORT, selfDatalist)
        server.run()
    else:
        print("该节点IP未被录入！")



