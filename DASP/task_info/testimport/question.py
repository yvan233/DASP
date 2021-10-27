import time 
from .A import a
def taskFunction(self,id,adjDirection,datalist):
    i = 0
    a()
    for i in range(5):
        time.sleep(1)
        i += 1
        self.sendDatatoGUI("time:{}s".format(i))
    return 0