# -*- coding: utf-8 -*-
"""
Created on Thu May 31 15:11:09 2018

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import QuantLib as ql
from instruments.portfolio import Product
import instruments.qlMaps as qlMaps

class Option(Product):
    
    option_type = {'Call':ql.Option.Call,
                   'Put' :ql.Option.Put}
    
    def __init__(self,setupparams,name='XYZ'):
        self.underlying_name = name
        self.security_type = "Option"
        #self.issue_date = setupparams['issue_date']
        self.maturity_date = setupparams['maturity_date']
        self.day_count = setupparams['day_count']
        self.calendar = setupparams['calendar']
        self.optionobject = None
        self.valuation_params = {}
        self.is_valued = False
        #self.business_convention = setupparams['business_convention']
        #self.settlement_days = setupparams['settlement_days']
        #self.facevalue = setupparams['facevalue']
        #self.month_end = setupparams['month_end']
    

    def getAnalytics(self):
        if self.is_valued:
            value = {'NPV':self.optionobject.NPV(),
                     'delta' : self.optionobject.delta(),
                     'gamma' : self.optionobject.gamma(),
                     'theta' : self.optionobject.theta()}
            try:
                value.update({'theta_per_day' : self.optionobject.thetaPerDay()})
            except:
                pass
            try:
                value.update({'rho' : self.optionobject.rho()})
            except:
                pass
            try:
                value.update({'vega' : self.optionobject.vega()})
            except:
                pass
            try:
                value.update({'strike_sensitivity' : self.optionobject.strikeSensitivity()})
            except:
                pass
            try:
                value.update({'dividendRho' : self.optionobject.dividendRho()})
            except:
                pass
        else:
            value = {"Status ":"Option not evaluated"}
        return value    
        
class VanillaEuropeanOption(Option):
    def __init__(self,setupparams):
        Option.__init__(self,setupparams)
        self.strike = setupparams['strike']
        self.type = setupparams['option_type']
        self.option_name = self.underlying_name+" "+str(self.type)  +" Option "+self.maturity_date.strftime('%d-%m-%Y')
        payoff = ql.PlainVanillaPayoff(self.type,
                                       self.strike)
        exercise = ql.EuropeanExercise(qlMaps.qlDates(self.maturity_date))
        self.optionobject = ql.VanillaOption(payoff,exercise)
        
    def valuation(self,
                  underlying_spot,
                  yieldcurve,
                  volcurve,
                  dividendcurve,
                  method='Black Scholes',
                  steps=100):
        underlying_quote = ql.SimpleQuote(underlying_spot)
        underlying_quote_handle = ql.QuoteHandle(underlying_quote)
        bsm_process = ql.BlackScholesMertonProcess(underlying_quote_handle,
                                                       dividendcurve.getCurveHandle(),
                                                       yieldcurve.getCurveHandle(),
                                                       volcurve.getCurveHandle())
        if method == 'Black Scholes':
            optionEngine = ql.AnalyticEuropeanEngine(bsm_process)
        else:
            optionEngine = ql.BinomialVanillaEngine(bsm_process,'crr',steps)
        
        self.optionobject.setPricingEngine(optionEngine)
        self.is_valued = True
        
class VanillaAmericanOption(Option):
    def __init__(self,setupparams):
        Option.__init__(self,setupparams)
        self.strike = setupparams['strike']
        self.type = setupparams['option_type']
        self.option_name = self.underlying_name+" "+str(self.type)  +" Option "+self.maturity_date.strftime('%d-%m-%Y')
        payoff = ql.PlainVanillaPayoff(self.type,
                                       self.strike)
        
        calc_date = ql.Settings.instance().evaluationDate
        exercise = ql.AmericanExercise(calc_date,qlMaps.qlDates(self.maturity_date))
        self.optionobject = ql.VanillaOption(payoff,exercise)
        
    def valuation(self,
                  underlying_spot,
                  yieldcurve,
                  volcurve,
                  dividendcurve,
                  method='Binomial',
                  steps=100):
        underlying_quote = ql.SimpleQuote(underlying_spot)
        underlying_quote_handle = ql.QuoteHandle(underlying_quote)
        bsm_process = ql.BlackScholesMertonProcess(underlying_quote_handle,
                                                       dividendcurve.getCurveHandle(),
                                                       yieldcurve.getCurveHandle(),
                                                       volcurve.getCurveHandle())
        optionEngine = ql.BinomialVanillaEngine(bsm_process,'crr',steps)
        
        self.optionobject.setPricingEngine(optionEngine)
        self.is_valued = True
   