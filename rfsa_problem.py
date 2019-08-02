"""routing and flexible spectrum slots allocation optimization problem."""
from __future__ import print_function
import cplex
import sys
import itertools
import math
import copy
import csv
import topology
import time
import pulp
from pulp import CPLEX_CMD

# グラフの定義
g_orgin = topology.COST239
g_length = len(g_orgin)
V = [a for a in range(g_length)] #ノードの集合
E = [] #リンクの集合
for i in V:
  for j in range(g_length):
    if g_orgin[i][j]  >0:
      E.append((i,j))

node_num = len(g_orgin)
#要求の設定
s = 0
s_d = []
for a in range(node_num):
  if a != s:
    s_d.append([s,a])

b = 2000 #要求伝送容量
#number of failures
M = input('M=')
M = int(M)
#partial protection requirement
rho = input('rho = ')
rho = float(rho)
r = input('r is ')
G = 1 # ガードバンドに必要なスロット数


# パスの長さのクラスわけ
C = [0,1,2,3,4] #パスの長さのクラス
L_c = [250,500,1000,2000,4000] #reach
e_c = [62.5,50,37.5,25,12.5] # 変調効率


alpha = 320


#for bhandari's alg.
map1 = topology.COST239
map2 = topology.COST239

g = copy.deepcopy(map1)
g2 = copy.deepcopy(map2)

nodes =[a for a in range(node_num)]



def fbar_set(K,N,M):
  F_bar = pulp.combination(K,N-M)
  
  
def rfsa_problem(N):
  K = [k for k in range(N)]
  F_bar = pulp.combination(K,N-M)
  possible_k_ij = [(k,(i,j)) for (i,j) in E for k in K] #path k とリンクのとりうる組み合わせ
  possible_k_c = [(k,c) for c in C for k in K] #path k とクラスCのとりうる組み合わせ
  
  # Variables
  x = pulp.LpVariable.dicts('x',possible_k_ij, cat = 'Binary') #x^k_ij
  B = pulp.LpVariable.dicts('B',K, lowBound = 0, upBound = 320, cat = 'Integer') #B_k
  a = pulp.LpVariable.dicts('a',possible_k_ij, lowBound = 0, upBound = 320, cat = 'Integer') #a^k_ij
  y = pulp.LpVariable.dicts('y',possible_k_c, cat = 'Binary') #y^k_c(path k のクラス)
  z = pulp.LpVariable.dicts('z',possible_k_c, lowBound = 0, upBound = 320, cat = 'Integer') #z^k_c
  
  #
  #モデルの設定
  m = pulp.LpProblem('RFSA problem')
  
  #
  # objective function 
  m += pulp.lpSum(a[i]+G*x[i] for i in possible_k_ij)
  
  #
  # constraints
  #
  
  #use N path 
  for k in K:
    m += B[k] >= 1
  
  # traffic capacity
  m += b <= pulp.lpSum(e_c[c]*z[(k,c)] for (k,c) in possible_k_c)
  
  for fbar in F_bar:
    possible_fbar_c = [(p,c) for p in fbar for c in C]
    m += rho*b <= pulp.lpSum(e_c[c]*z[(p,c)] for (p,c) in possible_fbar_c)
  
  #flow
  for k in K:
    for inter in V:
      if (inter !=s) and (inter !=d):
        m += pulp.lpSum(x[(k,(i,j))] for (i,j) in E if i == s) - pulp.lpSum(x[(k,(j,i))] for (j,i) in E if i == s) ==1
        m += pulp.lpSum(x[(k,(i,j))] for (i,j) in E if i == inter) - pulp.lpSum(x[(k,(j,i))] for (j,i) in E if i == inter) ==0

  # link disjoint
  for (i,j) in E:
    m += pulp.lpSum(x[(k,(i,j))] + x[(k,(j,i))] for k in K) <= 1
  
  # a^k_ij
  for k in K:
    for e in E:
      m += a[(k,e)] >= B[k] + alpha*(x[(k,e)]-1)
      m += a[(k,e)] <= alpha*x[(k,e)]
      #m += a[(k,e)] >= 0
  
  # path length class
  for k in K:
    m += pulp.lpSum(g[i][j]*x[(k,(i,j))] for (i,j) in E) <= pulp.lpSum(L_c[c]*y[(k,c)] for c in C)
    m += pulp.lpSum(y[(k,c)] for c in C) == 1
  
  # z^k_c
  for k in K:
    for c in C:
      m += z[(k,c)] <= B[k]
      m += z[(k,c)] >= B[k] + alpha*(y[(k,c)]-1)
      m += z[(k,c)] <= alpha*y[(k,c)]
      #m += z[(k,c)] >= 0
  
  # print(m)
  m.solve(CPLEX_CMD())
  total_slots = pulp.value(m.objective)
  for k in B.keys():
    print('B_' + str(k) + ' = ' + str(pulp.value(B[k])))
  for (k,e) in x.keys():
    if pulp.value(x[(k,e)]) == 1:
      print('a_'+str(k)+ '_' + str(e) + ' = ' +str(pulp.value(a[(k,e)])))
      
  for (k,c) in y.keys():
    if pulp.value(y[(k,c)]) ==1:
      print('z_' + str(k) +str(c) + ' = ' + str(pulp.value(z[(k,c)])))
  
  return total_slots


