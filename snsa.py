from __future__ import print_function
import sys
import itertools
import math
import copy
import csv
import topology
import time




#bandwidth requirement
b = 2000
#number of failures
M = 1
#partial protection requirement
rho = 1
r = '1'
#guardband
G = 1


#networks topology
map1 = topology.COST239
map2 = topology.COST239

g = copy.deepcopy(map1)
g2 = copy.deepcopy(map2)

#the number of nodes
node_num = len(g)


#combination of s and d
nodes =[a for a in range(node_num)]
s_d = []
for a in range(1,node_num):
  s_d.append([0,a])



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
  
  while True:
    
    
    # step 2
    
    j = get_j(S_bar,distance)
    if j == d:
      break
    #print('j =',j)
    S_bar.remove(j)
    
    
    
    # step 3
    # print(g[j])
    for index in nodes:
      if g[j][index] != 0:
        
        if distance[j] + g[j][index] < distance[index]:
          distance[index] = distance[j] + g[j][index]
          predecessor[index] = j
          
          if (index in S_bar) == False:

            S_bar.append(index)
    
  return distance,predecessor
    

def get_j(S_bar,distance):
  min_dis = math.inf
  min_i = d
  for index in S_bar:
    if min_dis > distance[index]:
      min_dis = distance[index]
      min_i = index
  return min_i
  

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
  while count < N: 
    distance,predecessor = dijkstra(s,d)
    # print(predecessor)
    p = d
    while p != None:
      pre = predecessor[p]
      if p != s and pre != None:
        
        #replace the overlapping links with the original links
        
        if g[pre][p] < 0:
          g[pre][p] = g2[pre][p]
          g[p][pre] = g2[p][pre]
        
        #make the length of each edges negative and print the path and the distance
        
        else:
          g[p][pre] = - g[p][pre]
          g[pre][p] = 0
      p = pre

    count += 1
  
  
  #replace links we should use (negative arcs will be used)
  for i in nodes:
    for j in nodes:
      if g[i][j] > 0:
        g[i][j] = 0
  for i in nodes:
    for j in nodes:
      if g[i][j] < 0:
        g[i][j] = g2[i][j]
        g[j][i] = g2[j][i]
  
  
  #get N disjoint paths
  
  for a in range(N):
    
    distance,predecessor = dijkstra(s,d)
    # print('distance = ',distance)
    hop_count = 0
    
    p = d
    # print(predecessor)
    while p != None:
      pre = predecessor[p]
      if p != s and pre != None:
        g[p][pre] = 0
        g[pre][p] = 0
        
        print(str(p) + " <- ", end='')
        hop_count += 1
      else:
        print(str(p))
        
        
      p = pre
      
    #print(g)
    hop.append(hop_count)
    
    eta.append(modulation_decision(distance[d]))




if __name__ == "__main__":
  for (s,d) in s_d:
    N = M+1 #the number of required disjoint paths
    opt_allocation = math.inf
    print("(s,d)=",(s,d))
    start_time = time.time()
    while True:
      hop = []
      eta = []
      #variables
      #the number of slots of k-th path
      
      Bhandari()
      
      g = copy.deepcopy(map1)
      g2 = copy.deepcopy(map2)

      if 0 in hop:
        break
      
      print(str(N)+"本")
      print(hop,eta)
    
    
      #slot balance
      ans = 0
      #determine B_k
      B_k =1
      eta.sort(reverse=True)
      while True:
        if B_k*sum(eta) >= b:
          eta_sum = sum(eta)
          for a in range(M):
            eta_sum = eta_sum - eta[a]
          if B_k*eta_sum <  rho*b:
            B_k += 1
          else:
            break
        else:
          B_k += 1
          
      for a in range(N):
        ans = ans + hop[a]*(B_k + G)
      if opt_allocation > ans:
        opt_allocation = ans
        optim_N = N

      N += 1
    
    if N == M+1:
      opt_allocation = 0
    
    timer = time.time() - start_time
    print("Solved in %s seconds." % timer)
    print("optimize solution=" + str(int(opt_allocation)))
    
    
    print("----------------------------------")
    
    Ans = [d+1,opt_allocation,timer]
    if d == 1:
      with open('result/snsa'+str(s+1)+'_b'+str(b)+'_rho'+r+'_M'+str(M)+'.csv','w') as f:
          writer = csv.writer(f)
          writer.writerow(Ans)
    else:
      with open('result/snsa'+str(s+1)+'_b'+str(b)+'_rho'+r+'_M'+str(M)+'.csv','a') as f:
          writer = csv.writer(f)
          writer.writerow(Ans)


