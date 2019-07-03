from __future__ import print_function
import cplex
import sys
import itertools
import math
import copy
import csv
import topology
import time



s = 0
#bandwidth requirement
b = 2000

#partial protection requirement
rho = 1
r = '1'
#number of failures
M = 2
#guardband
G = 1


#networks topology
map1_2 = topology.COST239
#map2 = topology.COST239

map1 = topology.COST239_hop
map2 = topology.COST239_hop

g = copy.deepcopy(map1)
g2 = copy.deepcopy(map2)
G1 = copy.deepcopy(map1_2)

#the number of nodes
node_num = len(g)


#used path and shortestpath with negative arcs
path = [[], []]

overlapped_link = []
negative_link = []
linkset = []


#slot assignment




def define_sd_pair(g,s,d):
  g[s],g[0] = g[0],g[s]
  for a in g:
    a[s],a[0] = a[0],a[s]
  g[d],g[node_num-1] = g[node_num-1],g[d]
  for a in g:
    a[d],a[node_num-1] = a[node_num-1],a[d]
  
  return g



def get_target_min_index(min_index, hops, unsearched_nodes):
  start = 0
  while True:
    index = hops.index(min_index,start)
    found = index in unsearched_nodes
    if found:
      return index
    else:
      start = index + 1


def dijikstra(hops,distance,unsearched_nodes, previous_nodes):
  
  while(len(unsearched_nodes) != 0): #until unsearched nodes = 0
    possible_min_hops = math.inf #set initial hops inf
    
    for node_index in unsearched_nodes:
      if possible_min_hops > hops[node_index]:
        possible_min_hops = hops[node_index]
    
    target_min_index = get_target_min_index(possible_min_hops, hops, unsearched_nodes)
    
    unsearched_nodes.remove(target_min_index) #remove a unsearched node
    
    target_edge = g[target_min_index]#list of edge from target node
    
    for index, route_dis in enumerate(target_edge):
      if route_dis != 0:
        if hops[index] > (hops[target_min_index]) + route_dis:
          
          hops[index] = hops[target_min_index] + route_dis
          distance[index] = distance[target_min_index] + G1[target_min_index][index]
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
  
  hops = [math.inf] * node_num
  distance = [0] * node_num
  hops[0] = 0
  
  previous_nodes = [-1] * node_num
  
  dijikstra(hops,distance, unsearched_nodes,previous_nodes)
  
  
  #make the length of each edges negative and print the path and the hops
  
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
    
    hops = [math.inf] * node_num
    distance = [0] * node_num
    hops[0] = 0
    
    previous_nodes = [-1] * node_num
    
    dijikstra(hops,distance,unsearched_nodes,previous_nodes)
    
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
    
    hops = [math.inf] * node_num
    distance = [0] * node_num
    hops[0] = 0
    
    previous_nodes = [-1] * node_num
    
    dijikstra(hops,distance,unsearched_nodes,previous_nodes)
    
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




#############
def setupproblem(c,b):
  
  c.objective.set_sense(c.objective.sense.minimize)
  
  # assignment variables:B_k

  for a in range(N):
    varname = "B_" + str(a)

    B_k.append(varname)





###############


  #objective
  
  c.variables.add(names=B_k,
                  lb=[1]*len(B_k),
                  ub=[320]*len(B_k),
                  types=["I"]*len(B_k),
                  obj = hop)


#constraints

  #\sum_{k in K}\eta_k*B_k >= b
  thevars = []
  thecoefs = []
  for a in P:
    thevars.append(B_k[a])
    thecoefs.append(eta[a])
    
  c.linear_constraints.add(lin_expr=[cplex.SparsePair(thevars, thecoefs)],
                           senses=["G"],
                           rhs=[b])
    
  #\sum _{k\in K:k\not\in F}eta_k*B_k >= rho*b
  for not_f in not_F:
    thevars = []
    thecoefs = []
    for a in list(not_f):
      thevars.append(B_k[a])
      thecoefs.append(eta[a])
      
    c.linear_constraints.add(lin_expr=[cplex.SparsePair(thevars, thecoefs)],
                             senses=["G"],
                             rhs=[rho*b])
   
   
   
   
#########


def assignment(b):
  
  c = cplex.Cplex()
  
  setupproblem(c,b)
  
  #c.write("MPP.lp")
  
  c.solve()
  
  
  sol = c.solution
  
  print()
  
  if sol.is_primal_feasible():
    ans = int(sol.get_objective_value())
    print(ans)
  
    print("B_k = {0}" .format(
      sol.get_values(B_k)))
  
    print()
  
  
  else:
    print("No solution available.")
  
  return ans


if __name__ == "__main__":
  s = 0
  for d in range (1,node_num):
    N = M+1 #the number of required disjoint paths
    opt_allocation = math.inf
    print("(s,d)=",(s,d))
    start_time = time.time()
    while True:
      g = define_sd_pair(g,s,d)
      g2 = define_sd_pair(g2,s,d)
      G1 = define_sd_pair(G1,s,d)
      hop = []
      eta = []
      #variables
      #the number of slots of k-th path
      
      Bhandari()
      
      g = copy.deepcopy(map1)
      g2 = copy.deepcopy(map2)
      G1 = copy.deepcopy(map1_2)

      if 0 in hop:
        path = [[], []]
        overlapped_link = []
        negative_link = []
        linkset = []
        break
      
      print(str(N)+"本")
      print(hop,eta)
    
    
      #set of paths
      P =[a for a in range(N)]
      
      #survive paths
      not_F = list(itertools.combinations(P,(N-M)))
      #proposed
      B_k = []
      print(b)
      ans = assignment(b)
      for a in hop:
        ans = ans + a*G #add guardband
    
      if opt_allocation > ans:
        opt_allocation = ans
          
      

      path = [[], []]
      overlapped_link = []
      negative_link = []
      linkset = []
      N += 1
    
    if N == M+1:
      opt_allocation = 0
      counter += 1
    
    
    path = [[], []]
    overlapped_link = []
    negative_link = []
    linkset = []
    
    timer = time.time() - start_time
    print('minimized required spectrum resource is ' + str(int(opt_allocation)))
    Ans = [d+1,opt_allocation,timer]
    if d == 1:
      with open('result/fsa_hop'+str(s+1)+'_b'+str(b)+'_rho'+r+'_M'+str(M)+'.csv','w') as f:
          writer = csv.writer(f)
          writer.writerow(Ans)
    else:
      with open('result/fsa_hop'+str(s+1)+'_b'+str(b)+'_rho'+r+'_M'+str(M)+'.csv','a') as f:
          writer = csv.writer(f)
          writer.writerow(Ans)


