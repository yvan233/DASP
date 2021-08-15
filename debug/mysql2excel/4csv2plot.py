import matplotlib.pyplot as plt
import numpy as np
from dateutil.parser import parse
import os,csv

csvdata = []
tablehead = []

#数据转换
def dataconversion(dataneme, datatype = "float"):
    global tablehead,csvdata
    returndata = [record[tablehead.index(dataneme)] for record in csvdata]
    if datatype == "float":
        for i in range(len(returndata)):
            if returndata[i]:
                returndata[i] = float(returndata[i])
            elif i>0:
                returndata[i] = float(returndata[i-1])
            else:
                returndata[i] = float(returndata[i+1])
    else:
        for i in range(len(returndata)):
            if returndata[i]:
                returndata[i] = float(returndata[i])
            elif i>0:
                returndata[i] = float(returndata[i-1])
            else:
                returndata[i] = float(returndata[i+1])
    return returndata

date = "2021-08-14"
node = "room_4"
fileName = 'DB_data/{}/{}.csv'.format(date,node)
starttime = 8*60+0
endtime = 19*60+0+1

csv_reader=csv.reader(open(fileName,encoding='utf-8'))
for row in csv_reader:
    csvdata.append(row)
tablehead = csvdata.pop(0)
dbtime = [parse(record[0] +" "+ record[1]) for record in csvdata]
temper = dataconversion("room_temp1")
plt.step(dbtime[starttime:endtime], temper[starttime:endtime], where='post',lw=2)

# plt.xlim(0, 11)
# plt.xticks(np.arange(1, 11, 1))
# plt.ylim(-1.2, 1.2)

plt.show()