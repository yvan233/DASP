import paramiko
import os
import csv


hostname = "192.168.5.12"   #linux主机IP地址
port = 22   #端口
username = 'skl'   #用户名
password = 'skl'    #密码
t=paramiko.Transport((hostname,port))
t.connect(username=username,password=password)
ssh = paramiko.SSHClient()
ssh._transport = t
# 打开一个Channel并执行命令
# stdin, stdout, stderr = ssh.exec_command('ls') 
cmd = "hostname -I"
# ls =  "cp -r xingtian/. xt2"
# ls = "sudo cp yanhu/DASP/myscript_pi.service /etc/systemd/system/myscript_pi.service"
# ls = "sudo systemctl enable myscript_pi.service"
stdin, stdout, stderr = ssh.exec_command(cmd,timeout=2)  # stdout 为正确输出，stderr为错误输出，同时是有1个变量有值
# 打印执行结果
print(stdout.read().decode('utf-8'))
# 关闭SSHClient
t.close()


