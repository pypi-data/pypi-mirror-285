import numpy as np
import pandas as pd
import copy


class baseAlgorithm():
    def __init__(self) -> None:
        self.generation_aver = []
        self.generation_best = []
    
    def saveDateToExcel(self,generation_aver = False,generation_best = False,other_data_name = '',fp = 'data.xlsx'):
        '''
            Function
            --------
            提供数据保存excel服务。默认提供generation_aver与generation_best两个数据的保存，同时提供一个可自定义数据的保存。

            Params
            ------
            generation_aver    : 每代平均
            generation_best    : 每代最优
            other_data_name    : 自定义数据名称，如想保存generation_aver，直接写generation_aver即可。
            fp                 : 文件名称，要求类型为xlsx。默认为data.xlsx。

            Return
            ------
            None
        '''
        writer = pd.ExcelWriter(fp,mode = 'w',engine='openpyxl')
        for i in writer.book.worksheets:
            writer.book.remove(worksheet=i)   #这里先删除所有sheet
        if generation_aver:
            df1 = pd.DataFrame(data = self.generation_aver)
            df1.to_excel(writer,sheet_name='generation_aver')
        if generation_best:  
            df2 = pd.DataFrame(data = self.generation_best)    
            df2.to_excel(writer,sheet_name='generation_best')   
        if other_data_name != '':  
            df3 = pd.DataFrame(data = eval('self.'+other_data_name))    
            df3.to_excel(writer,sheet_name=other_data_name)   
        writer._save()          #如果说没有save()，就写_save()
        writer.close()

################################################## 1 蚁群算法路径规划 ###########################################

# Ant只管通过地图数据以及信息素数据，输出一条路径。其他的你不用管。
class Ant():
    def __init__(self,start,end,max_step,pher_imp,dis_imp) -> None:
        self.max_step = max_step    # 蚂蚁最大行动力
        self.pher_imp = pher_imp    # 信息素重要性系数
        self.dis_imp = dis_imp      # 距离重要性系数
        self.start = start          # 蚂蚁初始位置[y,x] = [0,0],考虑到列表索引的特殊性，先定y，后定x
        self.destination = end  # 默认的终点节点(在run方法中会重新定义该值)
        self.successful = True      #标志蚂蚁是否成功抵达终点
        self.record_way = [start]   #路径节点信息记录
        

    def run(self,map_data,pher_data):
        self.position = copy.deepcopy(self.start)
        #Step 1:不断找下一节点，直到走到终点或者力竭 
        for i in range(self.max_step):
            r = self.select_next_node(map_data,pher_data)
            if r == False:
                self.successful = False
                break
            else:
                if self.position == self.destination:
                    break
        else:
            self.successful = False
    
    def select_next_node(self,map_data,pher_data):
        '''
        Function:
        ---------
        选择下一节点，结果直接存入self.postion，仅返回一个状态码True/False标志选择的成功与否。
        '''
        y_1 = self.position[0]
        x_1 = self.position[1]
        #Step 1:计算理论上的周围节点
        node_be_selected = [[y_1-1,x_1-1],[y_1-1,x_1],[y_1-1,x_1+1],     #上一层
                            [y_1,x_1-1],              [y_1,x_1+1],       #同层
                            [y_1+1,x_1-1],[y_1+1,x_1],[y_1+1,x_1+1],     #下一层
                        ]
        #Step 2:排除非法以及障碍物节点    
        node_be_selected_1 = []
        for i in node_be_selected:
            if i[0]<0 or i[1]<0:
                continue
            if i[0]>=len(map_data) or i[1]>=len(map_data):
                continue
            if map_data[i[0]][i[1]] == 0:
                node_be_selected_1.append(i)
        if len(node_be_selected_1) == 0:    # 如果无合法节点，则直接终止节点的选择
            return False
        if self.destination in node_be_selected_1:   # 如果到达终点旁，则直接选中终点
            self.position = self.destination
            self.record_way.append(copy.deepcopy(self.position))
            map_data[self.position[0]][self.position[1]] = 1
            return True
        #Step 3:计算节点与终点之间的距离，构建距离启发因子
        dis_1 = []    # 距离启发因子
        for i in node_be_selected_1:
            dis_1.append(((self.destination[0]-i[0])**2+(self.destination[1]-i[1])**2)**0.5)
        #Step 3.1:倒数反转
        for j in range(len(dis_1)):
            dis_1[j] = 1/dis_1[j]

        #Step 4:计算节点被选中的概率
        prob = []
        for i in range(len(node_be_selected_1)):
            p = (dis_1[i]**self.dis_imp) * (pher_data[y_1*len(map_data)+x_1][node_be_selected_1[i][0]*len(map_data)+node_be_selected_1[i][1]]**self.pher_imp)
            prob.append(p)
        #Step 5:轮盘赌选择某节点
        prob_sum = sum(prob)
        for i in range(len(prob)):
            prob[i] = prob[i]/prob_sum
        rand_key = np.random.rand()
        for k,i in enumerate(prob):
            if rand_key<=i:
                break
            else:
                rand_key -= i
        #Step 6:更新当前位置，并记录新的位置，将之前的位置标记为不可通过
        self.position = copy.deepcopy(node_be_selected_1[k])
        self.record_way.append(copy.deepcopy(self.position))
        map_data[self.position[0]][self.position[1]] = 1
        return True

