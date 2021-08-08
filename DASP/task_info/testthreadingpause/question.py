import copy
import time 
import threading

def test(printf):
    i = 0
    while True:
        time.sleep(1)
        i += 1
        printf("time:{}s".format(i))

def taskFunction(self,id,adjDirection,datalist):
    t = threading.Thread(target=test,args = (self.sendDatatoGUI,))
    t.setDaemon(True) 
    t.start()
    t.join()
    return 0  