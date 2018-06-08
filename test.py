# -*- coding: utf-8 -*-
"""
Created on Wed May 23 19:31:48 2018

@author: Santosh Bag
"""
import sys
sys.path.append('F:\\Mrig Analytics\\Development\\mrigAnalytics\\instruments')

from instruments import termstructure as ir
from instruments import bonds as bo
from instruments import index as i
from instruments import qlMaps as qm
import QuantLib as ql
from datetime import date


dt = date(2018,6,7)
#ql.Settings.instance().evaluationDate = ql.Date(8,6,2018)

spread = 0.01
mat = date(2018,11,30)
#shift = [[dt,mat],[spread,spread+.005]]
yc = ir.SpotZeroYieldCurve('INR',dt)
#yc = ir.Flat1ForwardYieldCurve(dt,0.002)
#yc.setupCurve({'day_count': ql.Actual360(),
#          'calendar': ql.India()})

fc = ql.RelinkableYieldTermStructureHandle()
#fc.linkTo(yc.flat_ts)

libor = i.Libor('Libor',
                '3M',
                3,
                'INR',
                'India',
                '30-360',
                yc.getCurveHandle())
libor.index.addFixing(ql.Date(4,4,2018),0.002)
index = ql.Euribor6M(fc)
index.addFixing(ql.Date(6,6,2018), 0.002)


params = {'issue_date':date(2018,4,7),
          'maturity_date' : date(2020,8,15), 
          'coupon_frequency': 2, 
          'day_count': ql.Thirty360(),
          'calendar': ql.India(),
          'business_convention': ql.Unadjusted,
          'settlement_days' : 3, 
          'facevalue':100, 
          'month_end' : False,
          'date_generation' : ql.DateGeneration.Backward,
          'coupon_index':libor.getIndex(),
          'coupon_rates' : spread,
          'inArrears' : False}


#yc.getShiftedCurve(shift)
#sc = yc.getShiftedCurveHandle()

frb = bo.FixedRateBond(params)

frb.valuation(yc.getCurveHandle())

cfs = frb.bondobject.cashflows()
print(frb.bondobject.NPV())
for cf in cfs:
    print("%s  %s" %(cf.date(),cf.amount()))