from __future__ import print_function
import cplex
import sys
import itertools
import math
import copy
import csv
import topology


T = [
[50,100,200,500,1000,2000], #b
[2], #M
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
map1 = topology.USbackbone3
map2 = topology.USbackbone3

g = copy.deepcopy(map1)
g2 = copy.deepcopy(map2)

#the number of nodes
node_num = len(g)

(s,d) = (0,0)
#combination of s and d
nodes =[a for a in range(node_num)]
s_d = list(itertools.combinations(nodes,2))



#slot assignment


slot_sum = [[0]*b_len for a in range(3)]
slot_av = []*3

counter = 0
optim_N = [0 for a in range(b_len)]



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
  for (s,d) in s_d:
    N = M+1 #the number of required disjoint paths
    Ans = [[math.inf]*b_len for a in range(3)]
    print("(s,d)=",(s,d))
    
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
    
    
      #set of paths
      P =[a for a in range(N)]
      
      #survive paths
      not_F = list(itertools.combinations(P,(N-M)))
      #proposed
      for b in T[0]:
        B_k = []
        print(b)
        ans = assignment(b)
        for a in hop:
          ans = ans + a*G #add guardband
      
        if Ans[0][T[0].index(b)] > ans:
          Ans[0][T[0].index(b)] = ans
          
      #capa balance    
      for b in T[0]:
        ans = 0
        #determine b_k
        b_k = b / N
        if b_k * (N-M) < rho*b:
          b_k = rho*b/(N-M)
        
        for a in range(N):
          ans = ans + hop[a]*(math.ceil(b_k/eta[a]) + G)
          
        if Ans[1][T[0].index(b)] > ans:
          Ans[1][T[0].index(b)] = ans

      #slot balance
      for b in T[0]:
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
          
        if Ans[2][T[0].index(b)] > ans:
          Ans[2][T[0].index(b)] = ans
          optim_N[T[0].index(b)] = N
      

      N += 1
    
    if N == M+1:
      Ans = [[0]*b_len]*3
      counter += 1
    
      
    print("optimize solution=", Ans)
    with open('test.csv','a') as f:
        writer = csv.writer(f)
        writer.writerow(Ans)
    for a in range(b_len):
      for b in range(3):
        slot_sum[b][a] = slot_sum[b][a] + Ans[b][a]
    print("----------------------------------")
  
  for a in range(b_len):
    slot_av = [T[0][a], slot_sum[0][a] / (len(s_d)-counter), slot_sum[1][a] / (len(s_d)-counter), slot_sum[2][a] / (len(s_d)-counter)]
    print("average=",slot_av)
    
    if a ==0:
      with open('result/rho'+r+'_M'+str(M)+'.csv','w') as f:
          writer = csv.writer(f)
          writer.writerow(slot_av)
    else:
      with open('result/rho'+r+'_M'+str(M)+'.csv','a') as f:
          writer = csv.writer(f)
          writer.writerow(slot_av)
  print(counter)       


