from __future__ import print_function
import cplex
import sys
import itertools
import math
import copy
import csv
import topology
import pulp

b = 1000 #要求伝送容量 
rho = 1 #partial protection requirement
M = 1 # 耐えうるパスの故障本数
G = 1 # ガードバンドに必要なスロット数


m = LpProblem('RFSA problem'sense = LpMinimize)
