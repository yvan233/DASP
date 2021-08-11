# mysql 存储成 csv脚本  转化成多维数据
"""
后续需要加一个indoortemp、alarm
"""
import pymysql
import csv,os
from datetime import datetime
date = "2021-08-10"  #待导出的数据日期

def valueindex(tablename, valuename, tablehead):
    if tablename == "fcu_panel_his" and valuename == "FCU_temp_setpoint":
        return tablehead.index("FCU_temp_setpoint_feedback")
    else:
        return tablehead.index(valuename)

def from_mysql_get_all_info(nodename, tablename):
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        db='data_{}'.format(nodename),
        password='DSPadmin')
    cursor = conn.cursor()
    sql = 'select * from {}'.format(tablename)
    cursor.execute(sql.encode('utf-8'))
    data = cursor.fetchall()
    conn.close()
    return data

def write_csv(nodename,tablehead):
    filepath = 'DB_data/{}'.format(date)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    filename = '{}/{}.csv'.format(filepath,nodename)
    with open(filename,mode='w',newline="",encoding='utf-8') as f:
        write = csv.writer(f,dialect='excel')
        write.writerow(tablehead)
        for ele in data:
            write.writerow(ele)

roomnodenamelist = ["room_1","room_2","room_3","room_4","room_5","room_6","room_7"]
roomtablenamelist = ["fcu_control_his", "fcu_panel_his","sensor_fcu_waterflow_his","sensor_fcu_watertemp_his","sensor_occupant_his","sensor_room_his"]
# csv表头
roomtablehead = [
    "date",
    "time",
    "FCU_temp_setpoint",
    "FCU_onoff_setpoint",
    "FCU_fan_setpoint",
    "FCU_mode_setpoint",
    "FCU_temp_setpoint_feedback",
    "FCU_onoff_feedback",
    "FCU_lock_feedback",
    "FCU_fan_feedback",
    "FCU_mode_feedback",
    "supply_pressure",
    "return_pressure",
    "waterflow",
    "supply_temp",
    "return_temp",
    "occupant_num",
    "occupant_transform",
    "room_temp1",
    "room_RH1",
    "room_temp2",
    "room_RH2",
    "differential_pressure"
]


pumpnodenamelist = ["pump_1"]
pumptablenamelist = ["electric_meter_his","pump_vfd_control_his","pump_vfd_his","sensor_outdoor_his","sensor_pressure_his","sensor_watertemp_his"]
pumptablehead = [
    "date",
    "time",
    "Active_power",
    "Reactive_power",
    "Apparent_power",
    "Active_energy",
    "Reactive_energy",
    "pump_onoff_setpoint",
    "pump_frequency_setpoint",
    "pump_onoff_feedback",
    "pump_frequency_feedback",
    "outdoor_temp",
    "supply_pressure",
    "return_pressure",
    "return_temp"
]

heatpumpnodenamelist = ["heatpump_1"]
heatpumptablenamelist = ["heatpump_panel_his"]
heatpumptablehead = [
    "date",
    "time",
    "heatpump_supplytemp_feedback",
    "heatpump_workingmode_feedback",
]

for nodename in roomnodenamelist:
    dataline = [""]*len(roomtablehead)
    data = [dataline[:] for i in range(1440)]
    for i in range(1440):
        data[i][0] = date
        data[i][1] = "{0:02d}:{1:02d}".format(int(i/60),i%60)

    for tablename in roomtablenamelist:
        sqldata = from_mysql_get_all_info(nodename, tablename)
        for ele in sqldata:
            if ele[0] != " ":
                time = datetime.strptime(ele[0],"%Y-%m-%d %H:%M:%S")
                index = time.minute + time.hour * 60
                data[index][valueindex(tablename, ele[2], roomtablehead)] = ele[3]
    write_csv(nodename,roomtablehead)
    print(nodename, "finished")

for nodename in pumpnodenamelist:
    dataline = [""]*len(pumptablehead)
    data = [dataline[:] for i in range(1440)]
    for i in range(1440):
        data[i][0] = date
        data[i][1] = "{0:02d}:{1:02d}".format(int(i/60),i%60)

    for tablename in pumptablenamelist:
        sqldata = from_mysql_get_all_info(nodename, tablename)
        for ele in sqldata:
            if ele[0] != " ":
                time = datetime.strptime(ele[0],"%Y-%m-%d %H:%M:%S")
                index = time.minute + time.hour * 60
                data[index][valueindex(tablename, ele[2], pumptablehead)] = ele[3]
    write_csv(nodename, pumptablehead)
    print(nodename, "finished")

for nodename in heatpumpnodenamelist:
    dataline = [""]*len(heatpumptablehead)
    data = [dataline[:] for i in range(1440)]
    for i in range(1440):
        data[i][0] = date
        data[i][1] = "{0:02d}:{1:02d}".format(int(i/60),i%60)

    for tablename in heatpumptablenamelist:
        sqldata = from_mysql_get_all_info(nodename, tablename)
        for ele in sqldata:
            if ele[0] != " ":
                time = datetime.strptime(ele[0],"%Y-%m-%d %H:%M:%S")
                index = time.minute + time.hour * 60
                data[index][valueindex(tablename, ele[2], heatpumptablehead)] = ele[3]
    write_csv(nodename, heatpumptablehead)
    print(nodename, "finished")