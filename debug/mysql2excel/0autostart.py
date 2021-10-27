# 自动脚本
import time
import subprocess,threading

class Proc:
    """用于多进程开启脚本   
    属性:
        path: 脚本路径
        date: 日期
        proc: 节点进程
        thread: 节点获取输出数据线程
        
        """
        
    def __init__(self, path, date):
        # -u参数是为了读取缓冲区中的打印信息
        self.proc = subprocess.Popen(['python','-u', path, date],\
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.end_judge()
        
    def end_judge(self):
        while True:
            rcode = self.proc.poll()
            # 若进程未结束
            if rcode is None:
                line = self.proc.stdout.readline().strip().decode('GBK')  #cmd窗口默认GBK编码
                if line:
                    print(line)
            else:
                print("运行结束")
                break
            time.sleep(0.01)

    def kill(self):
        """
        杀死节点进程
        """
        self.proc.kill()
        self.proc.wait()
        print ("[node{}]: 进程已被杀死".format(self.num))
datelist =["2021-08-04",
"2021-08-05",
"2021-08-06",
"2021-08-07"]

for i in range(1, len(datelist)):
    date_backup = datelist[i]
    date_real = datelist[i-1]
    proc = Proc('./debug/mysql2excel/1file2sql.py', date_backup)
    proc = Proc('./debug/mysql2excel/2sql2csvpast.py', date_real)
    # proc = Proc('./debug/mysql2excel/5data_process.py', date_real)
    # proc = Proc('./debug/mysql2excel/6data_process_fixed.py', date_real)
