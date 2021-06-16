import copy
import time
def taskFunction(self,id,adjDirection,datalist, tasknum):                      # 返回父节点方向、子节点方向
    edges = []
    for j in reversed(range(len(self.adjID))):
        tmpid = self.adjID[j]
        self.sendDataToID(tmpid,0, tasknum)    
    if len(self.adjID) > 0:
        for i in range(len(self.adjID)):
            edges.append([self.adjID[i],self.sensorID])
    return [edges,[self.parentID[tasknum],self.sensorID]]