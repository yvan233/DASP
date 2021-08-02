def clear_con_db(db, mode):
    cursor = db.cursor()
    sql = "SELECT database()"
    cursor.execute(sql)
    dbname = cursor.fetchall()[0][0]
    sql = '''SELECT 
                    table_name 
                FROM
                    information_schema.TABLES 
                WHERE 
                    table_schema = '%s'
        ''' % (dbname)
    cursor.execute(sql)
    data = cursor.fetchall()
    for l in range(len(data)):
        if mode == 1:
            if data[l][0][-7:] == 'control' or data[l][0][-11:] == 'control_his':
                sql = "TRUNCATE TABLE %s" % (data[l][0])
                cursor.execute(sql)
        elif mode == 2:
            if data[l][0][-7:] == 'control':
                sql = "TRUNCATE TABLE %s" % (data[l][0])
                cursor.execute(sql)
    db.commit()

def db_insert(cursor, table, time, id ,name, value):
    sql = "INSERT INTO %s(time, id ,name, value) VALUES ('%s', '%s', '%s', '%s')" % (table, time, id, name, value)
    cursor.execute(sql)

def db_update(cursor, table, time, name, value):
    sql = "UPDATE %s SET time='%s', value='%s' WHERE name='%s'" % (table, time, value, name)
    cursor.execute(sql)

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

def db_operate(cursor, table, time, id ,name, value):
    db_insert(cursor, table + '_his', time, id, name, value)
    db_insert(cursor, table, time, id, name, value)
    '''
    if step_num == 0:
        db_insert(cursor, table, time, id, name, value)
    else:
        db_update(cursor, table, time, name, value)'''