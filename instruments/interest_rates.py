# -*- coding: utf-8 -*-
"""
Created on Mon May 28 15:35:35 2018

@author: Santosh Bag
"""


import QuantLib as ql
from portfolio import Product

class InterestRates:
    """
    The Interest Rate class is the most fundamental class. It signifies the business 
    idea of the Yield Curve. This class will encapsulate the rates data and will have
    methods to calculate the Discount Factors, Forward Curve etc. 
    """
    
    
    def __init__(self,currency,reference_date,setupparams):
        self.currency = currency
        self.reference_date = reference_date     #Date for which the rates are applicable
        self.spot_rates = setupparams['spot_rates'] #List, a 2D array of dates and spot rates
        self.compounding = setupparams['compounding']
        self.compounding_frequency = setupparams['compounding_frequency']
        self.day_count = setupparams['day_count']
        self.calendar = setupparams['calendar']
        self.interpolation = setupparams['interpolation']
        
    def getSpotCurve(self):

        spotCurve = ql.ZeroCurve(self.spot_rates[0],
                                 self.spot_rates[1],
                                 self.day_count,
                                 self.calendar,
                                 self.interpolation,
                                 self.compounding,
                                 self.compounding_frequency)
        
        return spotCurve
    
    def getSpotCurveHandle(self):
        
        spotCurve = self.getSpotCurve()
        spotCurveHandle = ql.YieldTermStructureHandle(spotCurve)
        
        return spotCurveHandle