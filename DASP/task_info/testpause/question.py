import copy
import time 

def taskFunction(self,id,adjDirection,datalist):
    i = 0
    while True:
        time.sleep(1)
        i += 1
        self.sendDatatoGUI("time:{}s".format(i))
    return 0  