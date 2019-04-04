from __future__ import print_function
import cplex
import sys
import itertools
import math
import copy
#import topology


cost_ls = []
b = 150
N = 3
eta = [50,25,25]
hop = [1,2,3]


#全ての割り当てパターンとそのコストをリスト化
def make_list(b,hop,N):
  
  B_max = math.ceil(b/min(eta))    #パスに割り当てるスロット数の上限を定める
  
  #割り当てを全て書き出す。
  Bk_ls = [a+1 for a in range(B_max)]
  Bk_comb =list(itertools.product(Bk_ls, repeat=N))
  
  #各割り当て時の使用スペクトル資源をリスト化
  for a in Bk_comb:
    cost = 0
    for k in range(N):
      cost = a[k]*hop[k] + cost
    cost_ls.append(cost)
    
  return cost_ls,Bk_comb


#コスト順にソートした時のインデックスを取得
def sort_list(cost_ls):
  sort_index = sorted(range(len(cost_ls)), key=lambda k: cost_ls[k])
  return sort_index
  
  
#ソート後のインデックス順に要求を満たすか確認
def check(a,Bk_comb,eta,N,b,M):
  b_sum = 0
  Bk = Bk_comb[a]
  
  bk = [Bk[k]*eta[k] for k in range(N)]
  b_sum = sum(bk)   #通常時の伝送容量
    
  if b_sum < b:
    return 0
  else:
    if b_sum -  sum (sorted (bk, reverse = True)[:M]) < 0:  #M本故障時の伝送容量
      return 0
    else:
      return 1
    
  


if __name__ == "__main__":
  
  cost_ls, Bk_comb = make_list(100,hop,N)
  #print(cost_ls)
  sort_index = sort_list(cost_ls)
  #print(sort_index)
  #print(len(cost_ls))
  #print(Bk_comb[sort_index[1]])
  
  for index in sort_index:
    if check(index,Bk_comb,eta,N,b,1) == 1:
      ans_index = index
      break
  
  print(Bk_comb[ans_index])
  
  
    
  
  
  



