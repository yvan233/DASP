import csv
import platform
import os
import threading
import socket

class nodes():

    exist_nodes = []
    def __init__(self):
        pass
    def get_os(self):
        os = platform.system()
        if os == "Windows":
            return "n"
        else:
            return "c"

    # 这里可以对字典数据操作
    def ping_ip(self,nodeid,nodeip):
        flag = 0
        cmd = ["ping", "-{op}".format(op=self.get_os()),
            "1", nodeip]
        output = os.popen(" ".join(cmd)).readlines()
        for line in output:
            if str(line).upper().find("TTL") >= 0:
                # print(nodeid+ ' connect success.')
                self.exist_nodes.append(nodeid)
                flag = 1
                break
        if flag == 0:
            # print(nodeid+ ' connect failed.')
            pass

    
    def find_ip(self):
        threads = []
        self.exist_nodes = []
        localpath = os.getcwd() + "\\IoT\\binding.csv"
        with open(localpath,'r')as f:
            data = csv.reader(f)
            idiplist = []
            for i in data:
                idiplist.append(i)
        for ele in idiplist[1:]:
            if ele[1]:
                threads.append(threading.Thread(target=self.ping_ip, args=(ele[0],ele[1])))
        for i in threads:
            i.start()
        for i in threads:
            i.join()
 
if __name__ == "__main__":
    node = nodes()
    node.find_ip()
    print(node.exist_nodes)