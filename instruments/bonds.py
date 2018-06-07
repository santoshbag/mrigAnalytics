# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 11:20:48 2016

@author: sbag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import QuantLib as ql

from instruments.portfolio import Product

class Bond(Product):
    def __init__(self,setupparams,name='Bond1'):
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
        self.date_generation = setupparams['date_generation']
        self.bondobject = None
        self.is_valued = False
        
    def getSchedule(self):
        issueDate = ql.Date(self.issue_date.day,self.issue_date.month,self.issue_date.year)
        maturityDate = ql.Date(self.maturity_date.day,self.maturity_date.month,self.maturity_date.year)
        tenor = ql.Period(self.coupon_frequency)
        
        schedule = ql.Schedule(issueDate,
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
            bond_analytics = {'NPV':self.bondobject.NPV(),
                              'cleanPrice' : self.bondobject.cleanPrice(),
                              'dirtyPrice' : self.bondobject.dirtyPrice(),
                              'Yield':self.bondobject.bondYield(),
                              'Spread' : self.bondobject.bondYield(),
                              'Cash Flows' : self.bondobject.cashflows()}
        else:
            bond_analytics = "Bond not evaluated"
        return bond_analytics
    
    def valuation(self,yieldcurvehandle):
        bondEngine = ql.DiscountingBondEngine(yieldcurvehandle)
        self.bondobject.setPricingEngine(bondEngine)
        self.is_valued = True
    
class FixedRateBond(Bond):
    def __init__(self,setupparams):
        Bond.__init__(self,setupparams)
        self.coupon_rates = [setupparams['coupon_rates']]
        self.bondobject = ql.FixedRateBond(self.settlement_days,
                                              self.facevalue,
                                              self.getSchedule(),
                                              self.coupon_rates,
                                              self.day_count)
        
class FloatingRateBond(Bond):
    def __init__(self,setupparams):
        Bond.__init__(self,setupparams)
        self.coupon_index = setupparams['coupon_index']
        self.coupon_spread = [setupparams['coupon_spread']]
        self.inArrears = setupparams['inArrears']
        self.bondobject = ql.FloatingRateBond(self.settlement_days,
                                              self.facevalue,
                                              self.getSchedule(),
                                              self.coupon_index,
                                              self.day_count,
                                              self.business_convention,
                                              spreads=self.coupon_spread,
                                              inArrears=self.inArrears)
            

        
        
        
                                            

        
        
