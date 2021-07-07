import mysql.connector

class DB():
    def __init__(self, host = 'localhost',port= 3306, user='root', passwd='08191920.yh',database=''):
        self.conn = mysql.connector.connect(host = host, port = port, user=user,passwd=passwd,database=database)
        self.cur = self.conn.cursor()
 
    def __enter__(self):
        return self.cur
 
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

class MyDB:
    def __init__(self, host = 'localhost',port= 3306, user = "root", passwd = "08191920.yh", database= 'TESTDB'):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.databasename = database
        self.conn = mysql.connector.connect(host = host, port = port, user=user,passwd=passwd,database=database)
        self.db = self.conn.cursor()

    def create_table(self, tablename):
        self.reconnect()
        sql_drop = "DROP TABLE IF EXISTS `%s`" % (tablename)
        self.db.execute(sql_drop)
        sql_create = """CREATE TABLE `%s` (
                recordid INT NOT NULL AUTO_INCREMENT,
                code VARCHAR(255),
                codeline VARCHAR(255),
                PRIMARY KEY ( recordid )  )character set = utf8""" % (tablename)
        self.db.execute(sql_create)
        self.conn.commit()


    def insert_table(self, tablename, observelist, name, value, code, codeline):
        self.reconnect()
        name = str(name)
        value = str(value).replace("'",'')
        code = str(code).replace("'",'')
        codeline = str(codeline)
        
        refuselist = ["args","kwargs","function","self"]
        if name in refuselist:
            return 0
        if observelist:
            if name not in observelist:
                return 0

        # 获取列名
        self.db.execute("SHOW COLUMNS from `" + tablename + "`")
        answer = self.db.fetchall()
        columns = [column[0] for column in answer]
        if not name in columns:
            sql_add = "ALTER TABLE `%s` ADD `%s` VARCHAR(255)" % (tablename, name)
            self.db.execute(sql_add)
            columns.append(name)

        # 开始插入，复制上一行，只把name值改为value
        sql_select = "select * from `%s` order by recordid desc limit 1;" % (tablename)
        self.db.execute(sql_select)
        record_last = self.db.fetchone()
        if not record_last: #若为空表
            record_last = [None,None,None,None] 

        num = len(columns)
        record_last = list(record_last)
        for i in range(3):
            columns.pop(0)
            record_last.pop(0)

        for i in range(len(columns)):
            if columns[i] == name:
                record_last[i] = value

        ls1 = [str(i) for i in columns]
        ls1 = '`,`'.join(ls1)
        ls1 = "`"+ls1 + "`"
        ls2 = [str(i) for i in record_last]
        ls2 = "','".join(ls2) 
        ls2 = "'"+ls2 + "'"
        ls2 = ls2.replace("'None'","NUll")

        sql_insert = "INSERT INTO " + tablename + "(code, codeline, " \
            + ls1 + ") VALUES ('"+ code +"','" + codeline + "'," + ls2 + ")"   
        self.db.execute(sql_insert)
        self.conn.commit()

    def delete_table(self, tablename):
        self.reconnect()
        sql_drop = "DROP TABLE IF EXISTS `%s`" % (tablename)
        self.db.execute(sql_drop)  
        self.conn.commit()

    def show_tablename(self):
        self.reconnect()
        self.db.execute("SHOW TABLES")
        answer = self.db.fetchall()
        columns = [column[0] for column in answer]
        columns.insert(0,"Tables_in_%s" %(self.databasename))
        self.conn.commit()
        return columns

    def show_table(self, tablename):
        self.reconnect()
        # 获取列名

        self.db.execute("SHOW COLUMNS from `" + tablename + "`")
        answer = self.db.fetchall()
        columns = [column[0] for column in answer]
        sql_select = "select * from `%s`" % (tablename)
        self.db.execute(sql_select)   
        rows = self.db.fetchall()
        row = self.db.rowcount
        col = len(rows[0])

        result = []
        result.append(columns)

        for i in range(row):
            result_line = []
            for j in range(col):
                result_line.append(rows[i][j])
            result.append(result_line)
        self.conn.commit()
        return result

    def create_runtable(self, num, info):
        self.reconnect()
        sql_create = """CREATE TABLE IF NOT EXISTS  RUNTASK%s (
                recordid INT NOT NULL AUTO_INCREMENT,
                运行信息 VARCHAR(20000),
                PRIMARY KEY ( recordid )  )character set = utf8""" %(num)
        self.db.execute(sql_create)

        sql = "INSERT INTO RUNTASK%s (运行信息) VALUES (%s)"
        val = [num,info]
        self.db.execute(sql, val)
        self.conn.commit()

    def create_controltable(self):
        self.reconnect()
        # 先不删除旧表
        # sql_drop = "DROP TABLE IF EXISTS CONTROL" 
        # self.db.execute(sql_drop)
        sql_create = """CREATE TABLE IF NOT EXISTS CONTROL (
                recordid INT NOT NULL AUTO_INCREMENT,
                任务编号 VARCHAR(255),
                拓扑信息 VARCHAR(255),
                算法程序 VARCHAR(255),
                加载状态 VARCHAR(255),
                启动方式 VARCHAR(255),
                延时启动时间 VARCHAR(255),
                重复启动次数 VARCHAR(255),
                调试模式开关 VARCHAR(255),
                查看变量名 VARCHAR(255),
                运行状态 VARCHAR(255),
                剩余启动次数 VARCHAR(255),
                用户名 VARCHAR(255),
                PRIMARY KEY ( recordid )  )character set = utf8"""
        self.db.execute(sql_create)
        self.db.execute('select * from CONTROL')
        row = self.db.fetchall()
        if not row:
            sql = "INSERT INTO CONTROL (任务编号,拓扑信息,算法程序,加载状态,启动方式,延时启动时间,重复启动次数,调试模式开关,查看变量名,运行状态,剩余启动次数,用户名)  \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = ['0','1','系统任务','1','0','0.0','-1','0'," ",'0','-1', 'root']
            self.db.execute(sql, val)
        self.conn.commit()

    def insert_controltable(self, taskusername = 'root'):
        self.reconnect()
        datasample = ['0','0',' ','0','0','0.0','1','0',"",'0','0', taskusername]
        sql_select = "select * from CONTROL order by recordid desc limit 1"
        self.db.execute(sql_select)
        record_last = self.db.fetchone()
        datasample[0] = str(int(record_last[1])+1)
        sql = "INSERT INTO CONTROL (任务编号,拓扑信息,算法程序,加载状态,启动方式,延时启动时间,重复启动次数,调试模式开关,查看变量名,运行状态,剩余启动次数,用户名)  \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.db.execute(sql, datasample)
        self.conn.commit()
        return datasample[0]

    def delete_controltable(self, tasknum, taskusername = 'root'):
        self.reconnect()
        num = str(tasknum)
        sql_delete= "delete from CONTROL where 任务编号 = " + num
        self.db.execute(sql_delete)
        self.conn.commit()

    def update_controltable(self, tasknum, variables, value,  taskusername = 'root'):
        self.reconnect()
        num = str(tasknum)
        case = []
        for i in range(len(variables)):
            case.append(str(variables[i])+"= '"+str(value[i])+"'") 
        case = ','.join(case)

        sql_update= "UPDATE CONTROL SET "+case+" WHERE 任务编号 = " + num
        self.db.execute(sql_update)
        self.conn.commit()

    def insert_usertable(self, name, password):
        self.reconnect()
        sql = "INSERT INTO USER (name, password) VALUES (%s, %s)"
        val = [name, password]
        self.db.execute(sql, val)
        self.conn.commit()

    def show_runtable(self, tablename, lastrecordid):
        self.reconnect()
        # 获取列名
        try:
            sql_max = "select max(recordid) from `%s`" % (tablename)
            self.db.execute(sql_max)  
            maxid = self.db.fetchone()
            sql_select = "select * from `%s` where recordid > %s " % (tablename, lastrecordid)
            self.db.execute(sql_select)  
            rows = self.db.fetchall()
            row = self.db.rowcount
            self.conn.commit()
            result = []
            for i in range(row):
                result_line = rows[i][1]
                result.append(result_line)
            return result,maxid[0]
        except Exception:
            return [],lastrecordid

    def apply_permission(self, dllid,nIndex,paracode,username = 'root'):
        self.reconnect()
        sql_select = "select * from permission where dllid = %s AND nIndex >= %s AND nIndex <= %s AND paracode = %s"
        data = (dllid,nIndex[0],nIndex[1],paracode)
        self.db.execute(sql_select,data)  
        rows = self.db.fetchall()
        row = self.db.rowcount
        namelist = []

        if not row:
            for i in range(nIndex[0],nIndex[1]+1):
                sql_insert = "INSERT INTO permission (dllid,nIndex,paracode,上传用户) VALUES (%s,%s,%s,%s)"
                data = (dllid,i,paracode,username)
                self.db.execute(sql_insert,data)
        else:
            for item in rows:
                if item[4] not in namelist:
                    namelist.append(item[4])
        self.conn.commit()
        return namelist


    def cancel_permission(self, dllid,nIndex,paracode,username = 'root'):
        self.reconnect()
        if username == 'root':
            for i in range(nIndex[0],nIndex[1]+1):
                sql_insert = "DELETE FROM permission WHERE dllid = %s AND nIndex = %s AND paracode = %s"
                data = (dllid,i,paracode)
                self.db.execute(sql_insert,data)
        else:
            for i in range(nIndex[0],nIndex[1]+1):
                sql_insert = "DELETE FROM permission WHERE dllid = %s AND nIndex = %s AND paracode = %s AND 上传用户 = %s"
                data = (dllid,i,paracode,username)
                self.db.execute(sql_insert,data)
        self.conn.commit()

    def reconnect(self):
        try:
            self.conn.ping()
        except Exception:
            self.conn = mysql.connector.connect(host = self.host, port = self.port, user=self.user,passwd=self.passwd,database=self.databasename)
            self.db = self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.db.close()
        self.conn.close()

        
class SimDB:
    def __init__(self, host = "39.100.78.210", user = "root", passwd = "893893", database= "syslynkros_v30_qh"):
        self.conn = mysql.connector.connect(host = host, user=user,passwd=passwd,database = database)
        self.cur = self.conn.cursor()

    def getValue(self,paracode, table, nIndex):
        sql_select = "SELECT k%s FROM `%s` WHERE nIndex = %s" % (paracode, table, nIndex)
        self.cur.execute(sql_select)  
        data = self.cur.fetchall()
        self.conn.commit()
        return data[0][0]
    
    def controlModel(self,data):
        nID, dllid, nIndex, paracode, t, memindex, memlength, paravalue = data
        sql = "REPLACE INTO modeinfosetvalue(nID, dllid, nIndex, paracode, __t, memindex, memlength, paravalue) VALUES (%s, %s, %s, '%s', %s, %s, %s, %s);" %(nID, dllid, nIndex, paracode, t, memindex, memlength, paravalue)
        self.cur.execute(sql)
        self.conn.commit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cur.close()
        self.conn.close()
