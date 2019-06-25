# -*- coding: utf-8 -*-

import sys
import time
from ortools.constraint_solver import pywrapcp

import logging
logging.basicConfig(filename='WorkShiftOptCPv2_log.log', filemode='w', level=logging.DEBUG)
logging._warnings_showwarning


def main():
    
    start = time.time()
    
    solver = pywrapcp.Solver("schedule_shifts")

    # ナース人数
    num_nurses = 8
    # シフト数（甲番、乙番、丙番の３つ）
    num_shifts = 4
    # 最適化対象期間
    num_days = 7
    
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
            [1,2],
            [1,2],
            [1,2],
            [2,3],
            [2,3],
            [2,3],
            [3],
            [3]
    ]
    
    logging.info(['AssignableShifts:', AssignableShifts])
    logging.info(['num_nurses:', num_nurses])
    logging.info(['NerseCompatibility:', NerseCompatibility])
    logging.info(['num_shifts:', num_shifts])

    
    # ナースnが日dに入るシフト番号(一番大事な決定変数)
    shifts = {}
    for n in range(num_nurses):
        for d in range(num_days):
            shifts[n, d] = solver.IntVar(0, num_shifts - 1, "shifts(%i,%i)" % (n, d))

    # 各ナースは1週間に5日以上、6日以下働く制約
    for n in range(num_nurses):
        #solver.Add(solver.Sum([shifts[(n, d)] > 0 for d in range(num_days)]) >= 5)
        solver.Add(solver.Sum([shifts[n, d] > 0 for d in range(num_days)]) <= 6)
        pass
        
    # 各日dのシフトsには2人以下のナースがアサインされる
    for d in range(num_days):
        for s in range(1, num_shifts):
            solver.Add( solver.Sum([shifts[n, d]==s  for n in range(num_nurses)]) == 2
            )

    # 各ナースは、一日に1回しかアサインできない
    # 不要
        
    # ナースのアサイン可能なシフトの制約
    for n in range(num_nurses):
        for d in range(num_days):
            for s in range(1, num_shifts):
                if s not in AssignableShifts[n]:
                    solver.Add(shifts[n,d] != s) 

    # 目的関数
    # ナースn1とナースn2を同じシフトjにアサインしたときの、相性の総和
    obj_func = solver.Sum([
                            NerseCompatibility[n1][n2] * (shifts[n1,d] == s) * ( shifts[n2,d] == s) 
                            for d in range(num_days)
                            for s in range(1, num_shifts)
                            for n1 in range(num_nurses) 
                            for n2 in range(n1+1, num_nurses)
                            
                ])
        
        
    objective = solver.Maximize(obj_func, step=1)

    collector = solver.LastSolutionCollector()
    collector.Add([shifts[n, d] for n in range(num_nurses) for d in range(num_days)])
    collector.AddObjective(obj_func)
    
    db = solver.Phase([shifts[n, d] for n in range(num_nurses) for d in range(num_days)],
                    solver.CHOOSE_FIRST_UNBOUND,
                    solver.ASSIGN_MIN_VALUE)
    
    time_limit = solver.TimeLimit(300000) 
    
    solver.Solve(db,[objective, collector, time_limit])
  
    print("Solutions found:", collector.SolutionCount())
    print("Time:", solver.WallTime(), "ms")
  
    if collector.SolutionCount() > 0:
        best_solution = collector.SolutionCount() - 1
        print("Maximum of objective function:", collector.ObjectiveValue(best_solution))
        print("Minimum of objective function:", collector.ObjectiveValue(0))
  
    a_few_solutions = [0]
 
    for sol in a_few_solutions:
        print("Solution number" , sol, '\n')
        print("obj value" , collector.ObjectiveValue(sol), '\n')
        logging.info(['obj value:', collector.ObjectiveValue(sol)])

    for d in range(num_days):
        print("Day", d)
        for s in range(1, num_shifts):
            for n in range(num_nurses):
                res_s = collector.Value(sol, shifts[n, d])
                if res_s == s:
                    print("shift", s, "assigned nurse",n)  
                    logging.info(["Day", d, "shift", s, "assigned nurse",n])
                    
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")  
    logging.info(['elapsed_time:', elapsed_time])

if __name__ == "__main__":
    main()