#coding=utf-8
import pymysql
floorID = 1
room_Num = 16
def controlModel(data):
    db = pymysql.connect(host="39.100.78.210", user="root", passwd="893893", db="syslynkros_v30_qh", charset='utf8')
    cursor = db.cursor()
    for ele in data:
        # print ele
        nID, dllid, nIndex, paracode, t, memindex, memlength, paravalue = ele
        sql = "INSERT INTO modeinfosetvalue(nID, dllid, nIndex, paracode, __t, memindex, memlength, paravalue) VALUES (%s, %s, %s, '%s', %s, %s, %s, %s);" %(nID, dllid, nIndex, paracode, t, memindex, memlength, paravalue)
        cursor.execute(sql)
        db.commit()

def dataForRoom(floorID,roomID):
    roomToNode = [4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34]
    Tset = '002001022'
    Tk = '002001015'
    Tsend = ['001030009', roomToNode[roomID-1]]

    To = '000001001'
    numPeople = '002002004'
    V_room = '002001020'
    Q = '002001017'

    db = pymysql.connect(host="39.100.78.210", user="root", passwd="893893", db="syslynkros_v30_qh", charset='utf8')
    cursor = db.cursor()
    sql = "SELECT %s,%s,%s FROM room_heat32 WHERE nIndex=%s" %('k' + Tset, 'k' + Tk,  'k'+Q, (floorID-1)*16+roomID-1)
    cursor.execute(sql)
    data = cursor.fetchall()
    TsetValue = float(data[0][0])
    TkValue = float(data[0][1])

    QValue = float(data[0][2])

    sql = "SELECT %s FROM modeinfoinit WHERE dllid=%s and nIndex=%s and paracode =%s" % (
    'paravalue', '32', (floorID - 1) * 16 + roomID - 1, V_room)
    cursor.execute(sql)
    data = cursor.fetchall()
    V_roomValue = float(data[0][0])


    sql = "SELECT %s FROM swqx31 WHERE nIndex=0" % ('k' + To)
    cursor.execute(sql)
    data = cursor.fetchall()
    ToValue = float(data[0][0])

    sql = "SELECT %s FROM fgw_heat30 WHERE nIndex=%s" % ('k' + Tsend[0], floorID-1)
    cursor.execute(sql)
    data = cursor.fetchall()
    dataArray = data[0][0].split('|')
    TsendValue = float(dataArray[Tsend[1]-1])



    sql = "SELECT %s FROM room_people33 WHERE nIndex=%s" % ('k' + numPeople, floorID-1)
    cursor.execute(sql)
    data = cursor.fetchall()
    dataArray = data[0][0].split('|')
    numPeopleValue = int(dataArray[roomID-1])

    return TsetValue, TkValue, TsendValue,  V_roomValue, QValue

def dataForVAV(roomID):
    Tset = '002001022'
    Tk = '002001015'
    vav_open = '001005002'
    db = pymysql.connect(host="39.100.78.210", user="root", passwd="893893", db="syslynkros_v30_qh", charset='utf8')
    cursor = db.cursor()
    sql = "SELECT %s FROM vav_con6 WHERE nIndex=%s" % ('k' + Tset, (floorID - 1) * 16 + roomID - 1)
    cursor.execute(sql)
    data = cursor.fetchall()
    return 0

def dataForPID_room(roomID):
    Tset = '002001022'
    Tk = '002001015'
    vav_open = '001005002'
    db = pymysql.connect(host="39.100.78.210", user="root", passwd="893893", db="syslynkros_v30_qh", charset='utf8')
    cursor = db.cursor()
    sql = "SELECT %s,%s FROM room_heat32 WHERE nIndex=%s" % ('k' + Tset, 'k' + Tk, (floorID - 1) * 16 + roomID - 1)
    cursor.execute(sql)
    data = cursor.fetchall()
    TsetValue = float(data[0][0])
    TkValue = float(data[0][1])
    sql = "SELECT %s FROM vav_act5 WHERE nIndex=%s" % ('k' + vav_open, (floorID - 1) * 16 + roomID - 1)
    cursor.execute(sql)
    data = cursor.fetchall()
    vav_openValue = float(data[0][0])

    return TsetValue, TkValue, vav_openValue

def dataForPID_AHU(floorID):
    P_measure = ['001029008', 13]
    P_setValue = 220
    n = '001023010'
    T_send = '001022008'
    T_set = '001024020'
    vav_open = '001023013'
    db = pymysql.connect(host="39.100.78.210", user="root", passwd="893893", db="syslynkros_v30_qh", charset='utf8')
    cursor = db.cursor()

    sql = "SELECT %s FROM kongtx22 WHERE nIndex=%s" % ('k' + T_send, (floorID - 1))
    cursor.execute(sql)
    data = cursor.fetchall()
    T_sendValue = float(data[0][0])

    sql = "SELECT %s FROM kongtx_con24 WHERE nIndex=%s" % ('k' + T_set, (floorID - 1))
    cursor.execute(sql)
    data = cursor.fetchall()
    T_setValue = float(data[0][0])

    sql = "SELECT %s FROM fgw29 WHERE nIndex=%s" % ('k' + P_measure[0], floorID - 1)
    cursor.execute(sql)
    data = cursor.fetchall()
    dataArray = data[0][0].split('|')
    P_measureValue = float(dataArray[P_measure[1] - 1])

    sql = "SELECT %s,%s FROM kongtx_act23 WHERE nIndex=%s" % ('k' + n, 'k' + vav_open, (floorID - 1))
    cursor.execute(sql)
    data = cursor.fetchall()
    nValue = float(data[0][0])
    vav_openValue = float(data[0][1])

    return P_measureValue, P_setValue, nValue, T_sendValue, T_setValue, vav_openValue

if __name__ == "__main__":
    TsetValue, TkValue, ToValue, TsendValue, numPeopleValue = dataForRoom(1,1)
    # print TsetValue, TkValue, ToValue, TsendValue, numPeopleValue