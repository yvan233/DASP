# 无根节点的生成树
import datetime,time

def taskFunction(self,id,adjDirection,datalist):
    # init 
    min_uid = id
    # 生成树节点标识
    flag = False 
    # 父节点方向
    parent = []
    # 子节点方向
    child = []
    # 用于判断计算是否结束的END计数器，初始化为邻居数量
    end_counter = len(adjDirection)

    # 无发起节点
    flag = True
    parent.append(0)  # 假定一个0方向，父节点方向为0的即为根节点/发起节点
    for ele in adjDirection:
        self.sendAsynchData(ele,["search",id])

    starttime = datetime.datetime.now()
    message_cnt = 0  #消息总数

    while True:
        j,(data,token) = self.getAsynchData()
        message_cnt += 1
        # self.sendDatatoGUI("recv from {}:[{},{}]".format(j,data,token))

        # 忽略token比自己大的消息
        if token > min_uid:
            continue
        # 如果token比自己小改变自己的min_uid
        elif token < min_uid:
            min_uid = token
            flag = False
            parent = []
            child = []
            end_counter = len(adjDirection)
        # token一样，正常操作
        else:
            pass
       
        if data == "end" and j == parent[0]:
            for ele in child:
                self.sendAsynchData(ele,["end",min_uid]) 
            break

         # 如果邻居传来join信号
        elif data == "join":
            end_counter = end_counter - 1
            child.append(j)
        # search
        else:
            end_counter = end_counter - 1
            if flag == False:
                flag = True
                parent.append(j)  #将邻居方向加入父节点方向
                # 向其他邻居广播BFS信号
                for ele in adjDirection:
                    if ele != j:
                        self.sendAsynchData(ele,["search",min_uid])
                        
        if end_counter == 0:
            self.sendAsynchData(parent[0],["join",min_uid])      
            if min_uid == id:
                leader_state = "leader"
                endtime =  datetime.datetime.now()
                
            else:
                leader_state = "non-leader"         
            value = {"state":leader_state,"parent":parent,"child":child}

            # self.sendDatatoGUI(str(value))  

            if leader_state == "leader":
                for ele in child:
                    self.sendAsynchData(ele,["end",min_uid]) 
                break
    # 下面进行求和
    end_counter = len(child)
    if end_counter == 0:
        self.sendAsynchData(parent[0],message_cnt)
    else:
        while True:
            j,data = self.getAsynchData()
            message_cnt += data
            end_counter = end_counter - 1
            if end_counter == 0:
                self.sendAsynchData(parent[0],message_cnt)      
                break

    if leader_state == "leader":
        time.sleep(1)
        self.sendDatatoGUI("运行时间:"+str(endtime-starttime)+" 消息总数:"+str(message_cnt)) 
    return value