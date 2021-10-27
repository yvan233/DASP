import paramiko
import os
import sys
import csv

num = sys.argv[1]
path = os.getcwd() + "\\IoT\\binding.csv"
port = 22   #端口
username = 'pi'   #用户名
password = 'raspberry'    #密码
with open(path,'r')as f:
    data = csv.reader(f)
    idiplist = []
    for i in data:
        idiplist.append(i)
for ele in idiplist[1:]:
    if ele[1]:
        try:
            hostname = ele[1]   #linux主机IP地址
            t=paramiko.Transport((hostname,port))
            t.connect(username=username,password=password)
            sftp = paramiko.SFTPClient.from_transport(t)
            localpath = os.getcwd() + '\\IoT\\task\\question'+str(num)+'.py'
            remotepath = '/home/pi/zhongdy/IoT/task/question'+str(num)+'.py'
            sftp.put(localpath, remotepath) #将windows的文件上传到linux中，put上传
            sftp.close()
            print( ele[0] + '算法文件上传成功！')  
        except Exception as e:
            print( ele[0] + '算法文件上传失败！')  

        try:
            hostname = ele[1]   #linux主机IP地址
            t=paramiko.Transport((hostname,port))
            t.connect(username=username,password=password)
            sftp = paramiko.SFTPClient.from_transport(t)
            localpath = os.getcwd() + '\\IoT\\task\\topology'+str(num)+'.txt'
            remotepath = '/home/pi/zhongdy/IoT/task/topology'+str(num)+'.txt'
            sftp.put(localpath, remotepath) #将windows的文件上传到linux中，put上传
            sftp.close()
            print( ele[0] + '拓扑文件上传成功！')  
        except Exception as e:
            print( ele[0] + '拓扑文件上传失败！')  