import copy
import time

def taskFunction(self, id, adjDirection, datalist, tasknum):
    data = 0
    i = 0
    while(1):
        i = i + 1
        flag = 0
        for j in reversed(range(len(self.adjID))):
            tmpid = self.adjID[j]
            self.sendDataToID(tmpid,data, tasknum)
            if len(self.adjID) > j:
                if tmpid != self.adjID[j]:
                    flag = 1
            else:
                flag = 1
        if flag == 0:                           
            self.sendUDP("系统第"+str(i)+"次自检：本节点与所有邻居通信正常",tasknum)
        self.sendUDP("系统第"+str(i)+"次自检，当前邻居节点："+str(self.adjID),tasknum) 
        time.sleep(120)
    value = data
    return value