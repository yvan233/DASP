import time
import re
import pymysql

def obtainData(IP):
    db = pymysql.connect(host=IP, user="root", passwd="624624", db="node_config", charset='utf8')
    cursor = db.cursor()
    sql = "SELECT * FROM controlData"
    cursor.execute(sql)
    sqlData = cursor.fetchall()
    tmpData = [0, {}]
    data = []
    for i in range(len(sqlData)):
        if i == 0:
            tmpData[0] = sqlData[i][0]
            tmpData[1][sqlData[i][1]] = []
            tmpData[1][sqlData[i][1]].append({})
            tmpData[1][sqlData[i][1]][-1]["id"] = sqlData[i][2]
            tmpData[1][sqlData[i][1]][-1]["name"] = sqlData[i][3]
            tmpData[1][sqlData[i][1]][-1]["value"] = sqlData[i][4]
        elif sqlData[i][0] == sqlData[i - 1][0]:
            if sqlData[i][1] == sqlData[i - 1][1]:
                tmpData[1][sqlData[i][1]].append({})
                tmpData[1][sqlData[i][1]][-1]["id"] = sqlData[i][2]
                tmpData[1][sqlData[i][1]][-1]["name"] = sqlData[i][3]
                tmpData[1][sqlData[i][1]][-1]["value"] = sqlData[i][4]
            else:
                tmpData[1][sqlData[i][1]] = []
                tmpData[1][sqlData[i][1]].append({})
                tmpData[1][sqlData[i][1]][-1]["id"] = sqlData[i][2]
                tmpData[1][sqlData[i][1]][-1]["name"] = sqlData[i][3]
                tmpData[1][sqlData[i][1]][-1]["value"] = sqlData[i][4]
        else:
            data.append(tmpData)
            tmpData = [0, {}]
            tmpData[0] = sqlData[i][0]
            tmpData[1][sqlData[i][1]] = []
            tmpData[1][sqlData[i][1]].append({})
            tmpData[1][sqlData[i][1]][-1]["id"] = sqlData[i][2]
            tmpData[1][sqlData[i][1]][-1]["name"] = sqlData[i][3]
            tmpData[1][sqlData[i][1]][-1]["value"] = sqlData[i][4]
    data.append(tmpData)

    #删除数据表里数据
    sql = "TRUNCATE TABLE controldata"
    cursor.execute(sql)
    db.commit()
    db.close()
    return data

def table_exists(con, table_name):
    sql = "show tables;"
    con.execute(sql)
    tables = [con.fetchall()]
    table_list = re.findall('(\'.*?\')', str(tables))
    table_list = [re.sub("'", '', each) for each in table_list]
    if table_name in table_list:
        return 1
    else:
        return 0

def taskFunction(self,id,adjDirection,datalist,tasknum):
    db = pymysql.connect(host="localhost", user="root", passwd="cfins", db="data", charset='utf8')
    cursor = db.cursor()
    sonDirection = self.sonDirection[tasknum]
    parentDirection = self.parentDirection[tasknum]
    sonFlag = []
    parentFlag = 0
    for ele in sonDirection:
        sonFlag.append(0)

    if parentDirection == 0:
        conData = obtainData("192.168.3.35")
        for ele in sonDirection:
            self.sendDataToDirection(ele, conData, tasknum)
    else:
        while 1:
            time.sleep(0.01)
            for j in range(len(adjDirection)):
                if (parentDirection == adjDirection[j]):
                    if self.adjData[tasknum][j] != []:
                        parentFlag = 1
                        parentData = self.adjData[tasknum][j]
                        break
            if parentFlag == 1:
                conData = parentData
                for ele in sonDirection:
                    self.sendDataToDirection(ele, conData, tasknum)
                break
    # self.sendUDP(str(conData),tasknum)
    for ele in conData:
        conID = ele[0]
        conContent = ele[1]
        if conID == id:
            for key in conContent.keys():
                if table_exists(cursor, key) == 0:
                    self.sendUDP("需要控制的数据表不存在，请检查节点对应关系！", tasknum)
                else:
                    sql = "REPLACE INTO %s(time,id,name,value) VALUES" % (key)
                    for j in range(len(conContent[key])):
                        sql1 = "SELECT time FROM %s WHERE id='%s'" % (key,conContent[key][j]['id'])
                        cursor.execute(sql1)
                        data = cursor.fetchall()
                        if len(data) > 0:
                            newTime = data[-1][0] + 1
                            sql += "(%s,'%s','%s',%s)," % (newTime, conContent[key][j]['id'], conContent[key][j]['name'], conContent[key][j]['value'])
                        else:
                            self.sendUDP("需要控制的数据变量无记录，请检查相关数据表！", tasknum)
                    sql = sql[:-1]
                    cursor.execute(sql)
                    self.sendUDP("已写入新的控制指令", tasknum)
                    db.commit()
    db.close()
    return 1