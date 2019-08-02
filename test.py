#Bhandari algorithm
import math
import sys
import copy
import itertools
import topology


#networks topology

map1 = topology.USbackbone
map2 = topology.USbackbone


g = copy.deepcopy(map1)
g2 = copy.deepcopy(map2)


#the number of nodes
node_num = len(map1)


nodes =[a for a in range(node_num)]
# s_d = list(itertools.combinations(nodes,2))
s_d = [(0,15)]



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
    
    print('j =',j+1)
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
            print(S_bar)
    
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
  for (s,d) in s_d:
    
    print("(s,d)=", (s+1,d+1))
    count = Bhandari(s,d)
      # g = copy.deepcopy(map1)
      # g2 = copy.deepcopy(map2)
      
    print(str(count) + "本")
    print("-------------")
  



