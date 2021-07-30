# 智能电表读取脚本

from pymodbus.client.sync import ModbusSerialClient as ModbusClient

import struct
import time

if __name__ == "__main__":
    step = 0
    client1 = ModbusClient(method='rtu', port='/dev/ttyUSB1', timeout=1, stopbits = 1, bytesize = 8,  parity='N', baudrate= 9600)
    client1.connect()
    
    step = 0
    while True:
        print("-------------------------------------------------------------")
        print("step = " + str(step))
        try:
            rr = client1.read_holding_registers(address=79, count=12, unit=7)
            data = rr.registers
            # 有功功率
            ActivePower = data[3]*20/100   
            time.sleep(1)
            # 无功功率
        except:
            ReactivePower = data[7]*20/100
            # 视在功率
            ApparentPower = data[11]*20/100
            print("ActivePower: ", ActivePower) 
            print("ReactivePower: ", ReactivePower)
            print("ApparentPower: ", ApparentPower)
                        
            print("Power err")
        
        try:
            rr2 = client1.read_holding_registers(address=99, count=12, unit=7)
            data = rr2.registers
            # 总有功电能
            ActiveEnergy = int(str(data[0])+str(data[1]))*20/100
            # 总无功电能
            ReactiveEnergy = int(str(data[6])+str(data[7]))*20/100
            print("ActiveEnergy: ", ActiveEnergy)
            print("ReactiveEnergy: ", ReactiveEnergy)
            time.sleep(1)
        except:
            print("Energy err")
        

        step += 1
        time.sleep(60)

