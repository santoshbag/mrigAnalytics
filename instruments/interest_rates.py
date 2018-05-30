# -*- coding: utf-8 -*-
"""
Created on Mon May 28 15:35:35 2018

@author: Santosh Bag
"""


import QuantLib as ql
import mrigutilities
import pandas as pd

class InterestRates:
    """
    The Interest Rate class is the most fundamental class. It signifies the business 
    idea of the Yield Curve. This class will encapsulate the rates data and will have
    methods to calculate the Discount Factors, Forward Curve etc. 
    """
    
    
    def __init__(self,currency,reference_date):
        self.currency = currency
        self.reference_date = reference_date     #Date for which the rates are applicable
        self.compounding = ql.Compounded
        self.compounding_frequency = ql.Annual
        self.day_count = ql.Thirty360()
        self.calendar = ql.India()
        self.interpolation = ql.Linear()
        #self.spot_rates = ['sd']
        self.__setDBRates()
        
    def setupCurve(self,setupparams):
        self.spot_rates = setupparams['spot_rates'] #List, a 2D array of dates and spot rates
        self.compounding = setupparams['compounding']
        self.compounding_frequency = setupparams['compounding_frequency']
        self.day_count = setupparams['day_count']
        self.calendar = setupparams['calendar']
        self.interpolation = setupparams['interpolation']

    def __setDBRates(self):
        sql = "select curvedate, tenor, yield from yieldcurve where curve = 'INR' and curvedate='"+ self.reference_date.strftime('%Y-%m-%d')+"'"
        engine = mrigutilities.sql_engine()
        
        rates_df = pd.read_sql(sql,engine)
        spot_yields = list(rates_df['yield']/100)
        spot_dates = mrigutilities.get_date_vector([list(rates_df['curvedate']),list(rates_df['tenor'])])
        #print(spot_yields)
        spot_dates.insert(0,ql.Date(self.reference_date.day,
                                    self.reference_date.month,
                                    self.reference_date.year))
        spot_yields.insert(0,0.0)
        self.spot_rates = [spot_dates,spot_yields]        
        
    def getSpotCurve(self):
        
        ql.Settings.instance().evaluationDate = ql.Date(self.reference_date.day,
                                                        self.reference_date.month,
                                                        self.reference_date.year)
        self.spotCurve = ql.ZeroCurve(self.spot_rates[0],
                                 self.spot_rates[1],
                                 self.day_count,
                                 self.calendar,
                                 self.interpolation,
                                 self.compounding,
                                 self.compounding_frequency)
        
        return self.spotCurve
    #0.9846802113323603
    def getForwardRate(self,date1, 
                       date2, 
                       daycount=None, 
                       compounding=None,
                       frequency=None):
        
        if daycount is None:
            daycount=self.day_count
        if compounding is None:
            compounding=self.compounding
        if frequency is None:
            frequency=self.compounding_frequency
        
        forward_rate = self.spotCurve.forwardRate(ql.Date(date1.day,date1.month,date1.year),
                                                  ql.Date(date2.day,date2.month,date2.year),
                                                  daycount,
                                                  compounding,
                                                  frequency)
        return forward_rate.rate()
        
    def getDiscountFactor(self,dates):
        
        discount_factor = [self.spotCurve.discount(ql.Date(date.day,date.month,date.year)) for date in dates]
        return discount_factor
    
    def getSpotCurveHandle(self):
        
        spotCurve = self.getSpotCurve()
        spotCurveHandle = ql.YieldTermStructureHandle(spotCurve)
        
        return spotCurveHandle    