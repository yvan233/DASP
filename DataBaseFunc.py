import mysql.connector

class MyDB:
    def __init__(self, host = 'localhost',port= 3306, user = "root", passwd = "DSPadmin", database= 'pimanager'):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.databasename = database
        self.conn = mysql.connector.connect(host = host, port = port, user=user,passwd=passwd,database=database,buffered=True)
        self.db = self.conn.cursor()


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
        return columns

    def show_table(self, tablename):
        self.reconnect()
        # 获取列名
        self.db.execute("SHOW COLUMNS from `" + tablename + "`")
        answer = self.db.fetchall()
        columns = [column[0] for column in answer]
        sql_select = "SELECT * FROM `%s`" % (tablename)
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
                运行状态 VARCHAR(255),
                剩余启动次数 VARCHAR(255),
                PRIMARY KEY ( recordid )  )character set = utf8"""
        self.db.execute(sql_create)
        self.db.execute('SELECT * FROM CONTROL')
        row = self.db.fetchall()
        if not row:
            sql = "INSERT INTO CONTROL (任务编号,拓扑信息,算法程序,加载状态,启动方式,延时启动时间,重复启动次数,运行状态,剩余启动次数)  \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = ['0','1','系统任务','1','0','0.0','1','0','-1']
            self.db.execute(sql, val)
        self.conn.commit()

    def show_controltable(self):
        self.reconnect()
        # 获取列名
        columns = ['recordid','任务编号','拓扑信息','算法程序','加载状态','启动方式','延时启动时间','重复启动次数','运行状态','剩余启动次数']
        sql_select = "SELECT * FROM CONTROL ORDER BY 任务编号 ASC" 
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
        return result

    def insert_controltable(self):
        self.reconnect()
        datasample = ['0','0',' ','0','0','0.0','1','0','0']
        sql_select = "SELECT 任务编号 FROM (SELECT 任务编号 FROM CONTROL ORDER BY 任务编号 ASC) T WHERE NOT EXISTS (SELECT 1 FROM CONTROL WHERE 任务编号 =T.任务编号+1)"
        self.db.execute(sql_select)
        record_last = self.db.fetchone()
        datasample[0] = str(int(record_last[0])+1)
        sql = "INSERT INTO CONTROL (任务编号,拓扑信息,算法程序,加载状态,启动方式,延时启动时间,重复启动次数,运行状态,剩余启动次数)  \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.db.execute(sql, datasample)
        self.conn.commit()
        return datasample[0]

    def delete_controltable(self, tasknum):
        self.reconnect()
        num = str(tasknum)
        sql_delete= "DELETE FROM CONTROL WHERE 任务编号 = " + num
        self.db.execute(sql_delete)
        self.conn.commit()

    def update_controltable(self, tasknum, variables, value):
        self.reconnect()
        num = str(tasknum)
        case = []
        for i in range(len(variables)):
            case.append(str(variables[i])+"= '"+str(value[i])+"'") 
        case = ','.join(case)
        sql_update= "UPDATE CONTROL SET "+case+" WHERE 任务编号 = " + num
        self.db.execute(sql_update)
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

    # 重连
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

if __name__ == '__main__':
    mydb = MyDB()
    # mydb.create_controltable()
    # mydb.delete_controltable(2)
    # mydb.insert_controltable()
    re2 = mydb.show_controltable()