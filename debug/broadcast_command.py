import paramiko
import os
import csv

    
localpath = os.getcwd() + "/debug/binding.csv"
# 读取节点信息
with open(localpath,'r')as f:
    data = csv.reader(f)
    binding = []
    for i in data:
        binding.append(i)
for ele in binding[1:]:
    if ele[2] == "pi":
        if ele[1] != "offline":
            try:
                hostname = ele[1]   #linux主机IP地址
                port = 22   #端口
                username = 'pi'   #用户名
                password = 'raspberry'    #密码
                t=paramiko.Transport((hostname,port))
                t.connect(username=username,password=password)
                ssh = paramiko.SSHClient()
                ssh._transport = t
                # 打开一个Channel并执行命令
                # stdin, stdout, stderr = ssh.exec_command('ls') 
                cmd = "sudo reboot"
                # cmd =  "cp -r xingtian/. xt2"
                # cmd = "sudo cp yanhu/DASP/myscript_pi.service /etc/systemd/system/myscript_pi.service"
                # cmd = "sudo systemctl enable myscript_pi.service"
                stdin, stdout, stderr = ssh.exec_command(cmd,timeout=2)  # stdout 为正确输出，stderr为错误输出，同时是有1个变量有值
                # 打印执行结果
                print(stdout.read().decode('utf-8'))
                # 关闭SSHClient
                t.close()
                print( ele[0] + '执行成功！')  
            except Exception as e:
                print( ele[0] + '执行失败！')  

