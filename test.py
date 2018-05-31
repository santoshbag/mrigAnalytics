# -*- coding: utf-8 -*-
"""
Created on Wed May 23 19:31:48 2018

@author: Santosh Bag
"""
import sys
sys.path.append('F:\\Mrig Analytics\\Development\\mrigAnalytics\\instruments')

from instruments import interest_rates as ir
from instruments import bonds as bo
import QuantLib as ql
from datetime import date


dt = date(2018,5,30)
spread = 0.01
mat = date(2018,11,30)
shift = [[dt,mat],[spread,spread+.005]]
yc = ir.InterestRates('INR',dt)

params = {'issue_date':date(2017,5,18),
          'maturity_date' : date(2018,11,30), 
          'coupon_frequency': 1, 
          'day_count': ql.Thirty360(),
          'calendar': ql.India(),
          'business_convention': ql.Unadjusted,
          'settlement_days' : 0, 
          'facevalue':100, 
          'month_end' : True,
          'couponrate':0.10}

yc.getShiftedCurve(shift)
sc = yc.getShiftedCurveHandle()

frb = bo.FixedRateBond(params)

frb.valuation(sc)

val = frb.getValue()





