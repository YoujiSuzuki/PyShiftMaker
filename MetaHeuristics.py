# -*- coding: utf-8 -*-

import sys
import time
import numpy as np
import random
import copy

import WorkShiftOptDefines

import logging
logging.basicConfig(filename='WorkShiftOptMIP_log.log', filemode='w', level=logging.DEBUG)
logging._warnings_showwarning

def set_nurse_to_x(x, asg_nurse, num_days, num_shifts, num_nurses, Xconst):
    all_assigned = True
    asg_sccessful = False
    for d in range(num_days):
        for s in range(num_shifts):
            for n in range(Xconst.assign_in_one_shift_max):
                
                if  x[d][s][n] is None:
                    if asg_sccessful == False:
                        x[d][s][n] = asg_nurse
                        if check_constraint(x, num_days, num_shifts, num_nurses, Xconst) == True:
                            asg_sccessful = True
                        else:
                            x[d][s][n] = None
                            
                if  x[d][s][n] is None:
                   all_assigned = False
    if all_assigned == True:
        return x, 9999
    else:
        if asg_sccessful:
            return x, 1
        else:
            return x, 0

def generate_initial_solution(num_days, num_shifts, num_nurses, Xconst):
    x = []
    for d in range(num_days):
        x.append([[None for n in range(Xconst.assign_in_one_shift_max)] for s in range(num_shifts)])

    for i in range(100):
        for asg_nurse in range(num_nurses):
            x , status = set_nurse_to_x(x, asg_nurse, num_days, num_shifts, num_nurses, Xconst)
            if status == 9999:
                print('generate_initial_solution complete')
                return x
            elif status == 1:
                pass
            else:
                pass
    
    # 各シフトのナースリストを、ナース番号でソートする（目的関数計算のため）
#    for d in range(num_days):
#        for s in range(num_shifts):S
#            x[d][s] = sorted(x[d][s])
    print('generate_initial_solution function exit')
    return x


def check_constraint(x, 
                     num_days,
                     num_shifts,
                     num_nurses,
                     Xconst,
                     ascend = False):
    
    # 各シフトのナース番号は、昇順でなければならない
    if ascend:
        for d in range(num_days):
            for s in range(num_shifts):
                for n in range(0, Xconst.assign_in_one_shift_max-1):
                    if x[d][s][n] >= x[d][s][n+1]:
                        return False
    
    #各ナースは1週間に5日以上、6日以下働く制約
    #for d in range(num_days):    
    #各日のシフトsには2人のナースがアサインされる    
    
    #各ナースは、一日に1回しかアサインできない   
    for nurse in range(num_nurses):
        for d in range(num_days):
            if sum([1 for s in range(num_shifts) 
                        for n in range(Xconst.assign_in_one_shift_max)
                            if x[d][s][n] is not None
                                if x[d][s][n] == nurse]) > Xconst.num_assign_of_a_nurse_in_day_max:
                return False    
    

     
    #ナースのアサイン可能なシフトの制約
    if sum([1 for d in range(num_days) 
            for s in range(num_shifts) 
                for n in range(Xconst.assign_in_one_shift_max)
                    if x[d][s][n] is not None
                    if s not in Xconst.AssignableShifts[x[d][s][n]]]) > 0:
        return False
    
    return True

def objective_function(x, 
                     num_days,
                     num_shifts,
                     num_nurses,
                     Xconst):
    
    return(sum([ Xconst.NerseCompatibility[x[d][s][0]][x[d][s][1]]   
        for d in range(num_days)
        for s in range(num_shifts)]))

    
