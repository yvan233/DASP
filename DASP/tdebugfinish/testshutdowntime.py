# 测试终止线程时里面的timesleep()
import threading
import time
from datetime import datetime
class Checker(threading.Thread):
    def __init__(self, event):
        super().__init__()
        self.event = event

    def run(self):
        while not self.event.is_set():
            print('检查是否在运行')
            print(datetime.now())
            self.event.wait(10)
            print(datetime.now())
            # time.sleep(10)
        print("运行结束")


event = threading.Event()
checker = Checker(event)
checker.start()
time.sleep(15)
event.set()
