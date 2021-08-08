import threading

import time
 
def target():
    print('当前的线程%s 在运行' % threading.current_thread().name)
    time.sleep(6)
    print('当前的线程 %s 结束' % threading.current_thread().name)
 
print('当前的线程 %s 在运行' % threading.current_thread().name)
t = threading.Thread(target=target,args = [])

t.setDaemon(True) # 设置守护进程t.setDaemon(True)后，主进程结束就结束了整个进程
t.start()
t.join(5)  #为子线程设定运行的时间，5s后就退出子线程，如果不加等待时间，就会一直等待子线程运行结束后，再运行主线程
print('当前的线程 %s 结束' % threading.current_thread().name)
'''
当前的线程 MainThread 在运行
当前的线程Thread-35 在运行
当前的线程 Thread-35 结束
当前的线程 MainThread 结束
'''
# ————————————————
# 版权声明：本文为CSDN博主「brucewong0516」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/brucewong0516/article/details/81028716