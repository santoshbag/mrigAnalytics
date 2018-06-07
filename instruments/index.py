# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 17:49:16 2018

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import QuantLib as ql
import instruments.qlMaps as qlMaps

class Index:
    """
    This class is the base class for Indices like Libor, Euribor others.
    """
    def __init__(self,name):
        self.name = name
        self.index = None
    
class Libor(Index):
    """
    This is the generic Libor class to represent any interest rate index.
    """
    
    def __init__(self,name,
                 tenor, 
                 settlementDays, 
                 currency,
                 calendar,
                 day_count,
                 yieldcurvehandle):
        
        self.name = name
        self.tenor = qlMaps.period(tenor)
        self.settlementDays = settlementDays
        self.currency = qlMaps.CURRENCY[currency]
        self.calendar = qlMaps.CALENDAR[calendar]
        self.day_count = qlMaps.DAYCOUNT[day_count]
        self.yieldcurvehandle = yieldcurvehandle
        
        self.index = ql.Libor(self.name,
                              self.tenor,
                              self.settlementDays,
                              self.currency,
                              self.calendar,
                              self.day_count,
                              self.yieldcurvehandle)
        
    def getIndex(self):
        return self.index
        
    def getName(self):
        return self.name
        
        