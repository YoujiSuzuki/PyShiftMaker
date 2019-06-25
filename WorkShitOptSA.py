# -*- coding: utf-8 -*-

import sys
import time
from ortools.linear_solver import pywraplp
import numpy as np
import WorkShiftOptDefines as wsDef
import MetaHeuristics as mh

import logging
logging.basicConfig(filename='WorkShiftOptSA_log.log', filemode='w', level=logging.DEBUG)
logging._warnings_showwarning
        
def optimize_shift_SA():
    
    start = time.time()
    # ナース人数
    num_nurses = 8
    # シフト数（甲番、乙番、丙番の３つ）
    num_shifts = 3
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
            [0,1],
            [0,1],
            [0,1],
            [1,2],
            [1,2],
            [1,2],
            [2],
            [2]
    ]
    
    logging.info(['num_nurses:', num_nurses])
    logging.info(['NerseCompatibility:', NerseCompatibility])
    logging.info(['num_shifts:', num_shifts])
    logging.info(['AssignableShifts:', AssignableShifts])



    Xconst = wsDef.XConstraint(num_assign_week_min=2, num_assign_week_max=6, assign_in_one_shift_max=2, 
                 num_assign_of_a_nurse_in_day_max=1, AssignableShifts=AssignableShifts,
                 NerseCompatibility=NerseCompatibility)
    print('Xconst', Xconst)
    logging.info(['Xconst:', Xconst])
    
    # 初期解を生成する 決定変数定義　x[ 日d、シフトs, ナースのリスト ]
    x = mh.generate_initial_solution(num_days, num_shifts, num_nurses, Xconst)
    logging.info(['first solution x:', x])
    
    print('Local Search SA solve start')
    
    x = mh.local_searchSA(x, num_days, num_shifts, num_nurses, Xconst, search_loops=1000000)
    
    print('Local Search SA solve end')
    logging.info(['optimal solution x:', x])
    
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
    logging.info(['elapsed_time:', elapsed_time])
        
    return 

if __name__ == "__main__":
    
   optimize_shift_SA()

    
    






