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
            elif returndata[i-1]:
                returndata[i] = float(returndata[i-1])
            else:
                returndata[i] = 0
    else:
        for i in range(len(returndata)):
            if returndata[i]:
                returndata[i] = int(returndata[i])
            elif returndata[i-1]:
                returndata[i] = int(returndata[i-1])
            else:
                returndata[i] = 0
    return returndata

date = "2021-08-14"
node = "room_6"
fileName = 'DB_data/{}/{}.csv'.format(date,node)
starttime = 8*60+0
endtime = 19*60+0+1

csv_reader=csv.reader(open(fileName,encoding='utf-8'))
for row in csv_reader:
    csvdata.append(row)
tablehead = csvdata.pop(0)
dbtime = [parse(record[0] +" "+ record[1]) for record in csvdata]
# temper = dataconversion("room_temp1")
FCU_onoff_setpoint = dataconversion("FCU_onoff_setpoint","int")
occupant_num = dataconversion("occupant_num","int")
FCU_onoff_feedback =  dataconversion("FCU_onoff_feedback","int")
manul_FCU_onoff =  dataconversion("manul_FCU_onoff","int")
fig = plt.figure()
ax = fig.add_subplot(4, 1, 2)
ax2 = fig.add_subplot(4, 1, 3)
ax3 = fig.add_subplot(4, 1, 4)
ax4 = fig.add_subplot(4, 1, 1)
ax.step(dbtime[starttime:endtime], FCU_onoff_setpoint[starttime:endtime], 'royalblue',label = 'FCU_onoff_setpoint',where='post',lw=2)
ax.legend(loc='upper right',frameon=True,fontsize = "small")
# ax = plt.twinx()
ax2.step(dbtime[starttime:endtime], FCU_onoff_feedback[starttime:endtime], 'tomato',label = 'FCU_onoff_feedback',where='post',lw=2)
ax2.legend(loc='upper right',frameon=True,fontsize = "small")
ax3.plot(dbtime[starttime:endtime], manul_FCU_onoff[starttime:endtime], 'green',label = 'manul_time',lw=2)
ax3.legend(loc='upper right',frameon=True,fontsize = "small")
ax4.step (dbtime[starttime:endtime], occupant_num[starttime:endtime], 'darkorange',label = 'occupant_num',lw=2)
ax4.legend(loc='upper right',frameon=True,fontsize = "small")
# plt.xlim(0, 11)
# plt.xticks(np.arange(1, 11, 1))
# plt.ylim(-1.2, 1.2)
# plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
# plt.title('风机开关设定值、反馈值、手动保护时间')
ax4.set_title("房间人员、风机开关设定值、反馈值、手动保护时间",fontsize=16,fontproperties="SimHei")
plt.show()