def sa_1opt(x, num_days, num_shifts, num_nurses, Xconst, prev_obj_val):
    
    obj_val = 0
    d1 = random.randrange(num_days)
    d2 = d1
    #d2 = random.randrange(num_days)
    s1 = random.randrange(num_shifts)
    s2 = random.randrange(num_shifts)
    n1 = random.randrange(Xconst.assign_in_one_shift_max)
    n2 = random.randrange(Xconst.assign_in_one_shift_max)

    if d1 == d2 and s1 == s2:
        return x, 0
    
    if x[d1][s1][n1] == x[d2][s2][n2]:
        return x, 0
    
    x1 = copy.deepcopy(x[d1][s1][n1])
    x2 = copy.deepcopy(x[d2][s2][n2])
    
    #print(d1,s1,n1, ' ', d2, s2, n2, '  / ', x1, x2)
    
    x[d1][s1][n1] = x2
    x[d2][s2][n2] = x1
    
    if check_constraint(x, num_days, num_shifts, num_nurses, Xconst, ascend=True):
        obj_val = objective_function(x, num_days, num_shifts, num_nurses, Xconst)
        #print('obj_val', obj_val)
        if prev_obj_val < obj_val:
            print('new solution update obj_val', obj_val)
        else:
            x[d1][s1][n1] = x1
            x[d2][s2][n2] = x2
    else:
        x[d1][s1][n1] = x1
        x[d2][s2][n2] = x2    
        
    return x, obj_val

def sa_2opt(x, num_days, num_shifts, num_nurses, Xconst, prev_obj_val):
    
    obj_val = 0

    # opt1
    d1 = random.randrange(num_days)
    #d2 = d1
    d2 = random.randrange(num_days)
    s1 = random.randrange(num_shifts)
    s2 = random.randrange(num_shifts)
    n1 = random.randrange(Xconst.assign_in_one_shift_max)
    n2 = random.randrange(Xconst.assign_in_one_shift_max)

    if d1 == d2 and s1 == s2:
        return x, 0
    
    if x[d1][s1][n1] == x[d2][s2][n2]:
        return x, 0
    
    x1 = copy.deepcopy(x[d1][s1][n1])
    x2 = copy.deepcopy(x[d2][s2][n2])

    # opt2
    d3 = random.randrange(num_days)
    #d4 = d3
    d4 = random.randrange(num_days)
    s3 = random.randrange(num_shifts)
    s4 = random.randrange(num_shifts)
    n3 = random.randrange(Xconst.assign_in_one_shift_max)
    n4 = random.randrange(Xconst.assign_in_one_shift_max)

    if d3 == d4 and s3 == s4:
        return x, 0
    
    if x[d3][s3][n3] == x[d4][s4][n4]:
        return x, 0
    
    x3 = copy.deepcopy(x[d3][s3][n3])
    x4 = copy.deepcopy(x[d4][s4][n4])
    
    #print(d1,s1,n1, ' ', d2, s2, n2, '  / ', x1, x2)
    
    x[d1][s1][n1] = x2
    x[d2][s2][n2] = x1
    x[d3][s3][n3] = x4
    x[d4][s4][n4] = x3    
    
    if check_constraint(x, num_days, num_shifts, num_nurses, Xconst, ascend=True):
        obj_val = objective_function(x, num_days, num_shifts, num_nurses, Xconst)
        #print('obj_val', obj_val)
        if prev_obj_val < obj_val:
            print('new solution update obj_val', obj_val)
        else:
            x[d1][s1][n1] = x1
            x[d2][s2][n2] = x2
            x[d3][s3][n3] = x3
            x[d4][s4][n4] = x4            
    else:
        x[d1][s1][n1] = x1
        x[d2][s2][n2] = x2
        x[d3][s3][n3] = x3
        x[d4][s4][n4] = x4            
        
    return x, obj_val

