import math
import sys
import copy
import itertools
import topology
#Bhandari algorithm


#networks topology

map1 = topology.COST239_hop

#topology's copy
map2 = topology.COST239_hop


g = copy.deepcopy(map1)
g2 = copy.deepcopy(map2)


#the number of nodes
node_num = len(map1)


node =[a for a in range(node_num)]
s_d = list(itertools.combinations(node,2))
s_d = [(0,9)]



#used path and shortestpath with negative arcs
path = [[], []]

overlapped_link = []
negative_link = []
linkset = []


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


def dijkstra(g,distance, unsearched_nodes, previous_nodes):
  
  while(len(unsearched_nodes) != 0): #until unsearched nodes = 0
    possible_min_distance = math.inf #set initial distance inf
    
    for node_index in unsearched_nodes:
      if possible_min_distance > distance[node_index]:
        possible_min_distance  = distance[node_index]
    
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
  
  # g = define_sd_pair(G,s,d)
  # g2 = define_sd_pair(G2,s,d)
  
  #first dijkstra
  unsearched_nodes = list(range(node_num))
  
  distance = [math.inf] * node_num
  distance[0] = 0
  
  previous_nodes = [-1] * node_num
  
  dijkstra(g,distance, unsearched_nodes,previous_nodes)
  
  
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
        
    # if previous_node != 0:
    #   print(str(previous_node) + "<-", end ='')
      
    # else:
    #   print(str(previous_node))
    
    previous_node = previous_nodes[previous_node]
    
  #print(distance[node_num - 1])
  #print(g)
  count = 1
  while count < N: 
    #dijkstra for the topology with nefative arcs
    unsearched_nodes = list(range(node_num))
    
    distance = [math.inf] * node_num
    distance[0] = 0
    
    previous_nodes = [-1] * node_num
    
    dijkstra(g,distance, unsearched_nodes,previous_nodes)
    
    previous_node = node_num - 1
    present_node = node_num - 1
    
    while previous_node != -1:
      if present_node != previous_node:
        
        g[present_node][previous_node] = - g[present_node][previous_node]
        g[previous_node][present_node] = 0
        
        link = {previous_node,present_node}
        path[1].append(link)
        
        present_node = previous_node
      # if previous_node != 0:
      #   print(str(previous_node) + "<-", end ='')
        
      # else:
      #   print(str(previous_node))
      
      previous_node = previous_nodes[previous_node]
      
    #print(distance[node_num - 1])
      
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
  
  print(g)
  
  
  #get disjoint paths
  for a in range(N):
    unsearched_nodes = list(range(node_num))
    
    distance = [math.inf] * node_num
    distance[0] = 0
    
    previous_nodes = [-1] * node_num
    
    dijkstra(g,distance, unsearched_nodes,previous_nodes)
    
    previous_node = node_num - 1
    present_node = node_num - 1
    hop_count = 0
    while previous_node != -1:
      if present_node != previous_node:
        g[present_node][previous_node] = 0  
        g[previous_node][present_node] = 0
        present_node = previous_node
      if previous_node !=0:
        print(str(previous_node) + " <- ", end='')
      else:
        print(str(previous_node))
      previous_node = previous_nodes[previous_node]
      hop_count += 1
    print(distance[node_num - 1])
    #print(g)
    hop.append(hop_count-1)
    
    eta.append(modulation_decision(distance[node_num-1]))
    
    



    
if __name__ == "__main__":
  for (s,d) in s_d:
    
    print("(s,d)=", (s,d))
    N = 4
    while True:
      g = define_sd_pair(g,s,d)
      g2 = define_sd_pair(g2,s,d)
      hop = []
      eta = []
      Bhandari()
      
      g = copy.deepcopy(map1)
      g2 = copy.deepcopy(map2)
      
      if 0 in hop:
        path = [[], []]
        overlapped_link = []
        negative_link = []
        linkset = []
        break
      print(str(N) + "本")
      print(hop,eta)
      
      path = [[], []]
      overlapped_link = []
      negative_link = []
      linkset = []
      N += 1
    print("-------------")
  



