import copy
import time 

def taskFunction(self,id,adjDirection,datalist):
    i = 0
    while True:
        # time.sleep(4)    # shutdown任务时会等待
        self.timesleep(4)  # shutdown任务时不会等待
        i += 1
        self.sendDatatoGUI("step:{}".format(i))
    return 0  