def sa_3opt(x, num_days, num_shifts, num_nurses, Xconst, prev_obj_val):
    
    obj_val = 0

    # opt1
    d1 = random.randrange(num_days)
    d2 = random.randrange(num_days)
    d3 = random.randrange(num_days)
    s1 = random.randrange(num_shifts)
    s2 = random.randrange(num_shifts)
    s3 = random.randrange(num_shifts)
    n1 = random.randrange(Xconst.assign_in_one_shift_max)
    n2 = random.randrange(Xconst.assign_in_one_shift_max)
    n3 = random.randrange(Xconst.assign_in_one_shift_max)

    if d1 == d2 and s1 == s2:
        return x, 0
    
    if x[d1][s1][n1] == x[d2][s2][n2]:
        return x, 0
    
    x1 = copy.deepcopy(x[d1][s1][n1])
    x2 = copy.deepcopy(x[d2][s2][n2])

    # opt2
    d3 = random.randrange(num_days)
    #d4 = d3
    d4 = random.randrange(num_days)
    s3 = random.randrange(num_shifts)
    s4 = random.randrange(num_shifts)
    n3 = random.randrange(Xconst.assign_in_one_shift_max)
    n4 = random.randrange(Xconst.assign_in_one_shift_max)

    if d3 == d4 and s3 == s4:
        return x, 0
    
    if x[d3][s3][n3] == x[d4][s4][n4]:
        return x, 0
    
    x3 = copy.deepcopy(x[d3][s3][n3])
    x4 = copy.deepcopy(x[d4][s4][n4])
    
    #print(d1,s1,n1, ' ', d2, s2, n2, '  / ', x1, x2)
    
    x[d1][s1][n1] = x2
    x[d2][s2][n2] = x1
    x[d3][s3][n3] = x4
    x[d4][s4][n4] = x3    
    
    if check_constraint(x, num_days, num_shifts, num_nurses, Xconst, ascend=True):
        obj_val = objective_function(x, num_days, num_shifts, num_nurses, Xconst)
        #print('obj_val', obj_val)
        if prev_obj_val < obj_val:
            print('new solution update obj_val', obj_val)
        else:
            x[d1][s1][n1] = x1
            x[d2][s2][n2] = x2
            x[d3][s3][n3] = x3
            x[d4][s4][n4] = x4            
    else:
        x[d1][s1][n1] = x1
        x[d2][s2][n2] = x2
        x[d3][s3][n3] = x3
        x[d4][s4][n4] = x4            
        
    return x, obj_val

    
def sa_1opt_nerselist(x, num_days, num_shifts, num_nurses, Xconst, prev_obj_val):
    
    obj_val = 0
    d1 = random.randrange(num_days)
    s1 = random.randrange(num_shifts)
    n1 = random.randrange(Xconst.assign_in_one_shift_max)
    
    nurse2 = random.randrange(num_nurses)
    
    if x[d1][s1][n1] == nurse2:
        return x, 0
    
    x1 = copy.deepcopy(x[d1][s1][n1])
    
    #print(d1,s1,n1, ' ', '  / ', x1, nurse2)
    
    x[d1][s1][n1] = nurse2
    
    if check_constraint(x, num_days, num_shifts, num_nurses, Xconst, ascend=True):
        obj_val = objective_function(x, num_days, num_shifts, num_nurses, Xconst)
        #print('obj_val', obj_val)
        if prev_obj_val < obj_val:
            print('new solution update obj_val', obj_val)
        else:
            x[d1][s1][n1] = x1
            
    else:
        x[d1][s1][n1] = x1
        
    return x, obj_val

def sa_2opt_nerselist(x, num_days, num_shifts, num_nurses, Xconst, prev_obj_val):
    
    obj_val = 0
    d1 = random.randrange(num_days)
    s1 = random.randrange(num_shifts)
    n1 = random.randrange(Xconst.assign_in_one_shift_max)
    nurse1 = random.randrange(num_nurses)
    
    d2 = random.randrange(num_days)
    s2 = random.randrange(num_shifts)
    n2 = random.randrange(Xconst.assign_in_one_shift_max)
    nurse2 = random.randrange(num_nurses)   
    
    if x[d1][s1][n1] == nurse1:
        return x, 0
    
    if x[d2][s2][n2] == nurse2:
        return x, 0
    
    x1 = copy.deepcopy(x[d1][s1][n1])
    x2 = copy.deepcopy(x[d2][s2][n2])
    
    #print(d1,s1,n1, ' ', '  / ', x1, nurse2)
    
    x[d1][s1][n1] = nurse1
    x[d2][s2][n2] = nurse2
    
    if check_constraint(x, num_days, num_shifts, num_nurses, Xconst, ascend=True):
        obj_val = objective_function(x, num_days, num_shifts, num_nurses, Xconst)
        #print('obj_val', obj_val)
        if prev_obj_val < obj_val:
            print('new solution update obj_val', obj_val)
        else:
            x[d1][s1][n1] = x1
            x[d2][s2][n2] = x2
    else:
        x[d1][s1][n1] = x1
        x[d2][s2][n2] = x2
        
    return x, obj_val


