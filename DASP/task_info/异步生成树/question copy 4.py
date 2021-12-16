# 求leader 改endflag

def endflag(end_counter):
    for ele in end_counter:
        if ele == None:
            return 0
    return 1


def taskFunction(self,id,adjDirection,datalist):
    # init 
    min_uid = id
    # 生成树节点标识
    flag = False 
    # 父节点方向
    parent = []
    # 子节点方向
    child = []
    # 非父子关系
    non_relatives = []
    # 用于判断计算是否结束的END计数器，初始化为邻居数量
    end_counter = [None for ele in adjDirection]

    # 无发起节点
    flag = True
    parent.append(0)  # 假定一个0方向，父节点方向为0的即为根节点/发起节点
    for ele in adjDirection:
        self.sendAsynchData(ele,["search",id])


    while not endflag(end_counter):
        j,info = self.getAsynchData()
        index = adjDirection.index(j)
        data,token = info
        # 如果邻居传来join信号
        if data == "join":
            end_counter[index] = "child"
            child.append(j)
        elif data == "refuse":
            end_counter[index] = "non_relatives"
            non_relatives.append(j)
        # 如果传来search信号
        else:
            # 忽略token比自己大的消息
            if token > min_uid:
                continue
            # 如果token比自己小改变自己的min_uid
            elif token < min_uid:
                min_uid = token
                flag = False
                parent = []
                for ele in end_counter:
                    if ele == "parent":
                        ele = None
            # token一样，正常操作
            else:
                pass
            
            if flag == False:
                flag = True
                end_counter[index] = "parent"
                parent.append(j)  #将邻居方向加入父节点方向
                # 向其他邻居广播BFS信号
                for ele in adjDirection:
                    if ele != j:
                        self.sendAsynchData(ele,["search",min_uid])
                    
        # 如果本轮END计数器减为0
        if endflag(end_counter):
            self.sendAsynchData(parent[0],["join",min_uid])
            for ele in adjDirection:
                if ele != parent[0]:
                    self.sendAsynchData(ele,["refuse",min_uid])        
        self.sendDatatoGUI("recv:{}:{}".format(j,info))

    if min_uid == id:
        leader_state = "leader"
    else:
        leader_state = "non-leader"
    # 返回父节点方向、子节点方向
    value = {"state":leader_state,"parent":parent,"child":child}
    self.sendDatatoGUI(str(value))
    return value