class ACO(baseAlgorithm):
    def __init__(self,map_data,start = [0,0],end = [19,19],max_iter = 100,ant_num = 50,pher_imp = 1,dis_imp = 10,evaporate = 0.7,pher_init = 8) -> None:
        '''
            Params:
            --------
                pher_imp : 信息素重要性系数\n
                dis_imp  : 距离重要性系数\n
                evaporate: 信息素挥发系数(指保留的部分)\n
                pher_init: 初始信息素浓度\n
        '''
        #Step 0: 参数定义及赋值
        self.max_iter = max_iter       #最大迭代次数
        self.ant_num  = ant_num        #蚂蚁数量
        self.ant_gener_pher = 1    #每只蚂蚁携带的最大信息素总量
        self.pher_init = pher_init #初始信息素浓度
        self.ant_params = {        #生成蚂蚁时所需的参数
            'dis_imp':dis_imp,
            'pher_imp': pher_imp,
            'start'   : start,
            'end'     : end
        }
        self.map_data = map_data.copy()        #地图数据
        self.map_lenght = self.map_data.shape[0]  #地图尺寸,用来标定蚂蚁的最大体力
        self.pher_data = pher_init*np.ones(shape=[self.map_lenght*self.map_lenght,
                                            self.map_lenght*self.map_lenght])    #信息素矩阵
        self.evaporate = evaporate #信息素挥发系数
        self.generation_aver = []  #每代的平均路径(大小)，绘迭代图用
        self.generation_best = []  #每代的最短路径(大小)，绘迭代图用
        self.way_len_best = 999999 
        self.way_data_best = []     #最短路径对应的节点信息，画路线用  


        
    def run(self,show_process = False):
        #总迭代开始
        for i in range(self.max_iter):      
            self.success_way_list = []
            #Step 1:当代若干蚂蚁依次行动
            for j in range(self.ant_num):   
                ant = Ant(start =self.ant_params['start'],end=self.ant_params['end'], max_step=self.map_lenght*3,pher_imp=self.ant_params['pher_imp'],dis_imp=self.ant_params['dis_imp'])
                ant.run(map_data=self.map_data.copy(),pher_data=self.pher_data)
                if ant.successful == True:  #若成功，则记录路径信息
                    self.success_way_list.append(ant.record_way)
            #Step 2:计算每条路径对应的长度，后用于信息素的生成量
            way_lenght_list = []
            for j in self.success_way_list:
                way_lenght_list.append(self.calc_total_lenght(j))
            #Step 3:更新信息素浓度
            #  step 3.1: 挥发
            self.pher_data = self.evaporate*self.pher_data
            #  step 3.2: 叠加新增信息素
            for k,j in enumerate(self.success_way_list):
                j_2 = np.array(j)
                j_3 = j_2[:,0]*self.map_lenght+j_2[:,1]
                for t in range(len(j_3)-1):
                    self.pher_data[j_3[t]][j_3[t+1]] += self.ant_gener_pher/way_lenght_list[k]
            #Step 4: 当代的首尾总总结工作
            self.generation_aver.append(np.average(way_lenght_list))
            self.generation_best.append(min(way_lenght_list))
            if self.way_len_best>min(way_lenght_list):
                a_1 = way_lenght_list.index(min(way_lenght_list))
                self.way_len_best = way_lenght_list[a_1]
                self.way_data_best = copy.deepcopy(self.success_way_list[a_1])
            if show_process:
                print('第',i,'代:  成功寻路个数:',len(self.success_way_list),end= '')
                print('平均长度:',np.average(way_lenght_list),'最短:',np.min(way_lenght_list))
            

    
    def calc_total_lenght(self,way):
        lenght = 0
        for j1 in range(len(way)-1):
            a1 = abs(way[j1][0]-way[j1+1][0])+abs(way[j1][1]-way[j1+1][1])
            if a1 == 2:
                lenght += 1.41421
            else:
                lenght += 1
        return lenght

