# -*- coding: utf-8 -*-
"""
Created on Thu May 31 15:11:09 2018

@author: Santosh Bag
"""


import QuantLib as ql
from portfolio import Product

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
        self.type = [setupparams['type']]
        self.option_name = self.underlying_name+" "+self.type+" Option "+self.maturity_date.strftime('%d-%m-%Y')
        payoff = ql.PlainVanillaPayoff(Option.option_type[self.type],
                                       self.strike)
        exercise = ql.EuropeanExercise(ql.Date(self.maturity_date.day,
                                               self.maturity_date.month,
                                               self.maturity_date.year))
        self.vanilla_european_option = ql.VanillaOption(payoff,exercise)
        
    def valuation(self,
                  underlying_spot,
                  yieldcurvehandle,
                  volcurvehandle,
                  dividendcurvehandle,
                  method='BSM',
                  steps=100):
        underlying_quote = ql.SimpleQuote(underlying_spot)
        underlying_quote_handle = ql.QuoteHandle(underlying_quote)
        bsm_process = ql.BlackScholesMertonProcess(underlying_quote_handle,
                                                       dividendcurvehandle,
                                                       yieldcurvehandle,
                                                       volcurvehandle)
        if method == 'BSM':
            optionEngine = ql.AnalyticEuropeanEngine(bsm_process)
        else:
            optionEngine = ql.BinomialVanillaEngine(bsm_process,'crr',steps)
        
        self.vanilla_european_option.setPricingEngine(optionEngine)
        self.is_valued = True
        
    def getValue(self):
        if self.is_valued:
            value = {'NPV':self.vanilla_european_option.NPV(),
                     'delta' : self.vanilla_european_option.delta(),
                     'gamma' : self.vanilla_european_option.gamma(),
                     'theta' : self.vanilla_european_option.theta(),
                     'theta_per_day' : self.vanilla_european_option.thetaPerDay(),
                     'rho' : self.vanilla_european_option.rho(),
                     'vega' : self.vanilla_european_option.vega(),
                     'strike_sensitivity' : self.vanilla_european_option.strikeSensitivity(),
                     'dividendRho' : self.vanilla_european_option.dividendRho()}
        else:
            value = "Bond not evaluated"
        return value