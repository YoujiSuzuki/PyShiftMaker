# -*- coding: utf-8 -*-

import sys
import time
from ortools.linear_solver import pywraplp
import numpy as np

import logging
logging.basicConfig(filename='WorkShiftOptMIP_log.log', filemode='w', level=logging.DEBUG)
logging._warnings_showwarning


def optimize_shift_mip():
    
    start = time.time()

    solver = pywraplp.Solver('schedule_shifts',
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    # ナース人数
    num_nurses = 8
    # シフト数（甲番、乙番、丙番の３つ）
    num_shifts = 3
    # 最適化対象期間
    num_days = 3
    
    
    # ナースどうしの相性 縦軸ナースn1 横軸ナースn2
    NerseCompatibility = [
                    [0, 100, 100, 100, 100, 100, 100, 100],
                    [0,   0, 100,  90,  90,  90,  90,  90],
                    [0,   0,   0, 110,  80,  95,  92,  92],
                    [0,   0,   0,   0,  80,  95,  90,  90],
                    [0,   0,   0,   0,   0, 105,  90,  90],
                    [0,   0,   0,   0,   0,   0,  90,  90],
                    [0,   0,   0,   0,   0,   0,   0,  90],
                    [0,   0,   0,   0,   0,   0,   0,   0]
                ]
    
    # 各ナースの入れるシフト
    AssignableShifts = [
            [0,1],
            [0,1],
            [0,1],
            [1,2],
            [1,2],
            [1,2],
            [2],
            [2]
    ]
    
    logging.info(['AssignableShifts:', AssignableShifts])
    logging.info(['num_nurses:', num_nurses])
    logging.info(['NerseCompatibility:', NerseCompatibility])
    logging.info(['num_shifts:', num_shifts])

    # ナースnを日dのシフトsに割り当てる決定変数
    x = {}
    for n1 in range(num_nurses):
        for d1 in range(num_days): 
            for s1 in range(num_shifts):
                x[n1,d1,s1] = solver.IntVar(0, 1, "x%d,%d,%d" % (n1, d1, s1))
  
    # 各ナースは1週間に5日以上、6日以下働く制約
    for n1 in range(num_nurses):
        #solver.Add(solver.Sum([x[n1,d1,s1] for d in range(num_days) for s in range(num_shifts)]) >= 1)
        solver.Add(solver.Sum([x[n1,d1,s1] for d1 in range(num_days) for s1 in range(num_shifts)]) <= 6)
        pass
        
    # 各日のシフトsには2人のナースがアサインされる
    for d1 in range(num_days):
        for s1 in range(num_shifts):
            #solver.Add(solver.Sum([x[n1,d1,s1] for n1 in range(num_nurses)]) <= 2)
            solver.Add(solver.Sum([x[n1,d1,s1] for n1 in range(num_nurses)]) == 2)
            pass
        
    # 各ナースは、一日に1回しかアサインできない
    for n in range(num_nurses):
        for d in range(num_days):
            solver.Add(solver.Sum([x[n,d,s] for s in range(num_shifts)]) <= 1)
            pass
        
    # ナースのアサイン可能なシフトの制約
    for n in range(num_nurses):
        for d in range(num_days):
            for s in range(num_shifts):
                if s not in AssignableShifts[n]:
                    solver.Add(x[n,d,s] == 0) 

           
    print('Add Constraint x Complete')
       
    # ナースn1をシフトd1s1に、ナースn2をシフトd2s2に割り当てる変数y[n1,d1s1,n2,d2s2]
    y = {}
    ctr = 0
    for n1 in range(num_nurses):
        for d1 in range(num_days):    
            for s1 in range(num_shifts):
                for n2 in range(n1, num_nurses):#if n1 < n2:
                    for d2 in range(num_days):    
                        for s2 in range(num_shifts):
                            y[n1, d1, s1, n2, d2, s2] = solver.IntVar(0, 1, 'y(%d)' % (ctr))
                            ctr += 1
    print('Make Y Complete size:', ctr)
    
    # 制約条件1  xとyの関係
    for n1 in range(num_nurses):
        for d1 in range(num_days):    
            for s1 in range(num_shifts):
                for n2 in range(n1, num_nurses):#if n1 < n2:
                    for d2 in range(num_days):    
                        for s2 in range(num_shifts):
                            # z >= x + y - 1, z <= x, z <= y の 3 本の不等式による x, y, z に関する 0-1 表現
                            solver.Add( x[n1,d1,s1] >=  y[n1, d1, s1, n2, d2, s2])
                            solver.Add( x[n2,d2,s2] >=  y[n1, d1, s1, n2, d2, s2])
                            solver.Add( (x[n1,d1,s1] + x[n2,d2,s2] -1) <=  y[n1, d1, s1, n2, d2, s2])

    #n1とn2を同じシフトに割り当てたときに１となる行列
    IsSameShift = np.zeros([num_nurses, num_days, num_shifts, num_nurses, num_days, num_shifts])
    for n1 in range(num_nurses):
        for d1 in range(num_days):    
            for s1 in range(num_shifts):
                for n2 in range(num_nurses):
                    for d2 in range(num_days):    
                        for s2 in range(num_shifts):  
                            if n1 < n2 and d1 == d2 and s1 == s2:
                                IsSameShift[n1, d1, s1, n2, d2, s2] = 1


    # iとpが同じグループjqに割り当てられたときの相性を合計する   
    solver.Maximize(
        solver.Sum(
                [ (y[n1, d1, s1, n2, d2, s2] * (NerseCompatibility[n1][n2]) * IsSameShift[n1, d1, s1, n2, d2, s2])
                    for n1 in range(num_nurses)
                        for d1 in range(num_days)   
                            for s1 in range(num_shifts)
                                for n2 in range(n1,num_nurses)#if n1 < n2:
                                    for d2 in range(num_days)   
                                        for s2 in range(num_shifts)
                ]
        )
    )

        
    print("Set Objective Function Complete")   
    print("Solve Start !!!!")
    status = solver.Solve()  

    x_solval = {}
    if status == solver.OPTIMAL or status == solver.FEASIBLE:
        print('Solution:')
        obj = solver.Objective()
        
        for d1 in range(num_days):
            print("Day", d1)
            for s1 in range(num_shifts):
                for n1 in range(num_nurses):
                    x_solval[n1, d1, s1] = x[n1, d1, s1].SolutionValue()
                    if x_solval[n1, d1, s1] > 0.5:
                        print("shift", s1, "assigned nurse",n1)   
                        logging.info(["Day", d1, "shift", s1, "assigned nurse",n1])

        print('obj value: = ', obj.Value())
        logging.info(['obj.Value():', obj.Value()])
        
        # 各ナースの合計アサイン回数
        for n1 in range(num_nurses):
            print('nurse', n1, 'sum_assign', np.sum([x_solval[n1, d1, s1] for s1 in range(num_shifts) for d1 in range(num_days) ]))
        
        
  
    else:
        print('Infeasible')
        
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
    logging.info(['elapsed_time:', elapsed_time])
        
    return x_solval, NerseCompatibility, IsSameShift

if __name__ == "__main__":
    
    x_solval, NerseCompatibility, IsSameShift = optimize_shift_mip()