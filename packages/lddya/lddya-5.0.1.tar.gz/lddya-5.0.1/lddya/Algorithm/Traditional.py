import numpy as np
import pandas as pd
import copy




################################################## 1 A*算法路径规划 ###########################################
class A_Star_path():
    def __init__(self,map_data,start = np.array([0,0]),end = np.array([0,0])) -> None:
        print('A* Task:',start,end)
        self.map_data = np.array(map_data)
        self.size_map = self.map_data.shape[0]
        self.start = np.array(start)
        self.end   =  np.array(end)
        self.open_list  = pd.DataFrame([[start[0],start[1],0,abs(self.start[0]-self.end[0])+abs(self.start[1]-self.end[1]),abs(self.start[0]-self.end[0])+abs(self.start[1]-self.end[1]),-1,-1]],columns=['pos_y','pos_x','g','h','f','parent_y','parent_x'])
        self.close_list = pd.DataFrame([[999,999,0,0,0,0,0]],columns=['pos_y','pos_x','g','h','f','parent_y','parent_x'])
        self.best_way_len = 0
        

    def run(self):
        running = True
        while running:
            #step 1: select an element whose f is smallest(if there are multiple elements with the same f value, we will select the one with the lowest s value.)
            smal_index = self.open_list.loc[:,'f'].argmin()
            #step 2: find all the neighbor grid of it
            neighbour_allowed = self._find_neighbour(self.open_list.iloc[smal_index].values)
            #step 3: update open_list by neighbour_allowed
            have_find_term = self._update_open_list(neighbour_allowed,self.open_list.iloc[smal_index].values)
            if have_find_term == True:
                break
            #step 4: delete it in the open_list and copy to the close_list
            self.close_list.loc[self.close_list.shape[0]] = self.open_list.iloc[smal_index].copy()
            self.open_list.drop(smal_index,inplace=True)
            self.open_list.index = range(self.open_list.shape[0])
        self._calc_way()
        #!print('最优路径为:')
        #!(self.best_way_data)
        


              

    def _find_neighbour(self,who):
        '''
            Function:
            ---------
            This Func can find all neighbor grid of the who, and return them.

            Params:
            -------
            who : 1*d-list--> fe:[[0,0],0,19,19,-1]

            Return:
            ---------
            neighbour_allowed : 1*d-list--> all the neighbour can allowed.
        '''
        y = int(who[0])
        x = int(who[1])
        neighbour_1 = [
            [y-1,x-1],[y-1,x],[y-1,x+1],
            [y  ,x-1],        [y  ,x+1],
            [y+1,x-1],[y+1,x],[y+1,x+1],
        ]
        neighbour_allowed = []
        for i in neighbour_1:
            if (0<=i[0]<=self.size_map-1)and(0<=i[1]<=self.size_map-1): #grid within the scope of the map.
                if self.map_data[i[0],i[1]] == 0:
                    neighbour_allowed.append(i)
        return neighbour_allowed

    def _update_open_list(self,neighbour_allowed,who):
        have_find_term = False           # maiks whether the terminal was found
        for i in neighbour_allowed:
            # case 1: if i in close_list, discard it. 
            
            if (i == self.close_list.loc[:,['pos_y','pos_x']].values).all(axis = 1).any():
                continue
            # we must calculate the data first as it will be used in the both following case. 
            dict_1 = {
                'pos_y' : i[0],
                'pos_x' : i[1],
                'g'   : who[2]+(1.414 if (abs(i[0]-who[0])+abs(i[1]-who[1]))==2 else 1),
                'h'   : abs(i[0]-self.end[0])+abs(i[1]-self.end[1]),
                'f'   : 0,
                'parent_y': who[0],
                'parent_x': who[1]
            }
            dict_1['f']  = dict_1['g']+dict_1['h']
            # case 2: provided i in open_list, check whether i's f is greater 
            #              than b's, if True, update the data of i in the open_list;
            #              otherwise, discard new it. 
            r = (i == self.open_list.loc[:,['pos_y','pos_x']].values).all(axis = 1)
            if r.any():
                index = np.where(r==True)[0]
                if self.open_list.loc[index,'f'].values>dict_1['f']:
                    self.open_list.loc[index,'g'] = dict_1['g']
                    self.open_list.loc[index,'h'] = dict_1['h']
                    self.open_list.loc[index,'f'] = dict_1['f']
                    self.open_list.loc[index,'parent_y'] = dict_1['parent_y']
                    self.open_list.loc[index,'parent_x'] = dict_1['parent_x']
                    
                else:
                    pass
            # case 3: add the i in the open_list.(when i is terminal,the return_param will be True)
            else:
                self.open_list.loc[self.open_list.shape[0]] = dict_1
            if (i == self.end).all():
                have_find_term = True
        return have_find_term

    def _calc_way(self):
        '''
            Function:
            ---------
                find the best way from open_list and close_list, and the result will be saved in self.best_way_data.
        '''
        #step 1: Ectract the position and parent of each element in open_list and close_list.
        dict_1 = {

        }
        for k in range(self.open_list.shape[0]):
            i = self.open_list.iloc[k]
            dict_1[str(int(i.values[0]))+','+str(int(i.values[1]))] = str(int(i.values[-2]))+','+str(int(i.values[-1]))
        for k in range(self.close_list.shape[0]):
            i = self.close_list.iloc[k]
            dict_1[str(int(i.values[0]))+','+str(int(i.values[1]))] = str(int(i.values[-2]))+','+str(int(i.values[-1]))
        # step 2: find the best way between the end with start from dict_1.
        y,x = self.end
        self.best_way_data = [[y,x]]
        while True:
            a_1 = dict_1[str(y)+','+str(x)].split(',')
            y,x = eval(a_1[0]),eval(a_1[1])
            b_1 = self.best_way_data[-1]
            self.best_way_len += ((y-b_1[0])**2+(x-b_1[1])**2)**0.5
            self.best_way_data.append([y,x])
            if y==self.start[0] and x == self.start[1]:
                break
        self.best_way_data.reverse()
            

