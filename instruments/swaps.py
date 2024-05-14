# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 12:14:49 2018

@author: Santosh Bag
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import QuantLib as ql
import mrigutilities as mu

from portfolios.portfolio import Product

class Swap(Product):
    
    settledate = ql.Settings.instance().evaluationDate
    def __init__(self,setupparams,name='Swap'):
        self.issue_name = name
        self.security_type = "Swap"
        #self.issue_date = setupparams['issue_date']
        self.maturity_date = setupparams['maturity_date']
        self.facevalue = setupparams['facevalue']
        #self.coupon_frequency = setupparams['coupon_frequency']
        #self.day_count = setupparams['day_count']

        #self.settlement_days = setupparams['settlement_days']
        
        #self.month_end = setupparams['month_end']
        
        self.swapobject = None
        self.valuation_params = {}
        self.is_valued = False
        Product.productMetadataSet = setupparams
    
    def getAnalytics(self):
        if self.is_valued:
            npv = self.swapobject.NPV()
            fixedlegNPV = self.swapobject.fixedLegNPV()
            floatinglegNPV = self.swapobject.floatingLegNPV()
            fairSpread = self.swapobject.fairSpread()
            #spread = self.swapobject.Spread()
            fairRate = self.swapobject.fairRate()
            fixedlegBPS = self.swapobject.fixedLegBPS()
            floatinglegBPS = self.swapobject.floatingLegBPS()
            
            fixedlegCashflow = [(mu.python_dates(c.date()),c.amount()) for c in self.swapobject.leg(0)]
            floatinglegCashflow = [(mu.python_dates(c.date()),c.amount()) for c in self.swapobject.leg(1)]
            #cashflowamount = [c.amount() for c in self.swapobject.cashflows()]
            swap_analytics = {'NPV':npv,
                              'Fixed Leg NPV' : fixedlegNPV,
                              'Float Leg NPV' : floatinglegNPV,
                              'Fair Spread' : fairSpread,
                             # 'Spread' : spread,
                              'Fair Rate': fairRate,
                              'Fixed Leg BPS' : fixedlegBPS,
                              'Floating Leg BPS' : floatinglegBPS,
                              'Fixed Leg Cashflows' : fixedlegCashflow,
                              'Floating Leg Cashflows' : floatinglegCashflow}
            Product.resultSet = swap_analytics
            Product.value = npv
        else:
            swap_analytics = {'Swap Status':'Swap not evaluated'}
        return swap_analytics#self.valuation_params.update({"class" : "Convertible"})
    
    def valuation(self,yieldcurve):
        yieldcurvehandle = yieldcurve.getCurveHandle()
        swapEngine = ql.DiscountingSwapEngine(yieldcurvehandle)
        self.swapobject.setPricingEngine(swapEngine)
        self.is_valued = True
        self.valuation_params.update({'yieldcurve':yieldcurve})
    
class VanillaFixedFLoatSwap(Swap):
    def __init__(self,fixedleg_params,floatleg_params):
        Swap.__init__(self,fixedleg_params)
        self.pay_recieve_flag = fixedleg_params['pay_recieve_flag']
#FIXED LEG SETUP
                
        self.fixedleg_date_generation = fixedleg_params['date_generation']
        self.fixedleg_calendar = fixedleg_params['calendar']
        self.fixedleg_business_convention = fixedleg_params['business_convention']
        self.fixedleg_day_count = fixedleg_params['day_count']
        self.fixedleg_coupon_frequency = fixedleg_params['coupon_frequency']
        self.fixedleg_coupon_rates = fixedleg_params['coupon_rates']

#FLOAT LEG SETUP
        self.floatleg_date_generation = floatleg_params['date_generation']
        self.floatleg_calendar = floatleg_params['calendar']
        self.floatleg_business_convention = floatleg_params['business_convention']
        self.floatleg_day_count = floatleg_params['day_count']
        self.floatleg_coupon_frequency = floatleg_params['coupon_frequency']
        self.floatleg_index = floatleg_params['coupon_index']
        self.floatleg_coupon_spread = floatleg_params['coupon_spread']
        self.floatleg_indexfixing = floatleg_params['fixing']
        Product.productMetadataSet = {'fixedleg_params' : fixedleg_params,
                                          'floatleg_params' : floatleg_params}
             
        if self.floatleg_indexfixing != None:
            fixingdate = [self.floatleg_index.fixingDate(ql.Settings.instance().evaluationDate)]
            ql.IndexManager.instance().clearHistory(self.floatleg_index.name())
            self.floatleg_index.addFixings(fixingdate,[self.floatleg_indexfixing])
            #print(fixingdate)
        if self.pay_recieve_flag == "PAY":
            pay_recieve_flag = ql.VanillaSwap.Payer
        else:
            pay_recieve_flag = ql.VanillaSwap.Receiver
            
        self.swapobject = ql.VanillaSwap(pay_recieve_flag,
                                         self.facevalue,
                                         self.getFixedSchedule(),
                                         self.fixedleg_coupon_rates,
                                         self.fixedleg_day_count,
                                         self.getFloatSchedule(),
                                         self.floatleg_index,
                                         self.floatleg_coupon_spread,
                                         self.floatleg_day_count)
        
    def getFixedSchedule(self):
        maturityDate = ql.Date(self.maturity_date.day,self.maturity_date.month,self.maturity_date.year)
        tenor = ql.Period(self.fixedleg_coupon_frequency)
        
        schedule = ql.Schedule(Swap.settledate,
                               maturityDate,
                               tenor,
                               self.fixedleg_calendar,
                               self.fixedleg_business_convention,
                               self.fixedleg_business_convention,
                               self.fixedleg_date_generation,
                               False)
        return schedule

    def getFloatSchedule(self):
        maturityDate = ql.Date(self.maturity_date.day,self.maturity_date.month,self.maturity_date.year)
        tenor = ql.Period(self.floatleg_coupon_frequency)
        
        schedule = ql.Schedule(Swap.settledate,
                               maturityDate,
                               tenor,
                               self.floatleg_calendar,
                               self.floatleg_business_convention,
                               self.floatleg_business_convention,
                               self.floatleg_date_generation,
                               False)
        return schedule