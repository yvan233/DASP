import threading
import subprocess
import time
def start_proxy():
    try:
        p = subprocess.Popen("python -u ./DASP/tdebugtemp/test.py", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            process_code = p.poll()
            if process_code is None:
                line = p.stdout.readline().strip().decode()  #cmd窗口默认GBK编码
                if line:
                    print(line)
            else:
                print("进程异常退出！{}".format(str(process_code)))
                break
            # elif process_code == 0:
            #     print("进程正常退出！{}".format(str(process_code)))
            #     break
    except Exception as e:
        print(e)

def start_threading():
    try:
        td = threading.Thread(
            target=start_proxy
        )
        td.setDaemon(True)
        td.start()
        td.join(2)
    except threading.ThreadError as e:
        print(e)

if __name__ == '__main__':
    start_threading()
    time.sleep(2)
    print(1)
# ————————————————
# 版权声明：本文为CSDN博主「新月爱文宇」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/qq_37746897/article/details/109819788