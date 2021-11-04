import copy
import time 

def taskFunction(self,id,adjDirection,datalist):
    # init 
    # 生成树节点标识
    min_id = id
    self.sendDatatoGUI("min "+min_id)
    for m in range(10):  # 迭代节点数量的轮次数
        _, adjData = self.transmitData(adjDirection, [min_id]*len(adjDirection))       
        for ele in adjData:
            if ele < min_id:
                min_id = ele
        self.sendDatatoGUI("min "+min_id)
    if min_id == id:
        self.sendDatatoGUI("This is leader")
    return 0