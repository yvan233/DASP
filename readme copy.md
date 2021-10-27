`pip install paramiko`

广播绑定文件 python .\script\broadcast_binding.py
广播拓扑文件 python .\script\broadcast_topology.py
重启所有树莓派  python .\script\broadcast_restart.py
广播计算任务文件 python .\script\broadcast_task.py [tasknum]
打开监测端口  python .\script\moniter.py
启动系统  python .\script\run.py [ID]
启动计算任务 python .\script\starttask.py [ID] [tasknum] [delay]
停止计算任务 python .\script\stoptask.py [ID] [tasknum] [delay]


### windows本地运行
开启所有节点：  .\IoT\start.bat 12
开启某一节点：python .\IoT\initial.py 1
关闭节点： taskkill /f /im python.exe
开启监测  python .\script\moniter.py
启动系统  python .\shumeipaitest\1run.py
运行任务  python .\shumeipaitest\2starttask.py


CreateBFStree 显示了对DSP2.0的兼容
宽度优先生成树 显示了DASP下对同步通信函数的修改以及对程序为中文名的支持

pymysql
paramiko