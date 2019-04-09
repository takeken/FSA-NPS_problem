from __future__ import print_function
import cplex
import sys
import itertools
import math
import copy
#import topology


#sys.setrecursionlimit(100)
b = 100
rho = 1
N = 3
M = 1
eta = [50,25,25]
hop = [1,2,3]




# コストを計算
def cal_cost(Bk,hop):
  Bkhop = [x*y for (x,y) in zip(Bk,hop)]
  cost = sum (Bkhop)
  return cost

  
  

#要求を満たすか確認
def check(Bk,eta,N,b,rho,M):
  b_sum = 0
  
  bk = [Bk[k]*eta[k] for k in range(N)]
  #print(Bk,bk)
  b_sum = sum(bk)   #通常時の伝送容量
  
  if b_sum < b or b_sum -  sum (sorted (bk, reverse = True)[:M]) < rho*b:  ##合計伝送容量が足りない or M本故障時の伝送容量
    return 0      #故障時に耐えれない
  else:
    return 1  #トラヒック要求を満たす


#割り当てを決める
def allocation(Bk,eta,hop,N,b,rho,M,n):
  global cost
  global opt_Bk
  if (n == N ):# ネストの最深部まできている場合
    #for i in range(1, B_max+1):
      #Bk[n] = i
        
    if check(Bk,eta,N,b,rho,M) == 1:   # Bkが要求を満たすか調べる
      if cost >= cal_cost(Bk,hop):    # コストを比較し小さければ更新
        cost = cal_cost(Bk,hop)
        print(cost,Bk)
        opt_Bk = Bk
        #print(Bk)
        #print(cost)
      return
        
    return
  else:
    for i in range(1, B_max+1):
      Bk[n] = i
      allocation(Bk,eta,hop,N,b,rho,M,n+1)
    return
            

        
    





if __name__ == "__main__":
  B_max = math.ceil(b/min(eta))    #パスに割り当てるスロット数の上限を定める
  Bk = [0] * N      #Bkの初期設定
  opt_Bk = [0] * N
  cost = math.inf
  
  
  allocation(Bk,eta,hop,N,b,rho,M,0)
  print(cost)
  print(opt_Bk)
          
        
      
    
    
    
  

  
  
    
  
  
  


