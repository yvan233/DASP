DatabaseInfo = ["root", "08191920.yh", "TESTDB", "Tables"]
ObservedVariable = ["x", "m"]
data = {
    "key": "newtask",
    "DAPPname": "宽度优先生成树",
    "DebugMode": True, 
    "DatabaseInfo": DatabaseInfo,
    "ObservedVariable": ObservedVariable
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
databasename = debuglist.pop(0)
tablenamePrefix = debuglist.pop(0)

debuglist[0] = debuglist[0].strip(" ")
observelist = []
if len(debuglist) and debuglist != [""]:
    observelist = debuglist

if debugmode_flag:
    tablename = tablenamePrefix + "_task" + str(num) + "_node" + str(self.sensorID)
    filename = "./log/" + tablename + '.log'                          
    taskfunc = pysnooperDB.snoop(tablename = tablename,observelist = observelist,\
        user= user, passwd= passwd,databasename = databasename)(self.taskFuncList[num])