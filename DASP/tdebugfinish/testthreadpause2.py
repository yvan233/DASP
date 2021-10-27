# 测试暂停恢复线程
import threading
import time


 
class Job():

    def __init__(self):

        self.__flag = threading.Event()     # 用于暂停的标识
        self.__flag.set()       # 设置为True
        self.t = threading.Thread(target=self.test, args=())
        self.t.start()
    def test(self):
        while True:
            self.__flag.wait()      # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            print ('test')
            time.sleep(1)


    def pause(self):
        self.__flag.clear()     # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()    # 设置为True, 让线程停止阻塞
   

a = Job()

time.sleep(3)
a.pause()

time.sleep(3)
a.resume()

# time.sleep(3)
# a.pause()
# time.sleep(2)