################################################## 2 动态规划算法路径规划 ###########################################

class Dynamic_Programing():
    def __init__(self,map_data,start = [0,0],end= [19,19]) -> None:
        '''
            Function
            --------
            parameter initilization

            Parameter
            --------
            map_data : 栅格地图数据，   2d矩阵
            start    : 起点坐标，      1*2向量 [y,x]
            end      : 终点坐标，      1*2向量 [y,x]

            Return
            ------
            None
        '''
        self.map_data = map_data
        self.map_size = map_data.shape[0]
        self.start = start
        self.end = end
        self.relation_matrix = np.zeros_like(self.map_data,dtype = np.int16)   #关系矩阵，标记方向
        self.relation_code_zhi = np.array([1,3,5,7])          #回溯方向代码，放入关系矩阵中
        self.relation_code_xie = np.array([2,4,6,8])
        self.dynamic_matrix  = np.zeros_like(self.map_data)   #动态矩阵，标记需要处理的母节点
        self.dynamic_matrix[self.end[0],self.end[0]] = 1   #初始时，母节点仅有终点
        self.static_matrix   = self.dynamic_matrix.copy()   #静态矩阵，冻结的节点(不进行任何操作)

    
    def run(self):
        while True:
            self.relation_matrix_temp = np.zeros_like(self.relation_matrix)
            self.dynamic_matrix_temp  = np.zeros_like(self.dynamic_matrix) 
            # step 1: 由需要处理的母节点进行扩散
            self.task_matrix = np.zeros_like(self.map_data)
            #self.task_2_matrix = np.zeros(shape=np.array(self.map_data.shape)+2)    #扩大点，就不用考虑边界了，task
            y_1,x_1 = np.where(self.dynamic_matrix==1)
            for k,i in enumerate(y_1):      #直线方向上的更新
                y = y_1[k]
                x = x_1[k]
                neighbours = np.array([
                    [y-1,x],
                    [y,x+1],
                    [y+1,x],
                    [y,x-1],
                ])
                cond_1 = np.logical_and(neighbours[:,0]>=0,neighbours[:,0]<self.map_size)
                cond_2 = np.logical_and(neighbours[:,1]>=0,neighbours[:,1]<self.map_size)
                allowed_index = np.logical_and(cond_1,cond_2)          #约束1：坐标范围
                allowed_rela_code = self.relation_code_zhi[allowed_index]
                allowed_neigh = neighbours[allowed_index]
                allowed_rela_code = allowed_rela_code[self.map_data[allowed_neigh[:,0],allowed_neigh[:,1]]==0] #约束2的code，因为allowed_neigh下一步变了，故要提前处理code，约束3的同理
                allowed_neigh = allowed_neigh[self.map_data[allowed_neigh[:,0],allowed_neigh[:,1]]==0]     #约束2 ： 空白栅格
                allowed_rela_code = allowed_rela_code[self.static_matrix[allowed_neigh[:,0],allowed_neigh[:,1]]==0]
                allowed_neigh = allowed_neigh[self.static_matrix[allowed_neigh[:,0],allowed_neigh[:,1]]==0]  #约束3： 不能是static
                
                a_1 = self.relation_matrix[allowed_neigh[:,0],allowed_neigh[:,1]] == 0  # 没更新的地方,需要判断吗？
                self.relation_matrix_temp[allowed_neigh[a_1][:,0],allowed_neigh[a_1][:,1]] = allowed_rela_code[a_1]
                self.relation_matrix[self.relation_matrix_temp!=0] = self.relation_matrix_temp[self.relation_matrix_temp!=0]
                self.dynamic_matrix_temp[self.relation_matrix_temp!=0] = 1 
            
            self.relation_matrix_temp = np.zeros_like(self.relation_matrix)
            for k,i in enumerate(y_1):      #斜线方向上的更新
                y = y_1[k]
                x = x_1[k]
                neighbours = np.array([
                    [y-1,x+1],
                    [y+1,x+1],
                    [y+1,x-1],
                    [y-1,x-1]
                ])
                cond_1 = np.logical_and(neighbours[:,0]>=0,neighbours[:,0]<self.map_size)
                cond_2 = np.logical_and(neighbours[:,1]>=0,neighbours[:,1]<self.map_size)
                allowed_index = np.logical_and(cond_1,cond_2)
                allowed_rela_code = self.relation_code_xie[allowed_index]
                allowed_neigh = neighbours[allowed_index]
                allowed_rela_code = allowed_rela_code[self.map_data[allowed_neigh[:,0],allowed_neigh[:,1]]==0] #约束2的code，因为allowed_neigh下一步变了，故要提前处理code，约束3的同理
                allowed_neigh = allowed_neigh[self.map_data[allowed_neigh[:,0],allowed_neigh[:,1]]==0]     #约束2 ： 空白栅格
                allowed_rela_code = allowed_rela_code[self.static_matrix[allowed_neigh[:,0],allowed_neigh[:,1]]==0]
                allowed_neigh = allowed_neigh[self.static_matrix[allowed_neigh[:,0],allowed_neigh[:,1]]==0]  #约束3： 不能是static
                a_1 = self.relation_matrix[allowed_neigh[:,0],allowed_neigh[:,1]] == 0  # 没更新的地方,需要判断吗？
                self.relation_matrix_temp[allowed_neigh[a_1][:,0],allowed_neigh[a_1][:,1]] = allowed_rela_code[a_1] 
                self.relation_matrix[self.relation_matrix_temp!=0] = self.relation_matrix_temp[self.relation_matrix_temp!=0]
                self.dynamic_matrix_temp[self.relation_matrix_temp!=0] = 1 
            
            
            self.dynamic_matrix = self.dynamic_matrix_temp.copy()   #更新下一轮的母节点(动态矩阵)
            self.static_matrix[self.dynamic_matrix!=0] = 1   #本轮的母节点全部冻结
            if self.static_matrix[self.start[0],self.start[1]] !=0:
                print('路径规划完成！')
                self._translate()
                break


    def _translate(self):
        self.way_data_best = []
        self.way_len_best = 0
        grid = self.start.copy()
        self.way_data_best.append(grid)
        while True:
            change_matrix = np.array([
                [1,0],
                [1,-1],
                [0,-1],
                [-1,-1],
                [-1,0],
                [-1,1],
                [0,1],
                [1,1]
            ])

            grid = grid+change_matrix[self.relation_matrix[grid[0],grid[1]]-1]
            if 0 in change_matrix[self.relation_matrix[grid[0],grid[1]]-1].tolist():
                self.way_len_best += 1
            else:
                self.way_len_best += 2**0.5
            self.way_data_best.append(grid)
            if (grid == self.end).all():
                self.way_data_best = np.array(self.way_data_best)
                break
        
