# coding: UTF-8

from __future__ import print_function
#import cplex
import sys
import itertools
import math
import copy
import csv
import topology


T = [
[2000], #b
[1], #M
[0.5] #rho
]
r = '05'

b_len = len(T[0])
#bandwidth requirement
# b = T[0]
#number of failures
M = T[1][0]
#partial protection requirement
rho = T[2][0]

#guardband
G = 1


#networks topology
map1 = topology.COST239
map2 = topology.COST239

g = copy.deepcopy(map1)
g2 = copy.deepcopy(map2)

#the number of nodes
node_num = len(g)

#(s,d) = (0,0)
#combination of s and d
s_d = []
for a in range(1,node_num):
  s_d.append([0,a])



#used path and shortestpath with negative arcs
path = [[], []]

overlapped_link = []
negative_link = []
linkset = []


#slot assignment


slot_sum = [[0]*b_len for a in range(3)]
slot_av = []*3

counter = 0
optim_N = [0 for a in range(b_len)]


def define_sd_pair(g,s,d):
  g[s],g[0] = g[0],g[s]
  for a in g:
    a[s],a[0] = a[0],a[s]
  g[d],g[node_num-1] = g[node_num-1],g[d]
  for a in g:
    a[d],a[node_num-1] = a[node_num-1],a[d]
  
  return g



def get_target_min_index(min_index, distance, unsearched_nodes):
  start = 0
  while True:
    index = distance.index(min_index,start)
    found = index in unsearched_nodes
    if found:
      return index
    else:
      start = index + 1


def dijikstra(distance, unsearched_nodes, previous_nodes):
  
  while(len(unsearched_nodes) != 0): #until unsearched nodes = 0
    possible_min_distance = math.inf #set initial distance inf
    
    for node_index in unsearched_nodes:
      if possible_min_distance > distance[node_index]:
        possible_min_distance = distance[node_index]
    
    target_min_index = get_target_min_index(possible_min_distance, distance, unsearched_nodes)
    
    unsearched_nodes.remove(target_min_index) #remove a unsearched node
    
    target_edge = g[target_min_index]#list of edge from target node
    
    for index, route_dis in enumerate(target_edge):
      if route_dis != 0:
        if distance[index] > (distance[target_min_index]) + route_dis:
          
          distance[index] = distance[target_min_index] + route_dis
          previous_nodes[index] = target_min_index


def modulation_decision(distance):
  if distance <= 250:#32-QAM
    return 62.5
  elif distance <= 500:#16-QAM
    return 50
  elif distance <= 1000:#8-QAM
    return 37.5
  elif distance <= 2000:#QPSK
    return 25
  elif distance <= 4000:#BPSK
    return 12.5
  else:#over reach
    return 0

#Bhandari
def Bhandari():
  
  #first dijikstra
  unsearched_nodes = list(range(node_num))
  
  distance = [math.inf] * node_num
  distance[0] = 0
  
  previous_nodes = [-1] * node_num
  
  dijikstra(distance, unsearched_nodes,previous_nodes)
  
  
  #make the length of each edges negative and print the path and the distance
  
  previous_node = node_num - 1
  present_node = node_num - 1
  
  while previous_node != -1:
    if present_node != previous_node:
      
        g[present_node][previous_node] = - g[present_node][previous_node]  
        g[previous_node][present_node] = 0
        
        link = {previous_node,present_node}
        path[0].append(link)
        
        present_node = previous_node
        
    
    
    previous_node = previous_nodes[previous_node]
    

  count = 1
  while count < N: 
    #dijikstra for the topology with nefative arcs
    unsearched_nodes = list(range(node_num))
    
    distance = [math.inf] * node_num
    distance[0] = 0
    
    previous_nodes = [-1] * node_num
    
    dijikstra(distance, unsearched_nodes,previous_nodes)
    
    previous_node = node_num - 1
    present_node = node_num - 1
    
    while previous_node != -1:
      if present_node != previous_node:
        
        g[present_node][previous_node] = - g[present_node][previous_node]  
        g[previous_node][present_node] = 0
        
        link = {previous_node,present_node}
        path[1].append(link)
        
        present_node = previous_node

      
      previous_node = previous_nodes[previous_node]
    
    
    #replace the overlapping links with the original links
    overlapped_linkset = [a for a in path[0] if a in path[1]]
    for a in overlapped_linkset:
      a = list(a)
      overlapped_link.append(a)
      overlapped_link.append(a[::-1])
    
    for l in overlapped_link:
      g[l[0]][l[1]] = g2[l[0]][l[1]]
      
    #get links that we should use
    negative_link.extend([a for a in path[0] if a not in path[1]])
    negative_link.extend([a for a in path[1] if a not in path[0]]) #xor
    path[0] = negative_link
    path[1] = []
    
    count += 1
  
  
  linkset = path[0]
  
  
  #replace links we should use
  for a in range(node_num):
    for b in range(node_num):
      g[a][b] = 0
      for l in linkset:
        if [a,b] == list(l):
          g[a][b] = g2[a][b]
        if [b,a] ==list(l):
          g[a][b] = g2[a][b]
  
  
  
  #get disjoint paths
  for a in range(N):
    unsearched_nodes = list(range(node_num))
    
    distance = [math.inf] * node_num
    distance[0] = 0
    
    previous_nodes = [-1] * node_num
    
    dijikstra(distance, unsearched_nodes,previous_nodes)
    
    previous_node = node_num - 1
    present_node = node_num - 1
    hop_count = 0
    while previous_node != -1:
      if present_node != previous_node:
        g[present_node][previous_node] = 0  
        g[previous_node][present_node] = 0
        present_node = previous_node


      previous_node = previous_nodes[previous_node]
      hop_count += 1
    
    hop.append(hop_count-1)
    
    eta.append(modulation_decision(distance[node_num-1]))
    