def dijkstra(s,d):
  S_bar =[] #list of neighbor nodes
  predecessor = [None] * node_num
  
  
  # step 1
  
  distance = [math.inf] * node_num #distance of i from s
  distance[s] = 0 #source node
  for index in nodes:
    if g[index][s] > 0:
      distance[index] = g[index][s]
      predecessor[index] = s
      S_bar.append(index)
  # print(S_bar)
  while True:
    
    
    # step 2
    
    j = get_j(S_bar,distance)
    if j == None:
      print('Not found')
      
      break
      
    if j == d:
      print('get path')
      break
    
    S_bar.remove(j)
    # print(S_bar)
    
    
    # step 3
    # print(g[j])
    for index in nodes:
      if g[j][index] != 0:
        # print(distance[index],distance[j],g[])
        if distance[j] + g[j][index] < distance[index]:
          distance[index] = distance[j] + g[j][index]
          predecessor[index] = j
          if (index in S_bar) == False: # if 
            # print('reseach it')
            # print('i=',index+1)
            S_bar.append(index)
    
  return distance,predecessor
    

def get_j(S_bar,distance):
  min_dis = math.inf
  min_i = None
  for index in S_bar:
    if min_dis > distance[index]:
      min_dis = distance[index]
      min_i = index
  return min_i
  


#Bhandari
def Bhandari(s,d):
  
  #first dijkstra
  
  distance,predecessor = dijkstra(s,d)
  # print(predecessor)
  p = d
  while p != None:
    pre = predecessor[p]
    if p != s:
      g[p][pre] = - g[p][pre]
      g[pre][p] = 0
    p = pre
  
  
  #N-1 times dijkstra for the topology including negative arcs
  
  
  count = 1
  while True:
    distance,predecessor = dijkstra(s,d)
    print(distance)
    if distance[d] == math.inf:
      break
    # print(distance)
    # print(g)
    # print(predecessor)
    p = d
    while p != None:
      pre = predecessor[p]
      if p != s and pre != None:
        
        #replace the overlapping links with the original links
        
        if g[pre][p] < 0:
          g[pre][p] = g2[pre][p]
          g[p][pre] = g2[p][pre]
        
        #make the length of each edges negative
        
        else:
          g[p][pre] = - g[p][pre]
          g[pre][p] = 0
      p = pre
    

    count += 1
  return count



if __name__ == "__main__":
  for d in range(1,g_length):
    print('(s,d) = ',(s+1,d+1))
    opt_allocation = math.inf
    
    start_time = time.time()
    
    max_path_num = Bhandari(s,d)
    N = M # M+1本からスタート
    while True:
      N += 1
      if max_path_num < N:
        print('There is no %s paths' % N)
        break
      # total_slots = rfsa_problem(N)
      # elif total_slots == None:
      #   break
      else:
        print(str(N)+"本")
        total_slots = rfsa_problem(N)
        if opt_allocation > total_slots:
          opt_allocation = total_slots
    timer = time.time() - start_time
    if opt_allocation == math.inf:
      opt_allocation = 0
    print('minimized required spectrum resource is ' + str(int(opt_allocation)))
    
    
    Ans = [d+1,opt_allocation,timer]
    if d == 1:
      with open('result/rfsa'+str(s+1)+'_b'+str(b)+'_rho'+r+'_M'+str(M)+'.csv','w') as f:
          writer = csv.writer(f)
          writer.writerow(Ans)
    else:
      with open('result/rfsa'+str(s+1)+'_b'+str(b)+'_rho'+r+'_M'+str(M)+'.csv','a') as f:
          writer = csv.writer(f)
          writer.writerow(Ans)

  