def sa_3opt_nerselist(x, num_days, num_shifts, num_nurses, Xconst, prev_obj_val):
    
    obj_val = 0
    d1 = random.randrange(num_days)
    s1 = random.randrange(num_shifts)
    n1 = random.randrange(Xconst.assign_in_one_shift_max)
    nurse1 = random.randrange(num_nurses)
    
    d2 = random.randrange(num_days)
    s2 = random.randrange(num_shifts)
    n2 = random.randrange(Xconst.assign_in_one_shift_max)
    nurse2 = random.randrange(num_nurses)   

    d3 = random.randrange(num_days)
    s3 = random.randrange(num_shifts)
    n3 = random.randrange(Xconst.assign_in_one_shift_max)
    nurse3 = random.randrange(num_nurses)  
    
    if x[d1][s1][n1] == nurse1:
        return x, 0
    
    if x[d2][s2][n2] == nurse2:
        return x, 0
    
    if x[d3][s3][n3] == nurse3:
        return x, 0
    
    x1 = copy.deepcopy(x[d1][s1][n1])
    x2 = copy.deepcopy(x[d2][s2][n2])
    x3 = copy.deepcopy(x[d3][s3][n3])
    
    #print(d1,s1,n1, ' ', '  / ', x1, nurse2)
    
    x[d1][s1][n1] = nurse1
    x[d2][s2][n2] = nurse2
    x[d3][s3][n3] = nurse3
    
    if check_constraint(x, num_days, num_shifts, num_nurses, Xconst, ascend=True):
        obj_val = objective_function(x, num_days, num_shifts, num_nurses, Xconst)
        #print('obj_val', obj_val)
        if prev_obj_val < obj_val:
            print('new solution update obj_val', obj_val)
        else:
            x[d1][s1][n1] = x1
            x[d2][s2][n2] = x2
            x[d3][s3][n3] = x3
    else:
        x[d1][s1][n1] = x1
        x[d2][s2][n2] = x2
        x[d3][s3][n3] = x2
        
    return x, obj_val


def local_searchSA(x, 
                 num_days,
                 num_shifts,
                 num_nurses,
                 Xconst,
                 search_loops = 10000):
    
    # 乱数初期化
    random.seed(10)
    
    prev_obj_val = objective_function(x, num_days, num_shifts, num_nurses, Xconst)
    print('local searchSA start obj_val', prev_obj_val )    
    
    for i in range(search_loops):
        
        x, obj_val = sa_1opt(x, num_days, num_shifts, num_nurses, Xconst, prev_obj_val)
        if prev_obj_val < obj_val:
            prev_obj_val = obj_val
            
        x, obj_val = sa_1opt_nerselist(x, num_days, num_shifts, num_nurses, Xconst, prev_obj_val)
        if prev_obj_val < obj_val:
            prev_obj_val = obj_val       
         
        x, obj_val = sa_2opt(x, num_days, num_shifts, num_nurses, Xconst, prev_obj_val)
        if prev_obj_val < obj_val:
            prev_obj_val = obj_val
            
        x, obj_val = sa_2opt_nerselist(x, num_days, num_shifts, num_nurses, Xconst, prev_obj_val)
        if prev_obj_val < obj_val:
            prev_obj_val = obj_val   

        x, obj_val = sa_3opt_nerselist(x, num_days, num_shifts, num_nurses, Xconst, prev_obj_val)
        if prev_obj_val < obj_val:
            prev_obj_val = obj_val        
    
    obj_val = objective_function(x, num_days, num_shifts, num_nurses, Xconst)
    print('local searchSA exit obj_val', obj_val )    
    
    return x
    
    
    
        
        
