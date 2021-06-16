import paramiko
import os
import csv

# localpath2 = os.getcwd() + "\\DASP\\nodesystem_pi_newnode.py"
localpath2 = os.getcwd() + "\\DASP\\topology.txt"
localpath = os.getcwd() + "\\DASP\\binding.csv"
with open(localpath,'r')as f:
    data = csv.reader(f)
    idiplist = []
    for i in data:
        idiplist.append(i)
for ele in idiplist[1:]:
    if ele[1]:
        try:
            hostname = ele[1]   #linux主机IP地址
            port = 22   #端口
            username = 'pi'   #用户名
            password = 'raspberry'    #密码
            t=paramiko.Transport((hostname,port))
            t.connect(username=username,password=password)
            sftp = paramiko.SFTPClient.from_transport(t)
            remotepath = '/home/pi/zhongdy/DASP/topology.txt'
            sftp.put(localpath2, remotepath) #将windows的文件上传到linux中，put上传
            sftp.close()
            print( ele[0] + '上传成功！')  
        except Exception as e:
            print( ele[0] + '上传失败！')  

