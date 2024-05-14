# -*- coding: utf-8 -*-
"""
Created on Thu May 31 15:11:09 2018

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import QuantLib as ql
from portfolios.portfolio import Product
import instruments.qlMaps as qlMaps
import datetime

today = datetime.date.today()
class Futures(Product):

    def __init__(self,setupparams,name='XYZ'):
        Product.__init__(self,'Futures')
        self.underlying_name = name
        self.security_type = "Futures"
        #self.issue_date = setupparams['issue_date']
        self.maturity_date = setupparams['maturity_date']
        self.day_count = setupparams['day_count']
        self.calendar = setupparams['calendar']
        self.process = None
        self.futuresobject = None
        self.valuation_params = {}
        self.is_valued = False
        self.analytics = {}
        #self.business_convention = setupparams['business_convention']
        #self.settlement_days = setupparams['settlement_days']
        #self.facevalue = setupparams['facevalue']
        #self.month_end = setupparams['month_end']
        Product.productMetadataSet = setupparams
        ql.Settings.instance().evaluationDate = ql.Date(today.day,today.month,today.year)
            
    def getAnalytics(self):
        # print(ql.Settings.instance().evaluationDate)
        if self.is_valued:
            value = self.analytics
        else:
            value = {"Status ":"Not evaluated"}
        return value

    def valuation(self):
        return None
        
class EquityFutures(Futures):
    def __init__(self,setupparams):
        Futures.__init__(self,setupparams)
        self.futures_name = self.underlying_name+" "+" Futures "+self.maturity_date.strftime('%d-%m-%Y')
        # payoff = ql.PlainVanillaPayoff(self.type,self.strike)
        # exercise = ql.EuropeanExercise(qlMaps.qlDates(self.maturity_date))
        # self.optionobject = ql.VanillaOption(payoff,exercise)
        Product.productMetadataSet = setupparams


    def valuation(self,ltp):
        self.is_valued = True
        self.analytics = {'NPV': ltp, 'delta': 1, 'gamma': 0, 'theta': 0, 'theta_per_day': 0,
                     'rho': 0, 'vega': 0, 'strike_sensitivity': 0, 'dividendRho': 0,
                     'volatility': 0}
        return self.analytics


