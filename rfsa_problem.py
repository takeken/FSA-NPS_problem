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

# パスの長さのクラスわけ
C = [0,1,2,3,4] #パスの長さのクラス
L_c = [250,500,1000,2000,4000] #reach
e_c = [62.5,50,37.5,25,12.5] # 変調効率


K = 1
route = True
while route == True:
  K += 1
  path_index = [k for k in range(K)]
  possible_k_ij = [(k,link) for k in range(K) for link in E] #path k とリンクのとりうる組み合わせ
  possible_k_c = [(k,c) for k in range(K) for c in C] #path k とクラスCのとりうる組み合わせ
  
  x = pulp.LpVariable.dicts('x',possible_k_ij, cat = 'Binary') #x^k_ij
  B = pulp.LpVariable.dicts('B',path_index, lowBound = 0, upBound = 320, cat = 'Integer') #B_k
  a = pulp.LpVariable.dicts('a',possible_k_ij, lowBound = 0, upBound = 320, cat = 'Integer') #a^k_ij
  y = pulp.LpVariable.dicts('y',possible_k_c, cat = 'Binary') #y^k_c(path k のクラス)
  z = pulp.LpVariable.dicts('z',possible_k_ij, lowBound = 0, upBound = 320, cat = 'Integer') #z^k_c
  
  m = LpProblem('RFSA problem'sense = LpMinimize) #モデルの設定
  
  
