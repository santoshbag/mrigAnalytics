# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 15:53:34 2018

@author: Santosh Bag
"""

import xlwings as xw
import pandas as pd
import QuantLib as ql

objectmap = {}

@xw.func
def double_sum(x, y):
    """Returns twice the sum of the two arguments"""
    print("double_sum called")
    cnt = 0
    for keys in objectmap:
        cnt = cnt +1
    return cnt

@xw.func
@xw.arg('x', pd.DataFrame, index=True, header=True)
@xw.ret(index=True, header=True,expand='table')
def CORREL2(x):
    """Like CORREL, but as array formula for more than 2 data sets"""
    return x.corr()

@xw.func
@xw.arg('yielddata', dict)
def setYieldCurve(yielddata):
    localmap = {'30/360': ql.Thirty360(),
                'TARGET' : ql.TARGET(),
                 'Compounded' : ql.Compounded,
                 'Annual' : ql.Annual}
    objid = 'YC'
    for key in yielddata:
        objid = objid + "|" + str(yielddata[key]) 
    
    yc = ql.FlatForward(ql.Date(4,6,2018),yielddata['Flat Rate'],localmap[yielddata['Day Count']])
    ych = ql.YieldTermStructureHandle(yc) 
    objectmap[objid] = ych
    return objid

@xw.func
@xw.arg('bonddata', dict)
def makeBond(bonddata):
    localmap = {'30/360': ql.Thirty360(),
                'TARGET' : ql.TARGET(),
                 'Compounded' : ql.Compounded,
                 'Annual' : ql.Annual,
                 'Semiannual' : ql.Semiannual,
                 'Unadjusted' : ql.Unadjusted,
                 'Backward' : ql.DateGeneration.Backward}
    objid = 'Bond'
    for key in bonddata:
        objid = objid + "|" + str(bonddata[key]) 
    print(objid)
    issuedate = bonddata['Issue']
    issuedate = ql.Date(issuedate.day,issuedate.month,issuedate.year)
    print("santosh---")
    print(issuedate)
    maturitydate = bonddata['Maturity']
    maturitydate = ql.Date(maturitydate.day,maturitydate.month,maturitydate.year)
    print(maturitydate)
    bondschedule = ql.Schedule(issuedate,
                               maturitydate,
                               ql.Period(localmap[bonddata['tenor']]),
                               localmap[bonddata['Calendar']],
                               localmap[bonddata['Convention']],
                               localmap[bonddata['Convention']],
                               localmap[bonddata['Date Generation']],
                               False)
    bond = ql.FixedRateBond(int(bonddata['settlementdays']),
                            bonddata['face'],
                            bondschedule,
                            [bonddata['coupon']],
                            localmap[bonddata['Day Count']])
    
    objectmap[objid] = bond
    return objid

@xw.func
def setPricing(bondHandle, curvehandle):
    bond = objectmap[bondHandle]
    curve = objectmap[curvehandle]
    
    bondengine = ql.DiscountingBondEngine(curve)
    bond.setPricingEngine(bondengine)
    return True

@xw.func
def bondAnalytics(bondHandle):
    bond = objectmap[bondHandle]
    
    return bond.NPV()

if __name__ == '__main__':
    print("santosh---")
    print(objectmap)
    xw.serve()
    
    