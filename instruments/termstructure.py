# -*- coding: utf-8 -*-
"""
Created on Mon May 28 15:35:35 2018

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import QuantLib as ql
import mrigutilities
import pandas as pd
import instruments.qlMaps as qlMaps
import datetime

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
        self.curve = None
        self.basecurve = None   #Basecurve is the original curve

    def setShift(self,date_spread_vector):
        """
        This function shifts the spot curve based on the spread
        For parallel shifts to yield curve, the date_spread_vector is just the [spread]
        
        For non-parallel shifts, the date_spread_vector is a 2D array of dates and spreads
        """
        
        #Check if the shift is parallel or non-parallel
        parallel = True
        if len(date_spread_vector) > 1:
            parallel = False
        
        curveHandle = self.getCurveHandle()
        if parallel:
            spread_quote = ql.SimpleQuote(date_spread_vector[0][0])
            spread_handle = ql.QuoteHandle(spread_quote)
            
            self.shiftedCurve = ql.ZeroSpreadedTermStructure(curveHandle,spread_handle)
        else:
            spread_handles = [ql.QuoteHandle(ql.SimpleQuote(s)) for s in date_spread_vector[1]]
            dateList = [ql.Date(dt.day,dt.month,dt.year) for dt in date_spread_vector[0]]
            self.shiftedCurve = ql.SpreadedLinearZeroInterpolatedTermStructure(curveHandle,
                                                                          spread_handles,
                                                                          dateList)
            self.shiftedCurve.enableExtrapolation()
        self.curve = self.shiftedCurve
        return self.shiftedCurve
    
    def getShiftedCurveHandle(self):
        
        shiftedCurveHandle = ql.YieldTermStructureHandle(self.shiftedCurve)
        
        return shiftedCurveHandle    
    
    def getCurve(self):
        
        return self.curve

    def getBaseCurve(self):
        
        return self.basecurve

    def getReferenceDate(self):
        
        return self.reference_date
    
    
    def getCurveHandle(self):
        
        curve = self.getCurve()
        curveHandle = ql.YieldTermStructureHandle(curve)
        
        return curveHandle

###########Curve Anaytics####################

    def getZeroRate(self,date, 
                       daycount=None, 
                       compounding=None,
                       frequency=None):
        
        if daycount is None:
            daycount=self.day_count
        if compounding is None:
            compounding=self.compounding
        if frequency is None:
            frequency=self.compounding_frequency
        
        zero_rate = self.curve.zeroRate(qlMaps.qlDates(date),
                                              daycount,
                                              compounding,
                                              frequency)
        return zero_rate.rate()
        


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
        
        forward_rate = self.curve.forwardRate(qlMaps.qlDates(date1),
                                              qlMaps.qlDates(date2),
                                              daycount,
                                              compounding,
                                              frequency)
        return forward_rate.rate()
        
    def getDiscountFactor(self,dates):
        
        discount_factor = [self.curve.discount(qlMaps.qlDates(date)) for date in dates]
        return discount_factor
    
    
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
        self.curve = self.spotCurve
        self.curve.enableExtrapolation()
        self.basecurve = self.spotCurve
        
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
        self.shiftparameter = setupparams['shiftparameter']
        
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
        self.curve = self.spotCurve
        self.curve.enableExtrapolation()
        self.basecurve = self.spotCurve
        
        if self.shiftparameter != None:
            self.setShift(self.shiftparameter)

    def __setDBRates(self):
        sql = "select (curvedate + (tenor::TEXT)::INTERVAL) as date, yield from yieldcurve where curve = '"+self.currency+"' and curvedate='"+ self.reference_date.strftime('%Y-%m-%d')+"'"
        engine = mrigutilities.sql_engine()
        
        rates_df = pd.read_sql(sql,engine)
        rates_df['date'] = pd.to_datetime(rates_df['date'],format='%Y-%m-%d').apply(lambda x: x.date())
        rates_df = rates_df.sort_values(by='date')
#        print(rates_df)
        spot_yields = list(rates_df['yield']/100)
        spot_dates = list(rates_df['date'])
        spot_dates = [ql.Date(dt.day,dt.month,dt.year) for dt in spot_dates]
#        spot_dates = mrigutilities.get_date_vector([list(rates_df['curvedate']),list(rates_df['tenor'])])
#        print(spot_dates)
        spot_dates.insert(0,ql.Date(self.reference_date.day,
                                    self.reference_date.month,
                                    self.reference_date.year))
        spot_yields.insert(0,0.0)
        self.spot_rates = [spot_dates,spot_yields]        
        
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
        
        forward_rate = self.curve.forwardRate(ql.Date(date1.day,date1.month,date1.year),
                                                  ql.Date(date2.day,date2.month,date2.year),
                                                  daycount,
                                                  compounding,
                                                  frequency)
        return forward_rate.rate()
        
    def getDiscountFactor(self,dates):
        
        discount_factor = [self.curve.discount(ql.Date(date.day,date.month,date.year)) for date in dates]
        return discount_factor
    
    def getSpotCurve(self):
        
        return self.spotCurve
    
    def getSpotCurveHandle(self):
        
        spotCurveHandle = ql.YieldTermStructureHandle(self.spotCurve)
        return spotCurveHandle
    
    # def getForwardCurve(self,forwardDate):
    #     start = self.curve.getReferenceDate()
    #     period = (forwardDate - start).days
    #     forwardstart = start + datetime.timedelta(days=period)
    #     dates = [start + datetime.timedelta(days=period * i) for i in range(1, 80)]
    #     tenors = [datetime.timedelta(days=period * i) / datetime.timedelta(days=360) for i in range(1, 80)]
    #     discounts = self.curve.getDiscountFactor(dates)
    #     # baseforwards = [basecurve.getForwardRate(start,start+datetime.timedelta(days=180*i)) for i in range(0,20)]
    #     forwards = [self.curve.getForwardRate(forwardstart, forwardstart + datetime.timedelta(days=period * i)) for i in
    #                 range(1, 80)]
    #     forwardCurve = ql.ForwardCurve(dates,forwards,)
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
        ql.Settings.instance().evaluationDate = qlMaps.qlDates(reference_date)

    def setupCurve(self,setupparams):
        self.day_count = setupparams['day_count']
        self.calendar = setupparams['calendar']
        self.compounding = setupparams['compounding']
        self.compounding_frequency = setupparams['compounding_frequency']
        self.shiftparameter = setupparams['shiftparameter']
        print(setupparams)
        self.flat_ts = ql.FlatForward(qlMaps.qlDates(self.reference_date),
                                              ql.QuoteHandle(ql.SimpleQuote(self.flat_rate)),
                                              self.day_count,
                                              self.compounding,
                                              self.compounding_frequency)
        
        self.curve = self.flat_ts
        self.curve.enableExtrapolation()
        
        if self.shiftparameter != None:
            self.setShift(self.shiftparameter)
        
    def getCurve(self):
        return self.flat_ts
    
    
class FlatDividendYieldCurve(YieldCurveTermStructure):
    """
    Flat Forward Yield class to generate constant yield term structure
    """
    
    def __init__(self,reference_date,flat_rate):
        self.reference_date = reference_date     #Date for which the rates are applicable
        self.flat_rate= flat_rate
        self.day_count = ql.Thirty360()
        self.calendar = ql.India()
        self.interpolation = ql.Linear()
        self.compounding = ql.Compounded
        self.compounding_frequency = ql.Annual
        self.setupCurve(None)

    def setupCurve(self,setupparams):
        # self.day_count = setupparams['day_count']
        # self.calendar = setupparams['calendar']
        # self.compounding = setupparams['compounding']
        # self.compounding_frequency = setupparams['compounding_frequency']
        self.flat_ts = ql.FlatForward(qlMaps.qlDates(self.reference_date),
                                              ql.QuoteHandle(ql.SimpleQuote(self.flat_rate)),
                                              self.day_count,
                                              self.compounding,
                                              self.compounding_frequency)
        self.flat_ts_handle = ql.YieldTermStructureHandle(self.flat_ts)
    
    def getCurve(self):
        return self.flat_ts
    
    def getCurveHandle(self):
        return self.flat_ts_handle
    
    

class Volatilty(TermStructure):
    """
    Volatility Class to encapsulate volatilty term structure, volatility surface
    """
    def __init__(self,reference_date):
        self.reference_date = reference_date     #Date for which the rates are applicable

class FlatVolatilityCurve(Volatilty):
    """
    Flat Vol class to generate constant volatility term structure
    """    
    
    def __init__(self,reference_date,flat_vol):
        self.reference_date = reference_date     #Date for which the rates are applicable
        self.flat_vol= flat_vol
        self.day_count = ql.Thirty360()
        self.calendar = ql.India()
        self.interpolation = ql.Linear()
        self.setupCurve(None)

    def setupCurve(self,setupparams):
        # self.spot_vols = setupparams['spot_vols'] #List, a 2D array of dates and spot rates
        # self.day_count = setupparams['day_count']
        # self.calendar = setupparams['calendar']
        # self.vol_ts = ql.BlackConstantVol(qlMaps.qlDates(self.reference_date),
        #                              self.calendar,
        #                              self.flat_vol,
        #                              self.day_count)
        self.vol_ts = ql.BlackConstantVol(0, self.calendar,ql.QuoteHandle(ql.SimpleQuote(self.flat_vol)), self.day_count)
        self.vol_ts_handle = ql.BlackVolTermStructureHandle(self.vol_ts)
        
    def getCurve(self):
        return self.vol_ts
    
    def getCurveHandle(self):
        return self.vol_ts_handle

class ConstantVolatilityCurve(Volatilty):
    """
    Flat Vol class to generate constant volatility term structure
    """    
    
    def __init__(self,constant_vol):
        self.constant_vol= constant_vol
        self.vol_ts = ql.SimpleQuote(self.constant_vol)
        self.vol_ts_handle = ql.QuoteHandle(self.vol_ts)
        
    def getCurve(self):
        return self.vol_ts
    
    def getCurveHandle(self):
        return self.vol_ts_handle

class CapFloorVolatilitySurface(Volatilty):
    """
    Cap Floor Volatility surface 
    """    
    def __init__(self,setupparams):
        self.strikes = setupparams['strikes']
        self.expiries = setupparams['expiries']
        self.vols = setupparams['vols']
        self.day_count = setupparams['day_count']
        self.calendar = setupparams['calendar']
        self.business_convention = setupparams['business_convention']
        self.settlement_days = setupparams['settlement_days']
        
        expiries = [ql.Period(int(i),ql.Years) for i in self.expiries]
        vols = ql.Matrix(len(self.expiries),len(self.strikes))
        #expiries = [ql.Period(i, ql.Years) for i in range(1,11)] + [ql.Period(12, ql.Years)]
        for i in range(vols.rows()):
            for j in range(vols.columns()):
                vols[i][j] = self.vols[i][j]
        
        self.vol_surface = ql.CapFloorTermVolSurface(self.settlement_days,
                                                     self.calendar,
                                                     self.business_convention,
                                                     expiries,
                                                     self.strikes,
                                                     vols,
                                                     self.day_count)
        self.vol_surface.enableExtrapolation()
        
    def getCurve(self):
        return self.vol_surface
    
    def getVolatility(self,
                      expiry,
                      strike):
        return self.vol_surface.volatility(expiry,strike)
    
    

if __name__ == '__main__':
    print("santosh---")
    refdate = datetime.date(2018,12,28)
    sz = SpotZeroYieldCurve('INR',refdate)
    print(sz.spot_rates)    

