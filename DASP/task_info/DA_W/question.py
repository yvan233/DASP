import numpy
import time
import sys
sys.path.insert(1,".")  # 把上一级目录加入搜索路径
from DASP.task_info.DA_W.SimulationInterface_local1 import dataForRoom,controlModel
from sympy import *
from scipy.optimize import minimize
import copy
def coldLoadToG(V_room,T_set,T_k,T_send,Q,delt_t):
    m = V_room*1.29
    c = 1000.0
    rou = 1.29
    Q = Q /60 * 1000
    G = (m*T_set-float(delt_t*(Q))/c-m*T_k)/(delt_t*rou*(T_send-T_k))
    return G

def cal_n(sumGi,equ_S):
    a = 2395.4
    b = -101.16
    c = -12.96
    nd = 50.0 # 额定频率
    n = 0
    deltaP = equ_S*sumGi**2  # 总压力 pa
    omiga = (-b*sumGi+sqrt((b*sumGi)**2-4*a*(c*sumGi**2-deltaP)))/(2*a)
    n = omiga*nd
    return n

def calTheta(S):
    ai = 0.0027
    bi = 0.0092
    ci = 0.0249
    x = symbols("x")
    F = 1 / (ai * (x) + bi * (x) ** 2 + ci * (x) ** 3) ** 2 - S
    F_1 = diff(F,x)
    MAXSTEP = 100
    step_count = 0
    x0 = 1/S
    F_value = float(F.subs(x,x0))
    while step_count < MAXSTEP and abs(F_value) > 1e-6:
        F_1_value = float(F_1.subs(x,x0))
        x0 = x0 - F_value / F_1_value
        F_value = float(F.subs(x, x0))
        step_count += 1
        print (x0)
    return x0

def calS(theta):
    ai = 0.0027
    bi = 0.0092
    ci = 0.0249
    x = symbols("x")
    F = 1 / (ai * (x) + bi * (x) ** 2 + ci * (x) ** 3) ** 2
    return float(F.subs(x,theta))

# 目标函数：
def func1(alpha,lam,lam_u,lam_d,z_u,z_d,z):
    fun = lambda x: x[0] + alpha/2.0 * ((x[1] - z_u + lam_u) ** 2 + (x[2] - z_d + lam_d)**2+(x[0] - z +lam)**2)
    return fun

# 目标函数：
def func3(alpha,lam,lam_u,lam_d,z_u,z_d,z):
    fun = lambda x: x[0] + alpha/2.0 * ((x[1] - z_u + lam_u) ** 2 + (x[2] - z_d + lam_d)**2+(x[0] - z +lam)**2)
    return fun

# 目标函数：
def func2(alpha,lam,lam_u,z_u,z):
    fun = lambda x: x[0] + alpha/2.0 *((x[1] - z_u+lam_u) ** 2+(x[0] - z + lam)**2)
    return fun

# 约束条件，包括等式约束和不等式约束
def con1(S1,S2,G,Gu,Gus,Gd,Gds):
    cons = ({'type': 'ineq', 'fun': lambda x: x[0] - 738.42155},
            {'type': 'ineq', 'fun': lambda x: x[1] - 738.42155},
            {'type': 'ineq', 'fun': lambda x: x[2] - 738.42155},
            {'type': 'eq', 'fun': lambda x: (S1 + x[0]) * G ** 2 - S2 * Gds ** 2 - (S1 + x[2]) * Gd ** 2},
            {'type': 'eq', 'fun': lambda x: (S1 + x[1]) * Gu ** 2 - S2 * Gus ** 2 - (S1 + x[0]) * G ** 2})
    return cons

# 约束条件，包括等式约束和不等式约束
def con2(S1,S2,G,Gu,Gus):
    cons = ({'type': 'ineq', 'fun': lambda x: x[0] - 738.42155},
            {'type': 'ineq', 'fun': lambda x: x[1] - 738.42155},
            {'type': 'eq', 'fun': lambda x: (S1 + x[1]) * Gu ** 2 - S2 * Gus ** 2 - (S1 + x[0]) * G ** 2})
    return cons

# 约束条件，包括等式约束和不等式约束
def con3(S1,S2,G,Gu,Gus,Gus_2,Gd,Gds):
    cons = ({'type': 'ineq', 'fun': lambda x: x[0] - 738.42155},
            {'type': 'ineq', 'fun': lambda x: x[1] - 738.42155},
            {'type': 'ineq', 'fun': lambda x: x[2] - 738.42155},
            {'type': 'eq', 'fun': lambda x: (S1+x[0])*G**2 - S2*Gds**2 - (S1+x[2])*Gd**2},
            {'type': 'eq', 'fun': lambda x: (S1+x[1])*Gu**2 + S2*Gus_2**2 - S2*Gus**2 - (S1+x[0])*G**2})
    return cons


