# 无根节点的生成树
import datetime,time
def drc2id(adjDirection,adjID,drc):
    return adjID[adjDirection.index(drc)]
            

def taskFunction(self,id,adjDirection,datalist):
    flag = False 
    parent = []
    child = []
    end_counter = len(adjDirection)
    min_uid = id
    flag = True
    parent.append(-1)

    for ele in adjDirection:
        self.sendAsynchData(ele,["search",id])

    while True:
        j,(data,token) = self.getAsynchData()
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
                for ele in child:
                    self.sendAsynchData(ele,["end",min_uid]) 
                break
                
            else:
                leader_state = "non-leader"         


    adjID = self.TaskadjID 

    child = [drc2id(adjDirection,adjID,ele) for ele in child]
    parent = [drc2id(adjDirection,adjID,ele) for ele in parent if ele != -1]
    value = {"state":leader_state,"parent":parent,"child":child}
    return value