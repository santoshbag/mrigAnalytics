# -*- coding: utf-8 -*-
"""
Created on Thu May 31 15:11:09 2018

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import QuantLib as ql
from portfolio.portfolio import Product
import instruments.qlMaps as qlMaps
import datetime

today = datetime.date.today()
class Option(Product):
    
    option_type = {'Call':ql.Option.Call,
                   'Put' :ql.Option.Put}

    def __init__(self,setupparams,name='XYZ'):
        Product.__init__(self,'Option')
        self.underlying_name = name
        self.security_type = "Option"
        #self.issue_date = setupparams['issue_date']
        self.maturity_date = setupparams['maturity_date']
        self.day_count = setupparams['day_count']
        self.calendar = setupparams['calendar']
        self.process = None
        self.optionobject = None
        self.valuation_params = {}
        self.is_valued = False
        #self.business_convention = setupparams['business_convention']
        #self.settlement_days = setupparams['settlement_days']
        #self.facevalue = setupparams['facevalue']
        #self.month_end = setupparams['month_end']
        Product.productMetadataSet = setupparams
        ql.Settings.instance().evaluationDate = ql.Date(today.day,today.month,today.year)
            
    def getAnalytics(self):
        # print(ql.Settings.instance().evaluationDate)
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
            
            Product.resultSet = value
            Product.value = self.optionobject.NPV()
        else:
            value = {"Status ":"Option not evaluated"}
        return value    
        
class VanillaEuropeanOption(Option):
    def __init__(self,setupparams):
        Option.__init__(self,setupparams)
        self.strike = setupparams['strike']
        self.type = setupparams['option_type']
        self.option_name = self.underlying_name+" "+str(self.type)  +" Option "+self.maturity_date.strftime('%d-%m-%Y')
        payoff = ql.PlainVanillaPayoff(self.type,self.strike)
        exercise = ql.EuropeanExercise(qlMaps.qlDates(self.maturity_date))
        self.optionobject = ql.VanillaOption(payoff,exercise)
        Product.productMetadataSet = setupparams
             
    def valuation(self,
                  underlying_spot,
                  yieldcurve,
                  volcurve,
                  dividendcurve,
                  method='Black Scholes',
                  steps=100,
                  eval_date=today):

        ql.Settings.instance().evaluationDate = ql.Date(eval_date.day, eval_date.month, eval_date.year)
        # referenceDate = yieldcurve.spotCurve.referenceDate()
        # if ql.Date(eval_date.day,eval_date.month,eval_date.year) - referenceDate > 0:
        #     imp_yieldCurve = ql.ImpliedTermStructure(yieldcurve.getCurveHandle(),ql.Date(eval_date.day,eval_date.month,eval_date.year))
        #     # imp_volCurve = ql.ImpliedTermStructure(volcurve.getCurveHandle(),ql.Date(eval_date.day,eval_date.month,eval_date.year))
        #     imp_dividendcurve = ql.ImpliedTermStructure(dividendcurve.getCurveHandle(),ql.Date(eval_date.day, eval_date.month, eval_date.year))
        #
        #     print(imp_yieldCurve.referenceDate())
        # else:
        #     imp_yieldCurve = yieldcurve.spotCurve
        #     # imp_volCurve = volcurve.vol_ts
        #     imp_dividendcurve = dividendcurve.flat_ts
        # print(yieldcurve.spotCurve.referenceDate())
        underlying_quote = ql.SimpleQuote(underlying_spot)
        underlying_quote_handle = ql.QuoteHandle(underlying_quote)
        bsm_process = ql.BlackScholesMertonProcess(underlying_quote_handle,
                                                       dividendcurve.getCurveHandle(),
                                                       yieldcurve.getCurveHandle(),
                                                       volcurve.getCurveHandle())
        self.process = bsm_process
        if method == 'Black Scholes':
            optionEngine = ql.AnalyticEuropeanEngine(bsm_process)
        else:
            optionEngine = ql.BinomialVanillaEngine(bsm_process,'crr',steps)
        
        self.optionobject.setPricingEngine(optionEngine)
        self.is_valued = True

    def getImpliedVol(self,price):
        iv = None
        if self.is_valued:
            iv = self.optionobject.impliedVolatility(price,self.process)
            
        return iv

       
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
        Product.productMetadataSet = setupparams
             
    def valuation(self,
                  underlying_spot,
                  yieldcurve,
                  volcurve,
                  dividendcurve,
                  method='Binomial',
                  steps=100,
                  eval_date=today):

        ql.Settings.instance().evaluationDate = ql.Date(eval_date.day,eval_date.month,eval_date.year)
        
        underlying_quote = ql.SimpleQuote(underlying_spot)
        underlying_quote_handle = ql.QuoteHandle(underlying_quote)
        bsm_process = ql.BlackScholesMertonProcess(underlying_quote_handle,
                                                       dividendcurve.getCurveHandle(),
                                                       yieldcurve.getCurveHandle(),
                                                       volcurve.getCurveHandle())
        self.process = bsm_process
        optionEngine = ql.BinomialVanillaEngine(bsm_process,'crr',steps)
        
        self.optionobject.setPricingEngine(optionEngine)
        self.is_valued = True
   