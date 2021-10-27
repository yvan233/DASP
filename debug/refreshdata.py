
import csv
import os
import pymysql
import time


def db_read(cursor, table, name, num):               # num 为倒序读取数据条目数，0表示读取全部
    if num == 0:
        sql = "SELECT %s, %s, %s, %s FROM %s WHERE name='%s'" % ('time', 'id', 'name', 'value', table, name)
        cursor.execute(sql)
        data = cursor.fetchall()
    else:
        sql = "SELECT %s, %s, %s, %s FROM %s WHERE name='%s' order by time DESC limit %d" % ('time', 'id', 'name', 'value', table, name, num)
        cursor.execute(sql)
        data = cursor.fetchall()

    return data


def dp_show(cursor,node, table, name, num):
    try:
        data = list(db_read(cursor, table, name, num)[0])
        del data[1]
        print( node ,data)
    except Exception as e:
        print( node + name+'读取失败！') 

"""
刷新读取各节点压差
"""

if __name__ == '__main__':
    localpath = os.getcwd() + "\\debug\\binding.csv"
    # 读取节点信息
    with open(localpath,'r')as f:
        data = csv.reader(f)
        idiplist = []
        for i in data:
            idiplist.append(i)

    while (1):
        for ele in idiplist[1:]:
            if ele[1] != "false":
                supply_temp = []
                return_temp = []
                supply_pressure = []
                return_pressure = []
                db = pymysql.connect(host=ele[1], user="root", passwd="cfins", db="data", charset='utf8')
                cursor = db.cursor()
                dp_show(cursor,ele[0], 'sensor_fcu_watertemp', 'supply_temp', 0)
                dp_show(cursor,ele[0],'sensor_fcu_watertemp', 'return_temp', 0)
                dp_show(cursor,ele[0], 'sensor_fcu_waterflow', 'supply_pressure', 0)
                dp_show(cursor,ele[0], 'sensor_fcu_waterflow', 'return_pressure', 0)
                
        time.sleep(10)
        print("")
