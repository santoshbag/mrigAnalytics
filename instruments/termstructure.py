# -*- coding: utf-8 -*-
"""
Created on Mon May 28 15:35:35 2018

@author: Santosh Bag
"""


import QuantLib as ql
import mrigutilities
import pandas as pd

class TermStructure:
    """
    Term Structure class is a generic parent class for Interest Rate Curve,
    Dividend Yield Curve, Volatility Curve and Credit Spread Curves.
    """    
    def __init__(self,reference_date):
        self.reference_date = reference_date
        
class YieldCurveTermStructure(TermStructure):
    """
    The YieldCurveTermStructure class is the most fundamental class. It signifies the business 
    idea of the Yield Curve. This class will encapsulate the rates data and will have
    methods to calculate the Discount Factors, Forward Curve etc. 
    """
    def __init__(self,reference_date):
        self.reference_date = reference_date
    
    
class SpotZeroYieldCurve(YieldCurveTermStructure):
    """
    The SpotZeroYieldCurve class represents the yield curve generated from spot zero 
    rates.
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
        ql.Settings.instance().evaluationDate = ql.Date(self.reference_date.day,
                                                        self.reference_date.month,
                                                        self.reference_date.year)
        #print(self.spot_rates)
        self.spotCurve = ql.ZeroCurve(self.spot_rates[0],
                                 self.spot_rates[1],
                                 self.day_count,
                                 self.calendar,
                                 self.interpolation,
                                 self.compounding,
                                 self.compounding_frequency)
        
    def setupCurve(self,setupparams):
        try:
            self.spot_rates = setupparams['spot_rates'] #List, a 2D array of dates and spot rates
        except:
            pass
        self.compounding = setupparams['compounding']
        self.compounding_frequency = setupparams['compounding_frequency']
        self.day_count = setupparams['day_count']
        self.calendar = setupparams['calendar']
        self.interpolation = setupparams['interpolation']
        
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

    def __setDBRates(self):
        sql = "select curvedate, tenor, yield from yieldcurve where curve = '"+self.currency+"' and curvedate='"+ self.reference_date.strftime('%Y-%m-%d')+"'"
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
        
    def getCurve(self):
        
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
    
    def getCurveHandle(self):
        
        spotCurve = self.getCurve()
        spotCurveHandle = ql.YieldTermStructureHandle(spotCurve)
        
        return spotCurveHandle    
    
    def getShiftedCurve(self,date_spread_vector):
        """
        This function shifts the spot curve based on the spread
        For parallel shifts to yield curve, the date_spread_vector is just the spread
        
        For non-parallel shifts, the date_spread_vector is a 2D array of dates and spreads
        """
        
        #Check if the shift is parallel or non-parallel
        parallel = True
        if len(date_spread_vector) > 1:
            parallel = False
        
        spotCurveHandle = self.getSpotCurveHandle()
        if parallel:
            spread_quote = ql.SimpleQuote(date_spread_vector[0])
            spread_handle = ql.QuoteHandle(spread_quote)
            
            self.shiftedCurve = ql.ZeroSpreadedTermStructure(spotCurveHandle,spread_handle)
        else:
            spread_handles = [ql.QuoteHandle(ql.SimpleQuote(s)) for s in date_spread_vector[1]]
            dateList = [ql.Date(dt.day,dt.month,dt.year) for dt in date_spread_vector[0]]
            self.shiftedCurve = ql.SpreadedLinearZeroInterpolatedTermStructure(spotCurveHandle,
                                                                          spread_handles,
                                                                          dateList)
        return self.shiftedCurve
    
    def getShiftedCurveHandle(self):
        
        shiftedCurveHandle = ql.YieldTermStructureHandle(self.shiftedCurve)
        
        return shiftedCurveHandle    


class Volatilty(TermStructure):
    """
    Volatility Class to encapsulate volatilty term structure, volatility surface
    """
    
    def __init__(self,reference_date,setupparams):
        self.reference_date = reference_date     #Date for which the rates are applicable
        self.day_count = ql.Thirty360()
        self.calendar = ql.India()
        self.interpolation = ql.Linear()

    def setupCurve(self,setupparams):
        self.spot_vols = setupparams['spot_vols'] #List, a 2D array of dates and spot rates
        self.day_count = setupparams['day_count']
        self.calendar = setupparams['calendar']
        self.interpolation = setupparams['interpolation']     
    
    def getConstantVol(self,vol_quote):
        vol_ts = ql.BlackConstantVol(self.reference_date,
                                     self.calendar,
                                     vol_quote,
                                     self.day_count)
        vol_ts_handle = ql.BlackVolTermStructureHandle(vol_ts)
        
        return vol_ts_handle

class FlatForwardYieldCurve(YieldCurveTermStructure):
    """
    Flat Forward Yield class to generate constant yield term structure
    """
    
    def __init__(self,reference_date,flat_rate):
        self.reference_date = reference_date     #Date for which the rates are applicable
        self.flat_rate= flat_rate
        self.day_count = ql.Thirty360()
        self.calendar = ql.India()
        self.interpolation = ql.Linear()

    def setupCurve(self,setupparams):
        self.day_count = setupparams['day_count']
        self.calendar = setupparams['calendar']
        self.flat_ts = ql.FlatForward(ql.Date(self.reference_date.day,
                                              self.reference_date.month,
                                              self.reference_date.year),
                                              self.flat_rate,
                                              self.day_count,
                                              ql.Compounded,
                                              ql.Semiannual)
        self.flat_ts_handle = ql.YieldTermStructureHandle(self.flat_ts)
        
    def getCurve(self):
        return self.flat_ts
    
    def getCurveHandle(self):
        return self.flat_ts_handle