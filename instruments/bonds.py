# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 11:20:48 2016

@author: sbag
"""

import QuantLib as ql
from portfolio import Product

class Bond(Product):
    def __init__(self,name=Bond1,setupparams):
        self.issue_name = name
        self.security_type = "Bond"
        self.issue_date = setupparams['issue_date']
        self.maturity_date = setupparams['maturity_date']
        self.coupon_frequency = setupparams['coupon_frequency']
        self.day_count = setupparams['day_count']
        self.calendar = setupparams['calendar']
        self.business_convention = setupparams['business_convention']
        self.settlement_days = setupparams['settlement_days']
        self.facevalue = setupparams['facevalue']
        self.month_end = setupparams['month_end']
        
    def getSchedule(self):
        issueDate = ql.Date(self.issue_date.day,self.issue_date.month,self.issue_date.year)
        maturityDate = ql.Date(self.maturity_date.day,self.maturity_date.month,self.maturity_date.year)
        tenor = ql.Period(self.coupon_frequency)
        dateGeneration = ql.DateGeneration.Backward
        
        schedule = ql.Schedule(issueDate,
                               maturityDate,
                               tenor,
                               self.calendar,
                               self.business_convention,
                               self.business_convention,
                               dateGeneration,
                               self.month_end)
        return schedule
    
class FixedRateBond(Bond):
    def __init__(self,setupparams):
        Bond.__init__(self,setupparams)
        self.coupon_rates = [setupparams['couponrate']]
        self.fixedratebond = ql.FixedRateBond(self.settlement_days,
                                              self.facevalue,
                                              self.getSchedule(),
                                              self.coupon_rates,
                                              self.day_count)
        
    def valuation(self,spotcurvehandle):
        bondEngine = ql.DiscountingBondEngine(spotcurvehandle)
        self.fixedratebond.setPricingEngine(bondEngine)
        self.is_valued = True
        
    def getValue(self):
        if self.is_valued:
            value = {'NPV':self.fixedratebond.NPV(),
                     'cleanPrice' : self.fixedratebond.cleanPrice(),
                     'dirtyPrice' : self.fixedratebond.dirtyPrice()}
        else:
            value = "Bond not evaluated"
        return value
    
    def getYields(self):
        if self.is_valued:
            value = {'Yield':self.fixedratebond.bondYield()}
        else:
            value = "Bond not evaluated"
        return value
    
    def getSpreads(self):
        if self.is_valued:
            value = {'Spread' : self.fixedratebond.bondYield()}
        else:
            value = "Bond not evaluated"
        return value
    
    def getCashflows(self):
        if self.is_valued:
            value = {'Cash Flows' : self.fixedratebond.cashflows()}
        else:
            value = "Bond not evaluated"
        return value
        
        
        
                                            

        
        