################################################## 3 遗传算法路径规划 ###########################################
class GA(baseAlgorithm):
    def __init__(self, map_data,chroms_list,population=50, max_iter = 100, cross_pro=0.95, mut_pro=0.15):
        '''
            Function
            --------
            初始化一个基本GA用于解决路径规划。

            Params
            ------
            map_data     : n*n-np.array  -> 尺寸为n*n的地图数据。\n
            chroms_list  : 
            population   : int -> 种群大小，默认为50。\n
            max_iter     : int -> 最大迭代次数，默认为50。\n
            cross_pro    : float -> 交叉概率，默认0.95。\n
            mut_pro      : float -> 变异概率，默认0.15。\n

            Return
            ------
            返回一个用于解决路径规划的GA实例。
            
        '''
        self.map_data = map_data   
        self.population = population   
        self.max_iter = max_iter
        self.cross_pro = cross_pro
        self.mut_pro = mut_pro
        self.chroms_list = chroms_list  # 初代染色体信息库, 初始化由外部提供
        self.child_list = []    #子代染色体信息库
        self.generation_aver = []   #记录每代评估值的平均值的列表
        self.generation_best = []   #记录每代评估值的最优值的列表
        self.global_best_value = 999  #全局已知最优评估值，默认为一个很大的数，999一般够用。
        self.way_data_best = []       #全局已知最优评估值对应的路径信息
        self.temporary = []   #临时变量，用来保存ACO生成的初代路径


    def eval_fun(self,way):
        '''
            Function
            --------
            染色体评估函数。

            Params
            ------
            way : n-list -> 一条包含n个节点信息的路径列表。如: [[0,0],[0,1],[1,2]...]

            Return
            ------
            length   : float -> 路径长度
        '''
        length = 0
        for j1 in range(len(way)-1):
            a1 = abs(way[j1][0]-way[j1+1][0])+abs(way[j1][1]-way[j1+1][1])
            if a1 == 2:
                length += 1.41421
            else:
                length += 1
        return length
    
    def run(self,show_process = False):
        '''
            Function
            --------
            函数运行主流程
        '''
        for i in range(self.max_iter):
            # Step 1：执行种群选择
            self.child_list = self.selection()
            self.evalution()
            # Step 2: 交叉 
            self.cross()
            # Step 3: 变异
            self.mutation()
            # Step 4: 子代并入父代中
            self.chroms_list = self.child_list.copy()
            if show_process:
                print('第',i,'代:')
                print('平均长度:',self.generation_aver[-1],'最短:',self.generation_best[-1])
    
    def selection(self):
        '''
            Function:
            ---------
                选择算子。选择法则为竞标赛选择法。即每次随机选择3个个体出来竞争，最优秀的那个个体的染色体信息继承到下一代。
            
            Params:
            --------
                None

            Return:
            -------
                child_1:    list-list
                    子代的染色体信息
        '''
        chroms_1 = self.chroms_list.copy()
        child_1 = []
        for i in range(self.population):
            a_1 = []    # 3个选手
            b_1 = []    # 3个选手的成绩
            for j in range(3):
                a_1.append(np.random.randint(0,len(chroms_1)))
            for j in a_1:
                b_1.append(self.eval_fun(chroms_1[j]))
            c_1 = b_1.index(min(b_1))  # 最好的是第几个
            child_1.append(chroms_1[a_1[c_1]])  #最好者进入下一代
        return child_1


    def evalution(self):
        '''
            Function
            --------
            对child_list中的染色体进行评估
        '''
        e = []
        for i in self.child_list:
            e.append(self.eval_fun(i))
        self.generation_aver.append(sum(e)/len(e))
        self.generation_best.append(min(e))
        if min(e)<=self.global_best_value:
            self.global_best_value = min(e)
            k = e.index(min(e))
            self.way_data_best = self.child_list[k]

    def cross(self):
        '''
            Function
            --------
            交叉算子
        '''
        child_1 = []   # 参与交叉的个体
        for i in self.child_list:  #依据交叉概率挑选个体
            if np.random.random()<self.cross_pro:
                child_1.append(i)
        if len(child_1)%2 != 0:    #如果不是双数
            child_1.append(child_1[np.random.randint(0,len(child_1))])  #随机复制一个个体
        for i_1 in range(0,len(child_1),2):
            child_2 = child_1[i_1]       #交叉的第一个个体
            child_3 = child_1[i_1+1]     #交叉的第二个个体
            sames = []     #两条路径中，相同的节点的各自所在位置，放这里，留待后面交叉
            for k,i in enumerate(child_2[1:-1]):          # 找相同节点(除起点与终点)
                if i in child_3:
                    sames.append([k+1,child_3.index(i)])   # [index in child_2, index in child_3  ]
            if len(sames) != 0:
                a_1 = np.random.randint(0,len(sames))
                cut_1 = sames[a_1][0]
                cut_2 = sames[a_1][1]
                child_1[i_1] = child_2[:cut_1]+child_3[cut_2:]            #新的覆盖原染色体信息
                child_1[i_1+1] = child_3[:cut_2]+child_2[cut_1:]
        for i in child_1:                     #交叉后的染色体个体加入子代群集中
            self.child_list.append(i)

    def mutation(self):        
        '''
            Function
            --------
            变异算子
        '''
        child_1 = []   # 参与变异的个体
        for i in self.child_list:  #依据变异概率挑选个体
            if np.random.random()<self.mut_pro:
                child_1.append(i)
        for i in range(0,len(child_1)):
            child_2 = np.array(child_1[i])
            index = np.random.randint(low=1,high=len(child_2)-1)    #随机选择一个中间节点
            point_a,point_b,point_c = child_2[index-1:index+1+1]
            v1 = point_b-point_a
            v2 = point_c-point_b
            dot_product = np.dot(v1, v2)  #计算这两个向量的内积
            if dot_product <0 :          #如果两个向量之间的夹角为锐角，则必产生冗余
                del child_1[i][index]    #删除被选中的节点
            elif dot_product == 0:       #如果两个向量之间的夹角为直角，则需要进一步判断
                if 0 in v1:               #如果第一个向量是水平或者垂直的,则必存在冗余
                    del child_1[i][index]    #删除被选中的节点
                elif self.map_data[(point_a[0]+point_c[0])//2,(point_a[1]+point_c[1])//2]==0:                     #如果第一个向量是对角的,且point_a与point_b之间的节点为可通行，则可优化
                    child_1[i][index]  = [(point_a[0]+point_c[0])//2,(point_a[1]+point_c[1])//2]  #修改被选中的节点为中间节点

        for i in child_1:                     #交叉后的染色体个体加入子代群集中
            self.child_list.append(i)