def taskFunction(self,id,adjDirection,datalist):
    theta = 0
    start = time.time()
    # M = 100 * 100 #罚因子
    Gm = 1600.0 / 3600.0
    S1, S2 = 1.5, 2.0
    delt_t = 420.0
    room_id = id
    floorID = 5
    uID = self.TaskadjID[0]
    alpha = 0.00
    if len(self.TaskadjID) == 2:
        dID = self.TaskadjID[1]
    else:
        dID = 0
    start = 0
    k1 = 0
    X1 = 7000.0
    XU = 7000.0
    XD = 7000.0
    L1 = 15.0
    LU = 15.0
    LD = 15.0
    while 1:
        time.sleep(0.32)
        end = time.time()
        if end - start > 120:
            k1 = k1 + 1
            self.sendDatatoGUI("  k :" + str(k1))
            for i in range(len(self.TaskadjID)):
                self.adjData[i] = []
            start = end
            self.syncNode()
            T_set, T_k, T_send, V_room, Q = dataForRoom(floorID, room_id)
            G = coldLoadToG(V_room,T_set,T_k,T_send,Q,delt_t)
            if G < 0.01:
                G = 0.01
            if G > Gm * 1.5:
                G = Gm * 1.5

            if dID == 0:
                Gus = G
                Gds = 0
                Gd = 0
                self.sendDataToID(uID, [G,Gus])
            else:
                while 1:
                    tmp = 0
                    for i in range(len(self.TaskadjID)):
                        if (self.TaskadjID[i] == dID):
                            if self.adjData[i] != []:
                                dData = self.adjData[i]
                                tmp = 1
                                break
                    if tmp == 1:
                        Gd = dData[0]
                        Gds = dData[1]
                        Gus = Gds + G
                        self.sendDataToID(uID,[G,Gus])
                        self.sendDataToID(dID, [G])
                        break
                    time.sleep(0.02)

            while 1:
                tmp1 = 0
                for i in range(len(self.TaskadjID)):
                    if (self.TaskadjID[i] == uID):
                        if self.adjData[i] != []:
                            uData = self.adjData[i]
                            tmp1 = 1
                            break
                if tmp1 == 1:
                    if datalist["status"] == 3:
                        Gu = uData[0]
                        Gus_2 = uData[1]
                    else:
                        Gu = uData[0]
                        Gus_2 = 0
                    for i in range(len(self.TaskadjID)):
                        self.adjData[i] = []
                    break
                time.sleep(0.02)
            # time.sleep(0.32)
            self.syncNode()
            M = 100 / G**4 / 2

            X_value = numpy.zeros(3)
            if len(self.TaskadjID) == 2:
                X_value = [X1, XU, XD]
            else:
                X_value = [X1, XU, 0.0]

            if len(self.TaskadjID) == 2:
                xu_value = X_value[0]
                x_value = X_value[1]
                xd_value = X_value[2]
            else:
                xu_value = X_value[0]
                x_value = X_value[1]
                xd_value = X_value[2]
            # C = []
            x, xu, xd = symbols("x,xu,xd")

            mu1, lambda1 = symbols("mu,lambda1")
            S, Su, Sd = x, xu, xd
            if datalist["status"] == 1:
                F = abs((S1 + S) * G ** 2 - S2 * Gds ** 2 - (S1 + Sd) * Gd ** 2) + abs(
                        (S1 + Su) * Gu ** 2 - S2 * Gus ** 2 - (S1 + S) * G ** 2)
            elif datalist["status"] == 2:
                F = abs((S1 + Su) * Gu ** 2 - S2 * Gus ** 2 - (S1 + S) * G ** 2)
            elif datalist["status"] == 3:
                F = abs((S1 + S) * G ** 2 - S2 * Gds ** 2 - (S1 + Sd) * Gd ** 2) + abs(
                        (S1 + Su) * Gu ** 2 + S2 * Gus_2 ** 2 - S2 * Gus ** 2 - (S1 + S) * G ** 2)
            zeta = 0.01
            Flag = 0
            # alpha = 0.1
            alpha = 2
            m = 0
            l = 10
            z = X1
            z_u = XU
            z_d = XD
            lam = L1
            lam_u = LU
            lam_d = LD
            X_send = numpy.zeros(3)
            X_send = X_value
            xu_value_Neb = 0
            xd_value_Neb = 0
            x1_Neb = 0
            x2_Neb = 0
            while(m < 800):
                m = m + 1
                print (m)
                if datalist["status"] == 1:
                    Fun = func1(alpha,lam,lam_u,lam_d,z_u,z_d,z)
                    con = con1(S1,S2,G,Gu,Gus,Gd,Gds)
                    res = minimize(Fun, X_value, method='SLSQP', constraints=con)
                    X_value = res.x
                    y_value = res.fun
                elif datalist["status"] == 2:
                    Fun = func2(alpha,lam,lam_u,z_u,z)
                    con = con2(S1,S2,G,Gu,Gus)
                    res = minimize(Fun, X_value, method='SLSQP', constraints=con)
                    X_value = res.x
                    y_value = res.fun
                elif datalist["status"] == 3:
                    Fun = func3(alpha,lam,lam_u,lam_d,z_u,z_d,z)
                    con = con3(S1,S2,G,Gu,Gus,Gus_2,Gd,Gds)
                    res = minimize(Fun, X_value, method='SLSQP', constraints=con)
                    X_value = res.x
                    y_value = res.fun
                if len(self.TaskadjID) == 2:
                    xu_value = X_value[1]
                    x_value = X_value[0]
                    xd_value = X_value[2]
                else:
                    xu_value = X_value[1]
                    x_value = X_value[0]
                    xd_value = 0
                X_send = [[xu_value, x_value, xd_value]]*len(adjDirection)
                data = copy.deepcopy(self.transmitData(adjDirection, X_send))
                if len(self.TaskadjID) == 2:
                    if id == 9 or id == 1:
                        x1_Neb = data[1][0][0]
                        x2_Neb = data[1][1][0]
                    else:
                        x1_Neb = data[1][0][2]
                        x2_Neb = data[1][1][0]
                    z = (x1_Neb + x2_Neb + x_value)/3.0
                    lam = lam + (x_value-z)
                else:
                    x1_Neb = data[1][0][2]
                    x2_Neb = 0
                    z = (x1_Neb + x_value) / 2.0
                    z_d = 0.0
                    lam = lam + (x_value - z)
                Z_send = numpy.zeros(1)
                Z_send = [[z]]*len(adjDirection)
                #
                data = copy.deepcopy(self.transmitData(adjDirection, Z_send))
                if len(self.TaskadjID) == 2:
                    z_u = data[1][0][0]
                    z_d = data[1][1][0]
                    # lam = lam + alpha*(x_value-z)
                    lam_u = lam_u + (xu_value - z_u)
                    lam_d = lam_d + (xd_value - z_d)
                else:
                    z_u = data[1][0][0]
                    z_d = 0.0
                    lam_u = lam_u + (xu_value - z_u)
                reps = [(xu, z_u), (xd, z_d), (x, z)]
                F_value = float(F.subs(reps))
                constraint = F_value

            self.sendDatatoGUI("X_value: " + str(X_value))
            self.sendDatatoGUI("constraint :" + str(constraint))
            writeData = []
            X1,XU,XD = x_value,xu_value,xd_value
            L1,LU,LD = lam,lam_u,lam_d
            R = G/Gm

            sumG, numRoom, ESR = G, 16.0, x_value + S1
            son = self.sonID
            parent = self.parentID
            if son == []:
                self.sendDataToID(parent, [sumG,ESR])
            else:
                while 1:
                    tmp = 1
                    for i in range(len(self.sonID)):
                        for j in range(len(self.TaskadjID)):
                            if self.sonID[i] == self.TaskadjID[j]:
                                if self.adjData[j] == []:
                                    tmp = 0
                                    break
                    if tmp == 1:
                        for i in range(len(self.sonID)):
                            for j in range(len(self.TaskadjID)):
                                if self.sonID[i] == self.TaskadjID[j]:
                                    sumG += self.adjData[j][0]
                        if parent != id:
                            for i in range(len(self.sonID)):
                                for j in range(len(self.TaskadjID)):
                                    if self.sonID[i] == self.TaskadjID[j]:
                                        ESR = (1/(1 / (self.adjData[j][1]+2.0) ** 0.5 + 1 / ESR ** 0.5)) ** 2
                            # self.sendDatatoGUI("ESR:" + str(ESR)+ " id: " + str(id))
                            self.sendDataToID(parent,[sumG,ESR])
                        else:
                            for i in range(len(self.sonID)):
                                if self.sonID[i] == dID:
                                    ESR = (1/(1 / (self.adjData[i][1]+2.0) ** 0.5 + 1 / ESR ** 0.5)) ** 2
                            # self.sendDatatoGUI("ESR:" + str(ESR) + " id: " + str(id))
                            for i in range(len(self.sonID)):
                                if self.sonID[i] == uID:
                                    ESR = (1 / (1 / (self.adjData[i][1] + 2.5) ** 0.5+ 1 / (ESR+2.5) ** 0.5)) ** 2
                            # self.sendDatatoGUI("ESR:" + str(ESR) + " id: " + str(id))
                            totalESR = ESR + 16.4
                            n = cal_n(sumG, totalESR)
                            self.sendDatatoGUI("n:" + str(n))
                            if n < 20:
                                n = 20
                            if n > 50:
                                n = 50
                            writeData.append([160 + floorID, 24, floorID-1, '001024015', 0, 0, 1, n])
                            self.sendDatatoGUI("sumG:" + str(sumG))
                        break
                    time.sleep(0.01)
            theta = calTheta(x_value) * 100
            if theta >= 100:
                theta = theta - 0.001
            self.sendDatatoGUI(str(theta))
            writeData.append([(floorID - 1) * 16 + room_id, 6,(floorID - 1) * 16+ room_id-1, '001006010', 0, 0, 1, theta])
            # controlModel(writeData)
            # return theta