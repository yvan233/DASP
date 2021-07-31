# 测试后代节点向根节点发送数据，根节点向后代节点发送数据函数

import time
def taskFunction(self, id, adjDirection, datalist):
    ## 子节点向根节点发送数据框架
    # if id == "room_1":
    #     while True:
    #         # 阻塞性地获取数据
    #         path, data = self.descendantData.get()
    #         data.append(id)
    #         self.sendDatatoGUI(str([path, data]))
    #         self.sendDataToDescendant(data, path)

    # else:
    #     self.sendDataToRoot([id,adjDirection])
    #     # 阻塞性地获取数据
    #     data = self.rootData.get()
    #     self.sendDatatoGUI(str(data))

    # 根节点广播数据框架
    if id == "room_1":
        self.sendDataToDescendant("test connected")
        while True:
            # 阻塞性地获取数据
            path, data = self.descendantData.get()
            self.sendDatatoGUI(str([path, data]))
        
    else:
        # 阻塞性地获取数据
        data = self.rootData.get()
        self.sendDatatoGUI(str(data))
        self.sendDataToRoot(id+" received")
    return 0