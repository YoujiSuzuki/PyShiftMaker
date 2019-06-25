# -*- coding: utf-8 -*-

import sys
import time
import numpy as np

import logging
logging.basicConfig(filename='WorkShiftOptMIP_log.log', filemode='w', level=logging.DEBUG)
logging._warnings_showwarning


class XConstraint:
    """
    スケジュール制約クラス
     各ナースは1週間に5日以上、6日以下働く制約
     各日のシフトsには2人のナースがアサインされる
     各ナースは、一日に1回しかアサインできない        
     ナースのアサイン可能なシフトの制約
    """
    def __init__(self, num_assign_week_min=None, num_assign_week_max=None, 
                 assign_in_one_shift_max=None, num_assign_of_a_nurse_in_day_max=None, 
                 AssignableShifts=None, NerseCompatibility=None):
        if num_assign_week_min is not None:
            self.num_assign_week_min = num_assign_week_min
        else:
            self.num_assign_week_min = 0
            
        if num_assign_week_max is not None:
            self.num_assign_week_max = num_assign_week_max # list fot Face Type(t)
        else:
            self.num_assign_week_max = 9999
            
        if assign_in_one_shift_max is not None:
            self.assign_in_one_shift_max = assign_in_one_shift_max
        else:
            self.assign_in_one_shift_max = 2
            
        if num_assign_of_a_nurse_in_day_max is not None:
            self.num_assign_of_a_nurse_in_day_max = num_assign_of_a_nurse_in_day_max
        else:
            self.num_assign_of_a_nurse_in_day_max = 3
            
        if AssignableShifts is not None:
            self.AssignableShifts = AssignableShifts
        else:
            self.AssignableShifts = None
            
        if NerseCompatibility is not None:
            self.NerseCompatibility = NerseCompatibility
        else:
            self.NerseCompatibility = None
            
            
    def __str__(self):
        return('num_assign_week_min ' + str(self.num_assign_week_min) + '\n' +
               'num_assign_week_max ' + str(self.num_assign_week_max) + '\n' +
               'assign_in_one_shift_max ' + str(self.assign_in_one_shift_max) + '\n' +
               'num_assign_of_a_nurse_in_day_max ' + str(self.num_assign_of_a_nurse_in_day_max) +  '\n' +
               'AssignableShifts ' + str(self.AssignableShifts) + '\n' +
               'NerseCompatibility ' + str(self.NerseCompatibility)
               )
        
        
