# modified dijkstra
import math
import sys
import copy
import itertools
import topology


#target topology
map1 = topology.COST239

#topology's copy
map2 = topology.COST239


g = copy.deepcopy(map1)
g2 = copy.deepcopy(map2)


#the number of nodes
node_num = len(map1)


node =[a for a in range(node_num)]
s_d = list(itertools.combinations(node,2))
s_d = [(0,9)]

def dijkstra(g,s,d):
  S_bar =[] #list of neighbor nodes
  predecessor = [None] * node_num
  
  # step 1
  
  distance = [math.inf] * node_num #distance of i from s
  distance[s] = 0 #source node
  for index in range(node_num):
    if g[index][s] > 0:
      distance[index] = g[index][s]
      predecessor[index] = s
      S_bar.append(index)
  
  while True:
    
    
    # step 2
    
    j = get_j(S_bar,distance)
    print('j =',j)
    print(S_bar)
    S_bar.remove(j)
    print('after remove',S_bar)
    if j == d:
      break
    
    
    # step 3
    
    for index in range(node_num):
      if g[j][index] != 0:
        print('distance = ',distance)
        if distance[j] + g[j][index] < distance[index]:
          distance[index] = distance[j] + g[j][index]
          predecessor[index] = j
          if (index in S_bar) == False:
            print(S_bar)
            S_bar.append(index)
            print(S_bar)
    
  return distance,predecessor
    

def get_j(S_bar,distance):
  min_dis = math.inf
  for index in S_bar:
    if min_dis > distance[index]:
      min_dis = distance[index]
      min_i = index
  return min_i

if __name__ == "__main__":
  for (s,d) in s_d:
    distance,predecessor = dijkstra(g,s,d)
    print(distance)
    print(predecessor)
    p = d
    while p != None:
      if p != s:
        print(str(p) + " <- ", end='')
      else:
        print(str(p))
      p = predecessor[p]
            
    
