from __future__ import print_function
import cplex
import sys
import itertools
import math
import copy
import csv
import topology
import pulp

# グラフの定義
g = [
[0, 500, 800, 0, 1500],
[500, 0, 200, 150, 0 ],
[800, 200, 0, 100, 150],
[0, 150, 100, 0, 300],
[1500, 0, 150, 300, 0]
]
g_length = len(g)
V = [a for a in range(g_length)] #ノードの集合
E = [] #リンクの集合
for i in V:
    for j in range(g_length):
        if g[i][j]  >0:
            E.append((i,j))

#要求の設定
b = 1000 #要求伝送容量 
rho = 1 #partial protection requirement
M = 1 # 耐えうるパスの故障本数
G = 1 # ガードバンドに必要なスロット数
(s,d) = (0,4)

# パスの長さのクラスわけ
C = [0,1,2,3,4] #パスの長さのクラス
L_c = [250,500,1000,2000,4000] #reach
e_c = [62.5,50,37.5,25,12.5] # 変調効率


alpha = 1000

N = 1 #pathの本数
route = True
while route == True:
  N += 1
  
  
def rfsa_problem():
  K = [k for k in range(N)]
  F = pulp.combination(K,M)
  possible_k_ij = [(k,link) for k in range(N) for link in E] #path k とリンクのとりうる組み合わせ
  possible_k_c = [(k,c) for k in range(N) for c in C] #path k とクラスCのとりうる組み合わせ
  
  # Variables
  x = pulp.LpVariable.dicts('x',possible_k_ij, cat = 'Binary') #x^k_ij
  B = pulp.LpVariable.dicts('B',path_index, lowBound = 0, upBound = 320, cat = 'Integer') #B_k
  a = pulp.LpVariable.dicts('a',possible_k_ij, lowBound = 0, upBound = 320, cat = 'Integer') #a^k_ij
  y = pulp.LpVariable.dicts('y',possible_k_c, cat = 'Binary') #y^k_c(path k のクラス)
  z = pulp.LpVariable.dicts('z',possible_k_c, lowBound = 0, upBound = 320, cat = 'Integer') #z^k_c
  
  #
  #モデルの設定
  m = pulp.LpProblem('RFSA problem'sense = LpMinimize)
  
  #
  # objective function 
  m += pulp.lpSum(a[i]+G*x[i] for i in possible_k_ij)
  
  #
  # constraints
  #
  
  #use N path 
  for k in path_index:
    m += B[k] >= 1
  
  # traffic capacity
  m += b <= pulp.lpSum(e_c[c]*z[(k,c)] for (k,c) in possible_k_c)
  
  for f in F:
    m += rho*b <= pulp.lpSum(e_c[c]*z[(k,c)] for (k,c) in list(set(possible_k_c)-set(f))) 
  
  #flow
  for k in K:
    m += pulp.lpSum(x[(k,(i,j))] for (i,j) in E if i == s) - pulp.lpSum(x[(k,(j,i))] for (j,i) in E if i == s) ==1
  
    m += pulp.lpSum(x[(k,(i,j))] for (i,j) in E if (i != s) and (i != d)) - pulp.lpSum(x[(k,(j,i))] for (j,i) in E if (i != s) and (i != d)) ==0
  
  # link disjoint
  for e in E:
    m += pulp.lpSum(x[(k,e)] for k in K) <= 1
  
  # a^k_ij
  for k in K:
    for e in E:
      m += a[(k,e)] >= B[k] + alpha*(x[(k,e)]-1)
      m += a[(k,e)] <= alpha*x[(k,e)]
      m += a[(k,e)] >= 0
  
  # path length class
  for k in K:
    m += pulp.lpSum(g[i][j]*x[(k,(i,j))]) <= pulp.lpSum(L_c[c]*y[(k,c)] for c in C)
    m += pulp.lpSum(y[c] for c in C) == 1
  
  # z^k_c
  for k in K:
    for c in C:
      m += z[(k,c)] >= B[k] + alpha*(y[(k,c)]-1)
      m += z[(k,c)] <= alpha*y[(k,c)]
      m += z[(k,c)] >= 0

      
      
  
  
  
  