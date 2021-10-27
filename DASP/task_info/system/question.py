import copy
import time

def taskFunction(self, id, adjDirection, datalist):
    data = 0
    i = 0
    while(1):
        i = i + 1
        flag = 0
        for j in reversed(range(len(self.TaskadjID))):
            tmpid = self.TaskadjID[j]
            self.sendDataToID(tmpid,data)
            if len(self.TaskadjID) > j:
                if tmpid != self.TaskadjID[j]:
                    flag = 1
            else:
                flag = 1
        if flag == 0:                           
            self.sendDatatoGUI("系统第{}次自检：本节点与所有邻居通信正常，当前邻居节点：{}".format(i,str(self.TaskadjID)))
        else:
            self.sendDatatoGUI("系统第{}次自检：当前邻居节点：{}".format(i,str(self.TaskadjID)))
        time.sleep(120)
    return 0