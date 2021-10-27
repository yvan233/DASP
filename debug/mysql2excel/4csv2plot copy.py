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
node = "room_2"
fileName = 'DB_data/{}/{}.csv'.format(date,node)
starttime = 8*60+0
endtime = 19*60+0+1

csv_reader=csv.reader(open(fileName,encoding='utf-8'))
for row in csv_reader:
    csvdata.append(row)
tablehead = csvdata.pop(0)
dbtime = [parse(record[0] +" "+ record[1]) for record in csvdata]
# temper = dataconversion("room_temp1")
FCU_temp_feedback = dataconversion("FCU_temp_feedback")
FCU_temp_setpoint_feedback =  dataconversion("FCU_temp_setpoint_feedback")
FCU_fan_setpoint = dataconversion("FCU_fan_setpoint","int")
FCU_fan_feedback = dataconversion("FCU_fan_feedback","int")
FCU_onoff_setpoint = dataconversion("FCU_onoff_setpoint","int")
for i in range(len(FCU_fan_setpoint)):
    if FCU_fan_setpoint[i] == 1:
        FCU_fan_setpoint[i] = 3
    elif FCU_fan_setpoint[i] == 3:
        FCU_fan_setpoint[i] = 1
for i in range(len(FCU_fan_feedback)):
    if FCU_fan_feedback[i] == 1:
        FCU_fan_feedback[i] = 3
    elif FCU_fan_feedback[i] == 3:
        FCU_fan_feedback[i] = 1

fig = plt.figure()
ax = fig.add_subplot(4, 1, 1)
ax2 = fig.add_subplot(4, 1, 2)
ax3 = fig.add_subplot(4, 1, 3)
ax4 = fig.add_subplot(4, 1, 4)
ax.step(dbtime[starttime:endtime], FCU_temp_feedback[starttime:endtime], 'royalblue',label = 'FCU_temp_feedback',where='post',lw=2)
ax.legend(loc='upper right',frameon=True,fontsize = "small")
# ax = plt.twinx()
ax.step(dbtime[starttime:endtime], FCU_temp_setpoint_feedback[starttime:endtime], 'tomato',label = 'FCU_temp_setpoint',where='post',lw=2)
ax.legend(loc='upper right',frameon=True,fontsize = "small")
ax2.step(dbtime[starttime:endtime], FCU_onoff_setpoint[starttime:endtime], 'tomato',label = 'FCU_onoff_setpoint',where='post',lw=2)
ax2.legend(loc='upper right',frameon=True,fontsize = "small")
ax3.step(dbtime[starttime:endtime], FCU_fan_setpoint[starttime:endtime], 'green',label = 'FCU_fan_setpoint',lw=2)
ax3.legend(loc='upper right',frameon=True,fontsize = "small")
ax4.step(dbtime[starttime:endtime], FCU_fan_feedback[starttime:endtime], 'darkorange',label = 'FCU_fan_feedback',lw=2)
ax4.legend(loc='upper right',frameon=True,fontsize = "small")
# plt.xlim(0, 11)
# plt.xticks(np.arange(1, 11, 1))
# plt.ylim(-1.2, 1.2)
# plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
# plt.title('风机开关设定值、反馈值、手动保护时间')
ax.set_title("当前温度设定值、温度反馈、风机开关、风机档位设定值、风机档位反馈",fontsize=16,fontproperties="SimHei")
plt.show()