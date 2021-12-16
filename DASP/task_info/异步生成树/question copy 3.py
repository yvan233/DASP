def taskFunction(self,id,adjDirection,datalist):
    # init 
    min_uid = id
    # 生成树节点标识
    Flag = False 
    # 父节点方向
    parent = []
    # 子节点方向
    child = []
    # 用于判断计算是否结束的END计数器，初始化为邻居数量
    End_Counter = len(adjDirection)

    # 无发起节点
    Flag = True
    parent.append(0)  # 假定一个0方向，父节点方向为0的即为根节点/发起节点
    for ele in adjDirection:
        self.sendAsynchData(ele,["search",id])


    while End_Counter > 0:
        j,info = self.getAsynchData()
        data,token = info
        # 如果邻居传来join信号
        if data == "join":
            End_Counter = End_Counter-1
            child.append(j)
        # 如果传来search信号
        else:
            # 忽略token比自己大的消息
            if token > min_uid:
                continue
            # 如果token比自己小改变自己的min_uid
            elif token < min_uid:
                min_uid = token
                Flag = False
                parent = []
                End_Counter = len(adjDirection)-len(child)
            # token一样，正常操作
            else:
                pass
            
            End_Counter = End_Counter-1
            if Flag == False:
                Flag = True
                parent.append(j)  #将邻居方向加入父节点方向
                # 向其他邻居广播BFS信号
                for ele in adjDirection:
                    if ele != j:
                        self.sendAsynchData(ele,["search",min_uid])
                # else:
                #     self.sendAsynchData(ele,"refuse")
                    

        # 如果本轮END计数器减为0
        if End_Counter == 0:
            # self.sendDatatoGUI("send:{}:{}".format(parent[0],["join",min_uid]))
            self.sendAsynchData(parent[0],["join",min_uid])
        self.sendDatatoGUI("recv:{}:{}".format(j,info))

    if min_uid == id:
        leader_state = "leader"
    else:
        leader_state = "non-leader"
    # 返回父节点方向、子节点方向
    value = {"leader_state":leader_state,"parent":parent,"child":child}
    return value