import copy
import time
def taskFunction(self,id,adjDirection,datalist, tasknum):
    # init
    Flag = False                        # 生成树节点标识
    End_Counter = 0                     # 用于判断计算是否结束的END计数器
    parentdirection = []                # 父节点方向
    childdirection = []                 # 子节点方向
    End_Counter = len(adjDirection)     # END计数器初始化为邻居数量
    data_base = [0,False,0]             # 与邻居通信的数据格式，分别为邻居的方向、BFS信号、END信号
    data = []                           # 本地给不同邻居的数据数组  

    # 初始化data
    for i in range(len(adjDirection)):
        data_base_temp = [0,False,0]
        data_base_temp[0] = adjDirection[i]
        data.append(data_base_temp)

    # id为1-1的为发起节点
    if id == "communication_node":
        Flag = True
        parentdirection.append(0)       # 假定一个0方向，父节点方向为0的即为根节点/发起节点
        for i in range(len(data)):
            data[i][1] = True           # 给每个邻居发送BFS信号  

    # 循环次数为网络宽度的2倍，9  *2 = 18
    for m in range(18):
        # time.sleep(1)
        transdata = [one[1:] for one in data]                       # 只传给邻居BFS和END信号
        adjDirection_fb,adjData_fb = self.transmitData(adjDirection, transdata, tasknum)    # 获取邻居传输的数据       
        for i in range(len(data)):                                  
            data[i][1] = False                                      # 清空BFS、END信号
            data[i][2] = 0        
        if  End_Counter != 0:                                       # 如果END计数器不为0
            for i in range(len(adjData_fb)):
                if adjData_fb[i][0] == True:                        # 如果邻居传来BFS信号
                    if Flag == False:                               # 如果本节点没有加入宽度优先生成树中      
                        Flag = True
                        parentdirection.append(adjDirection_fb[i])  #将邻居方向加入父节点方向
                        for j in range(len(data)):                  # 向其他邻居广播BFS信号
                            if data[j][0] != adjDirection_fb[i]:
                                data[j][1] = True
                    End_Counter = End_Counter - 1                   
                if  adjData_fb[i][1] > 0:                           # 如果邻居传来END信号
                    End_Counter = End_Counter - 1
                    if adjData_fb[i][1] == 2:                       # END = 2 说明是该节点的子节点，将邻居方向加入父节点方向数组
                        childdirection.append(adjDirection_fb[i])            
            if End_Counter == 0:                                    # 如果本轮END计数器减为0
                for i in range(len(data)):
                    data[i][1] = False
                    if data[i][0] == parentdirection[0]:            # 给父节点方向的邻居发送END = 2
                        data[i][2] = 2
                    else:                                           # 给其他邻居发送END = 1
                        data[i][2] = 1
                        
        self.sendUDP("任务" + str(tasknum)  +" 第" + str(m+1) + "步完成",tasknum)

    value = [parentdirection,childdirection]                        # 返回父节点方向、子节点方向
    return value