import sys
sys.path.insert(1,".")
from DASP.pysnooperdb.tracer import Tracer as snoop
DatabaseInfo = {
    'host': "127.0.0.1",
    'port': 3306,
    'user': 'root',
    'password': 'DSPadmin',
 }

ObservedVariable = ["x", "m"]
data = {
    "key": "newtask",
    "DAPPname": "宽度优先生成树",
    "DebugMode": True, 
    "DatabaseInfo": DatabaseInfo,
    "ObservedVariable": ObservedVariable
}


database = 'Daspdb'
tablenamePrefix = 'DAPPname'
observelist = ['i','n','sum']
def A():
    sum = 0
    for i in range(5):
        for n in range(2):
            sum += i*10+n

B = snoop(config = DatabaseInfo, db = database, tablename = 'test111', observelist = observelist)(A)
B()
