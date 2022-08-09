# 异步SpanningTree 改结束标志

def endflag(end_counter):
    for ele in end_counter:
        if ele == None:
            return 0
    return 1
    
def taskFunction(self,id,adjDirection,datalist):
    # init 
    # 生成树节点标识
    Flag = False  
    # 用于判断计算是否结束的END计数器
    End_Counter = 0
    # 父节点方向
    parent = []
    # 子节点方向
    child = []
    # END计数器初始化为邻居数量
    End_Counter = [None for ele in adjDirection]
    # 本地给不同邻居的数据数组
    data = []

    # id为room_1的为发起节点
    if id == "communication_node":
        Flag = True
        parent.append(0)  # 假定一个0方向，父节点方向为0的即为根节点/发起节点
        for ele in adjDirection:
            self.sendAsynchData(ele,"search")


    while not endflag(End_Counter):
        j,data = self.getAsynchData()
        index = adjDirection.index(j)

        if data == "search":
            End_Counter[index] = "search"
            if Flag == False:
                Flag = True
                parent.append(j)  #将邻居方向加入父节点方向
                # 向其他邻居广播BFS信号
                for ele in adjDirection:
                    if ele != j:
                        self.sendAsynchData(ele,"search")
            # else:
            #     self.sendAsynchData(ele,"refuse")
                       
        # 如果邻居传来join信号
        elif data == "join":
            child.append(j)
            End_Counter[index] = "child"

        elif data == "refuse":
            child.append(j)
            End_Counter[index] = "non_relatives"


        # 如果本轮END计数器减为0
        if endflag(End_Counter):
            self.sendAsynchData(parent[0],"join")
            for ele in adjDirection:
                if ele != parent[0]:
                    self.sendAsynchData(ele,"refuse")     
        self.sendDatatoGUI("{}:{}".format(j,data))

    # 返回父节点方向、子节点方向
    value = {"parent":parent,"child":child}
    return value