import pymysql
Default_Config= {
'user': 'root',
'password': 'DSPadmin',
}
class DASPmysql:
    host = "127.0.0.1"
    port = 3306
    database = 'DASPdb'
    def __init__(self, config = Default_Config):
        self.user = config['user']
        self.password = config['password']
        self.connection = pymysql.connect(host=self.host,
                                          port=self.port,
                                          user=self.user,
                                          password=self.password,
                                          charset='utf8mb4'
                                          )
        self.cursor = self.connection.cursor()
        self.use_database()

    def use_database(self):
        """使用DASPdb数据库
        """
        # 创建数据库
        sql = "CREATE DATABASE IF NOT EXISTS {}".format(self.database)
        self.cursor.execute(sql)
        sql = "USE {}".format(self.database)
        self.cursor.execute(sql)

    def is_connected(self):
        """判断数据库连接是否存在，如果断开则重连
        """
        try:
            self.connection.ping()
        except Exception:
            self.connection = pymysql.connect(host=self.host,
                                            port=self.port,
                                            user=self.user,
                                            password=self.password,
                                            charset='utf8mb4'
                                            )
            self.cursor = self.connection.cursor()
            self.use_database()

    def create_debug_table(self, tablename, ObservedVariable):
        """创建调试数据表
        """
        var_list = [m + ' VARCHAR(255),' for m in ObservedVariable]
        var_list = ''.join(var_list)
        self.is_connected()
        sql_drop = "DROP TABLE IF EXISTS `{}`" .format(tablename)
        self.cursor.execute(sql_drop)
        sql_create = """CREATE TABLE `{}` (
                id INT NOT NULL AUTO_INCREMENT,
                time VARCHAR(255),
                code VARCHAR(255),
                codeline VARCHAR(255),
                {}
                PRIMARY KEY ( id )  )character set = utf8""".format(tablename, var_list)
        self.cursor.execute(sql_create)
        self.connection.commit()


    def insert_table(self, tablename, observelist, name, value, code, codeline):
        self.is_connected()
        name = str(name)
        value = str(value).replace("'","")
        code = str(code).replace("'","")
        codeline = str(codeline)
        
        refuselist = ["args","kwargs","function","self"]
        if name in refuselist:
            return 0
        if observelist:
            if name not in observelist:
                return 0

        # 获取列名
        self.cursor.execute("SHOW COLUMNS from `" + tablename + "`")
        answer = self.cursor.fetchall()
        columns = [column[0] for column in answer]


        # 开始插入，复制上一行，只把name值改为value
        sql_select = "select * from `%s` order by id desc limit 1;" % (tablename)
        self.cursor.execute(sql_select)
        record_last = self.cursor.fetchone()
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
        ls2 = ls2.replace("'None'","Null")

        sql_insert = "INSERT INTO " + tablename + "(code, codeline, " \
            + ls1 + ") VALUES ('"+ code +"','" + codeline + "'," + ls2 + ")"   
        self.cursor.execute(sql_insert)
        self.connection.commit()

    def delete_table(self, tablename):
        """删除数据表
        """
        self.is_connected()
        sql_drop = "DROP TABLE IF EXISTS `{}`" .format(tablename)
        self.cursor.execute(sql_drop)  
        self.connection.commit()

    def show_tables(self):
        """显示所有数据表
        """
        self.is_connected()
        self.cursor.execute("SHOW TABLES")
        answer = self.cursor.fetchall()
        columns = [column[0] for column in answer]
        columns.insert(0,"Tables_in_{}".format(self.database))
        self.connection.commit()
        return columns

    def show_table(self, tablename):
        """显示数据表的数据
        """
        self.is_connected()
        # 获取列名
        sql_columns = "SHOW COLUMNS FROM `{}`".format(tablename)
        self.cursor.execute(sql_columns)
        answer = self.cursor.fetchall()
        columns = [column[0] for column in answer]

        sql_select = "SELECT * FROM `{}`".format(tablename)
        self.cursor.execute(sql_select)   
        rows = self.cursor.fetchall()
        rows = [list(ele) for ele in rows]
        result = [columns,rows]
        self.connection.commit()
        return result


    def create_run_table(self, num, info):
        self.is_connected()
        sql_create = """CREATE TABLE IF NOT EXISTS RUNTASK%s (
                id INT NOT NULL AUTO_INCREMENT,
                运行信息 VARCHAR(20000),
                PRIMARY KEY ( id )  )character set = utf8""" %(num)
        self.cursor.execute(sql_create)

        sql = "INSERT INTO RUNTASK%s (运行信息) VALUES (%s)"
        val = [num,info]
        self.cursor.execute(sql, val)
        self.connection.commit()

    def create_controltable(self):
        self.is_connected()
        # 先不删除旧表
        # sql_drop = "DROP TABLE IF EXISTS CONTROL" 
        # self.cursor.execute(sql_drop)
        sql_create = """CREATE TABLE IF NOT EXISTS CONTROL (
                id INT NOT NULL AUTO_INCREMENT,
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
                PRIMARY KEY ( id )  )character set = utf8"""
        self.cursor.execute(sql_create)
        self.cursor.execute('select * from CONTROL')
        row = self.cursor.fetchall()
        if not row:
            sql = "INSERT INTO CONTROL (任务编号,拓扑信息,算法程序,加载状态,启动方式,延时启动时间,重复启动次数,调试模式开关,查看变量名,运行状态,剩余启动次数,用户名)  \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = ['0','1','系统任务','1','0','0.0','-1','0'," ",'0','-1', 'root']
            self.cursor.execute(sql, val)
        self.connection.commit()

    def insert_controltable(self, taskusername = 'root'):
        self.is_connected()
        datasample = ['0','0',' ','0','0','0.0','1','0',"",'0','0', taskusername]
        sql_select = "select * from CONTROL order by id desc limit 1"
        self.cursor.execute(sql_select)
        record_last = self.cursor.fetchone()
        datasample[0] = str(int(record_last[1])+1)
        sql = "INSERT INTO CONTROL (任务编号,拓扑信息,算法程序,加载状态,启动方式,延时启动时间,重复启动次数,调试模式开关,查看变量名,运行状态,剩余启动次数,用户名)  \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(sql, datasample)
        self.connection.commit()
        return datasample[0]

    def delete_controltable(self, tasknum, taskusername = 'root'):
        self.is_connected()
        num = str(tasknum)
        sql_delete= "delete from CONTROL where 任务编号 = " + num
        self.cursor.execute(sql_delete)
        self.connection.commit()

    def update_controltable(self, tasknum, variables, value,  taskusername = 'root'):
        self.is_connected()
        num = str(tasknum)
        case = []
        for i in range(len(variables)):
            case.append(str(variables[i])+"= '"+str(value[i])+"'") 
        case = ','.join(case)

        sql_update= "UPDATE CONTROL SET "+case+" WHERE 任务编号 = " + num
        self.cursor.execute(sql_update)
        self.connection.commit()

    def insert_usertable(self, name, password):
        self.is_connected()
        sql = "INSERT INTO USER (name, password) VALUES (%s, %s)"
        val = [name, password]
        self.cursor.execute(sql, val)
        self.connection.commit()

    def show_runtable(self, tablename, lastrecordid):
        self.is_connected()
        # 获取列名
        try:
            sql_max = "select max(id) from `%s`" % (tablename)
            self.cursor.execute(sql_max)  
            maxid = self.cursor.fetchone()
            sql_select = "select * from `%s` where id > %s " % (tablename, lastrecordid)
            self.cursor.execute(sql_select)  
            rows = self.cursor.fetchall()
            row = self.cursor.rowcount
            self.connection.commit()
            result = []
            for i in range(row):
                result_line = rows[i][1]
                result.append(result_line)
            return result,maxid[0]
        except Exception:
            return [],lastrecordid

    def apply_permission(self, dllid,nIndex,paracode,username = 'root'):
        self.is_connected()
        sql_select = "select * from permission where dllid = %s AND nIndex >= %s AND nIndex <= %s AND paracode = %s"
        data = (dllid,nIndex[0],nIndex[1],paracode)
        self.cursor.execute(sql_select,data)  
        rows = self.cursor.fetchall()
        row = self.cursor.rowcount
        namelist = []

        if not row:
            for i in range(nIndex[0],nIndex[1]+1):
                sql_insert = "INSERT INTO permission (dllid,nIndex,paracode,上传用户) VALUES (%s,%s,%s,%s)"
                data = (dllid,i,paracode,username)
                self.cursor.execute(sql_insert,data)
        else:
            for item in rows:
                if item[4] not in namelist:
                    namelist.append(item[4])
        self.connection.commit()
        return namelist

    def cancel_permission(self, dllid,nIndex,paracode,username = 'root'):
        self.is_connected()
        if username == 'root':
            for i in range(nIndex[0],nIndex[1]+1):
                sql_insert = "DELETE FROM permission WHERE dllid = %s AND nIndex = %s AND paracode = %s"
                data = (dllid,i,paracode)
                self.cursor.execute(sql_insert,data)
        else:
            for i in range(nIndex[0],nIndex[1]+1):
                sql_insert = "DELETE FROM permission WHERE dllid = %s AND nIndex = %s AND paracode = %s AND 上传用户 = %s"
                data = (dllid,i,paracode,username)
                self.cursor.execute(sql_insert,data)
        self.connection.commit()


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

if __name__ == '__main__':

    ObservedVariable = ["x", "m"]

    db = DASPmysql()
    # db.create_debug_table('test' , ObservedVariable)
    print(db.show_tables())
    table = db.show_table('default_node_1')
    print(table)