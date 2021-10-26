# 房间人员绘制脚本
import matplotlib.pyplot as plt
from dateutil.parser import parse
import csv


fig = plt.figure()
axlist = []

# 日期列表（需修改）
datelist = ["2021-08-14","2021-08-15","2021-08-16","2021-08-17","2021-08-18"]
colorlist = ['darkorange','royalblue','tomato','green','deepskyblue']
# 房间（可修改）
node = "room_2"
for i in range(len(datelist)):
    ax = fig.add_subplot(5, 1, i+1)
    axlist.append(ax)

    # 文件相对路径（需修改）
    fileName = 'DB_data/{}/{}.csv'.format(datelist[i],node)

    # 绘图时间区间（可修改，格式：小时*60+分钟）
    starttime = 8*60+0
    endtime = 19*60+0+1

    csvdata =[]
    csv_reader=csv.reader(open(fileName,encoding='utf-8'))
    for row in csv_reader:
        csvdata.append(row)
    tablehead = csvdata.pop(0)
    dbtime = [parse(record[0] +" "+ record[1]) for record in csvdata]
    occupant_num = data = [record[tablehead.index("occupant_num")] for record in csvdata]
    
    #绘图
    ax.step (dbtime[starttime:endtime], occupant_num[starttime:endtime], colorlist[i],label = 'occupant_num',lw=2)
    ax.legend(loc='upper right',frameon=True,fontsize = "small")

axlist[0].set_title("房间人员",fontsize=16,fontproperties="SimHei")
plt.show()