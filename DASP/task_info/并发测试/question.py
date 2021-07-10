import time
import copy

def taskFunction(self,id,adjDirection,datalist):
    data = [[id]]*len(adjDirection)
    for m in range(10000):
        # self.transmitData(adjDirection, data)
        # time.sleep(1)
        self.syncNode()
        print (m)
    return 0