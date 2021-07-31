# 时间同步APP
from datetime import datetime

def taskFunction(self, id, adjDirection, datalist):
    TIMEFORMAT = "%Y-%m-%d %H:%M:%S.%f"
    # 子节点向根节点发送数据框架
    if id == "communication_node":
        while True:
            # 阻塞性地获取数据
            path, data, time = self.descendantData.get()
            self.sendDatatoGUI(str([path[0], data]))
            time3 = datetime.now().strftime(TIMEFORMAT)
            self.sendDataToDescendant([data, time, time3], path)

    else:
        time1 = datetime.now().strftime(TIMEFORMAT)
        self.sendDataToRoot(time1)
        # 阻塞性地获取数据
        data, time = self.rootData.get()
        data.append(time)
        timelist = [datetime.strptime(ele,TIMEFORMAT) for ele in data]
        theta = (timelist[1]-timelist[0]+timelist[3]-timelist[2])/2
        real_time = timelist[2]+theta
        settime = real_time.strftime(TIMEFORMAT)
        self.sendDatatoGUI(str([str(theta),time,settime]))

    return 0

"""
[communication_node]TimeSynch: ['room_8', '2021-08-01 03:18:38.806052']
[communication_node]TimeSynch: ['room_7', '2021-08-01 03:18:38.806052']
[communication_node]TimeSynch: ['pump_2', '2021-08-01 03:18:38.806052']
[communication_node]TimeSynch: ['pump_1', '2021-08-01 03:18:38.806052']
[communication_node]TimeSynch: ['room_6', '2021-08-01 03:18:38.806052']
[communication_node]TimeSynch: ['room_5', '2021-08-01 03:18:38.806052']
[communication_node]TimeSynch: ['room_3', '2021-08-01 03:18:38.806052']
[communication_node]TimeSynch: ['heatpump_1', '2021-08-01 03:18:38.806052']
[room_7]TimeSynch: ['0:00:00.001000', '2021-08-01 03:18:38.808052', '2021-08-01 03:18:38.809052']
[room_8]TimeSynch: ['0:00:00', '2021-08-01 03:18:38.808052', '2021-08-01 03:18:38.808052']
[communication_node]TimeSynch: ['room_2', '2021-08-01 03:18:38.806052']
[pump_2]TimeSynch: ['0:00:00.001000', '2021-08-01 03:18:38.809051', '2021-08-01 03:18:38.810051']
[room_7]TimeSynch: 执行完毕
[room_8]TimeSynch: 执行完毕
[communication_node]TimeSynch: ['room_1', '2021-08-01 03:18:38.806052']
[pump_2]TimeSynch: 执行完毕
[pump_1]TimeSynch: ['0:00:00.001500', '2021-08-01 03:18:38.810052', '2021-08-01 03:18:38.811552']
[communication_node]TimeSynch: ['room_4', '2021-08-01 03:18:38.806052']
[room_6]TimeSynch: ['0:00:00.002502', '2021-08-01 03:18:38.812055', '2021-08-01 03:18:38.813554']
[pump_1]TimeSynch: 执行完毕
[room_6]TimeSynch: 执行完毕
[room_5]TimeSynch: ['0:00:00.003001', '2021-08-01 03:18:38.813057', '2021-08-01 03:18:38.815056']
[room_5]TimeSynch: 执行完毕
[heatpump_1]TimeSynch: ['0:00:00.004501', '2021-08-01 03:18:38.816052', '2021-08-01 03:18:38.819552']
[heatpump_1]TimeSynch: 执行完毕
[room_1]TimeSynch: ['0:00:00.005994', '2021-08-01 03:18:38.819055', '2021-08-01 03:18:38.823061']
[room_2]TimeSynch: ['0:00:00.006001', '2021-08-01 03:18:38.819055', '2021-08-01 03:18:38.822053']
[room_3]TimeSynch: ['0:00:00.005502', '2021-08-01 03:18:38.818053', '2021-08-01 03:18:38.819555']
[room_2]TimeSynch: 执行完毕
[room_1]TimeSynch: 执行完毕
[room_3]TimeSynch: 执行完毕
[room_4]TimeSynch: ['0:00:00.007500', '2021-08-01 03:18:38.822054', '2021-08-01 03:18:38.826555']
"""

## 更新时间的获取机制后
"""
[communication_node]TimeSynch: ['room_7', '2021-08-01 03:36:21.270967']
[communication_node]TimeSynch: ['room_8', '2021-08-01 03:36:21.270967']
[communication_node]TimeSynch: ['pump_1', '2021-08-01 03:36:21.270967']
[communication_node]TimeSynch: ['pump_2', '2021-08-01 03:36:21.270967']
[communication_node]TimeSynch: ['room_6', '2021-08-01 03:36:21.270967']
[communication_node]TimeSynch: ['room_5', '2021-08-01 03:36:21.270967']
[communication_node]TimeSynch: ['room_4', '2021-08-01 03:36:21.270967']
[communication_node]TimeSynch: ['room_3', '2021-08-01 03:36:21.270967']
[room_7]TimeSynch: ['0:00:00.000498', '2021-08-01 03:36:21.273967', '2021-08-01 03:36:21.274465']
[room_7]TimeSynch: 执行完毕
[communication_node]TimeSynch: ['heatpump_1', '2021-08-01 03:36:21.270967']
[communication_node]TimeSynch: ['room_2', '2021-08-01 03:36:21.270967']
[room_8]TimeSynch: ['0:00:00.001000', '2021-08-01 03:36:21.275973', '2021-08-01 03:36:21.275969']
[pump_1]TimeSynch: ['0:00:00.000498', '2021-08-01 03:36:21.276966', '2021-08-01 03:36:21.277464']
[communication_node]TimeSynch: ['room_1', '2021-08-01 03:36:21.270967']
[room_8]TimeSynch: 执行完毕
[pump_1]TimeSynch: 执行完毕
[pump_2]TimeSynch: ['0:00:00.000498', '2021-08-01 03:36:21.277973', '2021-08-01 03:36:21.278471']
[pump_2]TimeSynch: 执行完毕
[room_5]TimeSynch: ['0:00:00.002005', '2021-08-01 03:36:21.281976', '2021-08-01 03:36:21.281974']
[room_4]TimeSynch: ['0:00:00.001506', '2021-08-01 03:36:21.281976', '2021-08-01 03:36:21.282474']
[room_2]TimeSynch: ['0:00:00.001502', '2021-08-01 03:36:21.283975', '2021-08-01 03:36:21.284477']
[room_6]TimeSynch: ['0:00:00.002500', '2021-08-01 03:36:21.281976', '2021-08-01 03:36:21.280473']
[room_5]TimeSynch: 执行完毕
[room_3]TimeSynch: ['0:00:00.002001', '2021-08-01 03:36:21.283975', '2021-08-01 03:36:21.283977']
[room_4]TimeSynch: 执行完毕
[heatpump_1]TimeSynch: ['0:00:00.002500', '2021-08-01 03:36:21.284972', '2021-08-01 03:36:21.284476']
[room_2]TimeSynch: 执行完毕
[room_6]TimeSynch: 执行完毕
[room_3]TimeSynch: 执行完毕
[heatpump_1]TimeSynch: 执行完毕
[room_1]TimeSynch: ['0:00:00.001502', '2021-08-01 03:36:21.285974', '2021-08-01 03:36:21.286474']
[room_1]TimeSynch: 执行完毕

"""