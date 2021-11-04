import os, csv 
path = os.getcwd() + "/DASP/task_info/system/autostart.csv"
with open(path,'r',encoding='utf-8-sig')as f:
    data = csv.reader(f)
    dapp_autostart = []
    for i in data:
        dapp_autostart.append(i)
del dapp_autostart[0]
print(dapp_autostart)
"[['CreateBFStree', 'room_1', '10'], ['宽度优先生成树', 'default', '20']]"