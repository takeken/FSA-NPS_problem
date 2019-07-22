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
rho = 0.5
r = '05'
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
nodes =[a for a in range(node_num)]


#slot assignment

def dijkstra(s,d):
  S_bar =[] #list of neighbor nodes
  predecessor = [None] * node_num
  
  # step 1
  
  hop_num = [math.inf] * node_num #hop_num of i from s
  hop_num[s] = 0 #source node
  for index in nodes:
    if g[index][s] > 0:
      hop_num[index] = g[index][s]
      predecessor[index] = s
      S_bar.append(index)
  
  while True:
    
    
    # step 2
    
    j = get_j(S_bar,hop_num)
    if j == d:
      break
    #print('j =',j)
    S_bar.remove(j)
    
    
    
    # step 3
    # print(g[j])
    for index in nodes:
      if g[j][index] != 0:
        
        if hop_num[j] + g[j][index] < hop_num[index]:
          hop_num[index] = hop_num[j] + g[j][index]
          predecessor[index] = j
          
          if (index in S_bar) == False:

            S_bar.append(index)
    
  return hop_num,predecessor
    

def get_j(S_bar,hop_num):
  min_dis = math.inf
  min_i = d
  for index in S_bar:
    if min_dis > hop_num[index]:
      min_dis = hop_num[index]
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
  
  hop_num,predecessor = dijkstra(s,d)
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
    hop_num,predecessor = dijkstra(s,d)
    # print(predecessor)
    p = d
    while p != None:
      pre = predecessor[p]
      if p != s and pre != None:
        
        #replace the overlapping links with the original links
        
        if g[pre][p] < 0:
          g[pre][p] = g2[pre][p]
          g[p][pre] = g2[p][pre]
        
        #make the length of each edges negative and print the path and the hop_num
        
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
    
    hop_num,predecessor = dijkstra(s,d)
    # print('hop_num = ',hop_num)
    hop_count = 0
    distance = 0
    p = d
    # print(predecessor)
    while p != None:
      pre = predecessor[p]
      if p != s and pre != None:
        g[p][pre] = 0
        g[pre][p] = 0
        
        print(str(p) + " <- ", end='')
        hop_count += 1
        distance += G1[pre][p]
      else:
        print(str(p))
        
        
      p = pre
      
    #print(g)
    hop.append(hop_count)
    
    eta.append(modulation_decision(distance))




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
      hop = []
      eta = []
      #variables
      #the number of slots of k-th path
      
      Bhandari()
      
      g = copy.deepcopy(map1)
      g2 = copy.deepcopy(map2)
      G1 = copy.deepcopy(map1_2)

      if 0 in hop:
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
          
      
      N += 1
    
    if N == M+1:
      opt_allocation = 0
      counter += 1
    
    
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


