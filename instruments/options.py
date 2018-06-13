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
        self.is_valued = False
        #self.business_convention = setupparams['business_convention']
        #self.settlement_days = setupparams['settlement_days']
        #self.facevalue = setupparams['facevalue']
        #self.month_end = setupparams['month_end']
        
        
class VanillaEuropeanOption(Option):
    def __init__(self,setupparams):
        Option.__init__(self,setupparams)
        self.strike = setupparams['strike']
        self.type = setupparams['option_type']
        self.option_name = self.underlying_name+" "+str(self.type)  +" Option "+self.maturity_date.strftime('%d-%m-%Y')
        payoff = ql.PlainVanillaPayoff(self.type,
                                       self.strike)
        exercise = ql.EuropeanExercise(qlMaps.qlDates(self.maturity_date))
        self.vanilla_european_option = ql.VanillaOption(payoff,exercise)
        
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
        
        self.vanilla_european_option.setPricingEngine(optionEngine)
        self.is_valued = True
        
    def getAnalytics(self):
        if self.is_valued:
            value = {'NPV':self.vanilla_european_option.NPV(),
                     'delta' : self.vanilla_european_option.delta(),
                     'gamma' : self.vanilla_european_option.gamma(),
                     'theta' : self.vanilla_european_option.theta()}
            try:
                value.update({'theta_per_day' : self.vanilla_european_option.thetaPerDay()})
            except:
                pass
            try:
                value.update({'rho' : self.vanilla_european_option.rho()})
            except:
                pass
            try:
                value.update({'vega' : self.vanilla_european_option.vega()})
            except:
                pass
            try:
                value.update({'strike_sensitivity' : self.vanilla_european_option.strikeSensitivity()})
            except:
                pass
            try:
                value.update({'dividendRho' : self.vanilla_european_option.dividendRho()})
            except:
                pass
        else:
            value = {"Status ":"Option not evaluated"}
        return value