DatabaseInfo = {
    'host': "127.0.0.1",
    'port': 3306,
    'user': 'root',
    'password': 'DSPadmin',
 }
ObserveList = ["x", "m"]
data = {
    "key": "newtask",
    "DAPPname": "宽度优先生成树",
    "DebugMode": True, 
    "DatabaseInfo": DatabaseInfo,
    "ObserveList": ObserveList
}

import pysnooperDB

path2 = os.getcwd() + "\\IoT\\task\\debug"+str(num)+".txt"
debuglist = []
debugmode_flag = 0
with open( path2, 'r' ) as f:
    for line in f.readlines():  
        line=line.strip('\n')  
        debuglist.append(line)
print (debuglist)
if "start in debug mode" in debuglist:
    debugmode_flag = 1
if debugmode_flag:
    debuglist.pop()
user = debuglist.pop(0)
passwd = debuglist.pop(0)
databasename = 'DASPdb'

debuglist[0] = debuglist[0].strip(" ")
observelist = []
if len(debuglist) and debuglist != [""]:
    observelist = debuglist

if debugmode_flag:
    tablename = "{}_{}".format(self.DAPPname, self.nodeID)
    taskfunc = pysnooperDB.snoop(tablename = tablename,observelist = observelist,\
        user= user, passwd= passwd,databasename = databasename)(self.taskFuncList[num])