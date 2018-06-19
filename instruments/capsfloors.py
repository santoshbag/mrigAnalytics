# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 14:52:11 2018

@author: Santosh Bag
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import QuantLib as ql
import mrigutilities as mu
import instruments.qlMaps as qlMaps

from instruments.options import Option

class CapsFloors(Option):
    def __init__(self,setupparams,name='Bond1'):
        Option.__init__(self,setupparams)
        self.security_type = "CapsFloors"
        self.start_date = setupparams['start_date']
        self.maturity_date = setupparams['maturity_date']
        self.coupon_frequency = setupparams['coupon_frequency']
        self.business_convention = setupparams['business_convention']
        self.settlement_days = setupparams['settlement_days']
        self.facevalue = setupparams['facevalue']
        self.month_end = setupparams['month_end']
        self.date_generation = setupparams['date_generation']
        self.cap_or_floor = setupparams['cap_or_floor']
        self.strike = setupparams['strike']
        self.coupon_index = setupparams['coupon_index']
        self.coupon_spread = [setupparams['coupon_spread']]
        self.fixing = setupparams['fixing']
        if self.fixing != None:
            fixingdate = [self.coupon_index.fixingDate(ql.Settings.instance().evaluationDate)]
            ql.IndexManager.instance().clearHistory(self.coupon_index.name())
            self.coupon_index.addFixings(fixingdate,[self.fixing])
        
        ibor_leg = ql.IborLeg([self.facevalue],self.getSchedule(),self.coupon_index)
        if self.cap_or_floor == 'CAP':
            self.optionobject = ql.Cap(ibor_leg,[self.strike])
        if self.cap_or_floor == 'FLOOR':
            self.optionobject = ql.Floor(ibor_leg,[self.strike])
    
        
    def getSchedule(self):
        start_date = ql.Date(self.start_date.day,self.start_date.month,self.start_date.year)
        maturityDate = ql.Date(self.maturity_date.day,self.maturity_date.month,self.maturity_date.year)
        tenor = ql.Period(self.coupon_frequency)
        
        schedule = ql.Schedule(start_date,
                               maturityDate,
                               tenor,
                               self.calendar,
                               self.business_convention,
                               self.business_convention,
                               self.date_generation,
                               self.month_end)
        return schedule

    
    def getAnalytics(self):
        if self.is_valued:
            yieldcurve = self.valuation_params['yieldcurve']
            npv = self.bondobject.NPV()
            cleanprice = self.bondobject.cleanPrice()
            dirtyprice = self.bondobject.dirtyPrice()
            accrued_interest = self.bondobject.accruedAmount()
            YTM = self.bondobject.bondYield(self.day_count,ql.Compounded,self.coupon_frequency)
            YTMObj = ql.InterestRate(YTM,self.day_count,ql.Compounded,self.coupon_frequency)
            zspread = ql.BondFunctions.zSpread(self.bondobject,dirtyprice,yieldcurve.getCurve(),self.day_count,ql.Compounded,self.coupon_frequency)
            modduration = ql.BondFunctions.duration(self.bondobject,YTMObj,ql.Duration.Modified)
            simduration = ql.BondFunctions.duration(self.bondobject,YTMObj,ql.Duration.Simple)
            macduration = ql.BondFunctions.duration(self.bondobject,YTMObj,ql.Duration.Macaulay)
            convexity = ql.BondFunctions.convexity(self.bondobject,YTMObj)
            cashflow = [(mu.python_dates(c.date()),c.amount()) for c in self.bondobject.cashflows()]
            #cashflowamount = [c.amount() for c in self.bondobject.cashflows()]
            bond_analytics = {'NPV':npv,
                              'cleanPrice' : cleanprice,
                              'dirtyPrice' : dirtyprice,
                              'accruedAmount' : accrued_interest,
                              'Yield': YTM,
                              'Spread' : zspread,
                              'Modified Duration' : modduration,
                              'Simple Duration' : simduration,
                              'Macualay Duration' : macduration,
                              'Convexity' : convexity,
                              'cashflows' : cashflow}
        else:
            bond_analytics = {'Bond Status':'Bond not evaluated'}
        return bond_analytics#self.valuation_params.update({"class" : "Convertible"})
    
    def valuation(self,yieldcurve,volcurve):
        yieldcurvehandle = yieldcurve.getCurveHandle()
        volcurvehandle = volcurve.getCurveHandle()
        capfloorEngine = ql.BlackCapFloorEngine(yieldcurvehandle,volcurvehandle)
        self.optionobject.setPricingEngine(capfloorEngine)
        self.is_valued = True
        self.valuation_params.update({'yieldcurve':yieldcurve,
                                      'volcurve':volcurve})