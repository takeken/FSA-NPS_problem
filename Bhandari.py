#Bhandari algorithm
import math
import sys
import copy
import itertools
import topology


#networks topology

map1 = topology.COST239

#topology's copy
map2 = topology.COST239


g = copy.deepcopy(map1)
g2 = copy.deepcopy(map2)


#the number of nodes
node_num = len(map1)


nodes =[a for a in range(node_num)]
s_d = list(itertools.combinations(nodes,2))
s_d = [(0,9)]



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
        
        if distance[j] + g[index][j] < distance[index]:
          distance[index] = distance[j] + g[j][index]
          predecessor[index] = j
          
          if (j in S_bar) == False:

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
    
    print("(s,d)=", (s,d))
    N = 2
    while True:
      
      hop = []
      eta = []
      Bhandari(s,d)
      
      g = copy.deepcopy(map1)
      g2 = copy.deepcopy(map2)
      
      if 0 in hop:
        break
      print(str(N) + "本")
      print(hop,eta)
      
      N += 1
    print("-------------")
  