# コストを計算
def cal_cost(Bk,hop):
  Bkhop = [x*y for (x,y) in zip(Bk,hop)]
  cost = sum (Bkhop)
  return cost

  
  

#要求を満たすか確認
def check(Bk,eta,N,b,rho,M):
  b_sum = 0
  
  bk = [Bk[k]*eta[k] for k in range(N)]
  #print(Bk,bk)
  b_sum = sum(bk)   #通常時の伝送容量
  
  if b_sum < b or b_sum -  sum (sorted (bk, reverse = True)[:M]) < rho*b:  ##合計伝送容量が足りない or M本故障時の伝送容量
    return 0      #故障時に耐えれない
  else:
    return 1  #トラヒック要求を満たす


#割り当てを決める
def allocation(Bk,eta,hop,N,b,rho,M,n):
  global cost
  global opt_Bk
  if (n == N ):# ネストの最深部まできている場合
    #for i in range(1, B_max+1):
      #Bk[n] = i
        
    if check(Bk,eta,N,b,rho,M) == 1:   # Bkが要求を満たすか調べる
      if cost >= cal_cost(Bk,hop):    # コストを比較し小さければ更新
        cost = cal_cost(Bk,hop)
        #print(cost,Bk)
        opt_Bk = Bk
        #print(Bk)
        #print(cost)
      return
        
    return
  else:
    for i in range(1, B_max+1):
      Bk[n] = i
      allocation(Bk,eta,hop,N,b,rho,M,n+1)
    return
            


    
    


if __name__ == "__main__":
  for (s,d) in s_d:
    N = M+1 #the number of required disjoint paths
    Ans = [math.inf]
    print("(s,d)=",(s,d))
    
    while True:
      g = define_sd_pair(g,s,d)
      g2 = define_sd_pair(g2,s,d)
      hop = []
      eta = []
      #variables
      #the number of slots of k-th path
      
      Bhandari()
      
      g = copy.deepcopy(map1)
      g2 = copy.deepcopy(map2)

      if 0 in hop:
        path = [[], []]
        overlapped_link = []
        negative_link = []
        linkset = []
        break
      
      print(str(N)+"本")
      print(hop,eta)
      
      
      for b in T[0]:
        B_max = math.ceil(b/min(eta))    #パスに割り当てるスロット数の上限を定める
        Bk = [0] * N      #Bkの初期設定
        
        cost = math.inf
        
        
        allocation(Bk,eta,hop,N,b,rho,M,0)
        #print(ans_index)
        
        print(cost,opt_Bk)
        
        ans = cost + sum(hop)
        print(ans)
        if Ans[0] > ans:
          Ans[0] = ans
        print(Ans)
      path = [[], []]
      overlapped_link = []
      negative_link = []
      linkset = []
      N +=1
      
    if N == M+1:
      Ans = [0]
      counter += 1
        
    path = [[], []]
    overlapped_link = []
    negative_link = []
    linkset = []
    
    Ans.insert(0,d+1)
    if d == 1:
      with open('result/poly'+str(s+1)+'_b'+str(b)+'_rho'+r+'_M'+str(M)+'.csv','w') as f:
          writer = csv.writer(f)
          writer.writerow(Ans)
    else:
      with open('result/poly'+str(s+1)+'_b'+str(b)+'_rho'+r+'_M'+str(M)+'.csv','a') as f:
          writer = csv.writer(f)
          writer.writerow(Ans)
