# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 11:20:48 2016

@author: sbag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import QuantLib as ql
import mrigutilities as mu
import instruments.qlMaps as qlMaps

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
        self.valuation_params = {}
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
            yieldcurve = self.valuation_params['yieldcurve']
            npv = self.bondobject.NPV()
            cleanprice = self.bondobject.cleanPrice()
            dirtyprice = self.bondobject.dirtyPrice()
            accrued_interest = self.bondobject.accruedAmount()
            YTM = self.bondobject.bondYield(self.day_count,ql.Compounded,self.coupon_frequency)
            YTMObj = ql.InterestRate(YTM,self.day_count,ql.Compounded,self.coupon_frequency)
            zspread = ql.BondFunctions.zSpread(self.bondobject,dirtyprice,yieldcurve.getCurve(),self.day_count,ql.Compounded,self.coupon_frequency)
            modduration = ql.BondFunctions.duration(self.bondobject,YTMObj,ql.Duration.Modified)
            simduration = ql.BondFunctions.duration(self.bondobject,YTMObj,ql.Duration.Simple)
            macduration = ql.BondFunctions.duration(self.bondobject,YTMObj,ql.Duration.Macaulay)
            convexity = ql.BondFunctions.convexity(self.bondobject,YTMObj)
            cashflow = [(mu.python_dates(c.date()),c.amount()) for c in self.bondobject.cashflows()]
            #cashflowamount = [c.amount() for c in self.bondobject.cashflows()]
            bond_analytics = {'NPV':npv,
                              'cleanPrice' : cleanprice,
                              'dirtyPrice' : dirtyprice,
                              'accruedAmount' : accrued_interest,
                              'Yield': YTM,
                              'Spread' : zspread,
                              'Modified Duration' : modduration,
                              'Simple Duration' : simduration,
                              'Macualay Duration' : macduration,
                              'Convexity' : convexity,
                              'cashflows' : cashflow}
        else:
            bond_analytics = {'Bond Status':'Bond not evaluated'}
        return bond_analytics#self.valuation_params.update({"class" : "Convertible"})
    
    def valuation(self,yieldcurve):
        yieldcurvehandle = yieldcurve.getCurveHandle()
        bondEngine = ql.DiscountingBondEngine(yieldcurvehandle)
        self.bondobject.setPricingEngine(bondEngine)
        self.is_valued = True
        self.valuation_params.update({'yieldcurve':yieldcurve})
    
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
        self.cap = setupparams['cap']
        self.floor = setupparams['floor']
        self.fixing = setupparams['fixing']
        if self.fixing != None:
            fixingdate = [self.coupon_index.fixingDate(ql.Settings.instance().evaluationDate)]
            ql.IndexManager.instance().clearHistory(self.coupon_index.name())
            self.coupon_index.addFixings(fixingdate,[self.fixing])
        self.bondobject = ql.FloatingRateBond(self.settlement_days,
                                              self.facevalue,
                                              self.getSchedule(),
                                              self.coupon_index,
                                              self.day_count,
                                              self.business_convention,
                                              spreads=self.coupon_spread,
                                              inArrears=self.inArrears,
                                              caps=[],
                                              floors=[])
    def setBlackPricer(self):
        pricer = ql.BlackIborCouponPricer()

        # optionlet volatilities
        volatility = 0.10;
        vol = ql.ConstantOptionletVolatility(self.settlement_days,
                                          self.calendar,
                                          self.business_convention,
                                          volatility,
                                          self.day_count)
        
        pricer.setCapletVolatility(ql.OptionletVolatilityStructureHandle(vol))
        #setCouponPricer(floatingRateBond.cashflows(),pricer)
        ql.setCouponPricer(self.bondobject.cashflows(),pricer)
        
            

class FixedRateConvertibleBond(Bond):
    def __init__(self,setupparams):
        Bond.__init__(self,setupparams)
        self.coupon_rates = [setupparams['coupon_rates']]
        self.conversion_ratio = setupparams['conversion_ratio']
        self.conversion_price = setupparams['conversion_price']
        self.call_schedule = setupparams['call_schedule']
        self.put_schedule = setupparams['put_schedule']
        self.dividend_schedule = setupparams['dividend_schedule']
        self.credit_spread = setupparams['credit_spread']
        
        ## Create call and put schedule
        
        callability_schedule = ql.CallabilitySchedule()
        try:
            for call_date, call_price in zip(self.call_schedule[0],self.call_schedule[1]):
                callability_price = ql.CallabilityPrice(call_price,ql.CallabilityPrice.Clean)
                callability_schedule.append(ql.Callability(callability_price,
                                                           ql.Callability.Call,qlMaps.qlDates(call_date)))
        except:
            pass
        try:
            for put_date, put_price in zip(self.put_schedule[0],self.put_schedule[1]):
                puttability_price = ql.CallabilityPrice(put_price,ql.CallabilityPrice.Clean)
                callability_schedule.append(ql.Callability(puttability_price,
                                                           ql.Callability.Put,qlMaps.qlDates(put_date)))            
        except:
            pass
        ## Create dividend schedule
        dividend_schedule = ql.DividendSchedule()
        try:
            for div_date, div_amount in zip(self.dividend_schedule[0],self.dividend_schedule[1]):
                dividend_schedule.append(ql.FixedDividend(div_amount,qlMaps.qlDates(div_date)))            
        except:
            pass
        calc_date = ql.Settings.instance().evaluationDate
        print(calc_date)                                
        #American Exercise
        
        exercise = ql.AmericanExercise(calc_date,qlMaps.qlDates(self.maturity_date))
        credit_spread_handle = ql.QuoteHandle(ql.SimpleQuote(self.credit_spread))
        
        self.bondobject = ql.ConvertibleFixedCouponBond(exercise,
                                                        self.conversion_ratio,
                                                        dividend_schedule,
                                                        callability_schedule,
                                                        credit_spread_handle,
                                                        qlMaps.qlDates(self.issue_date),
                                                        self.settlement_days,
                                                        self.coupon_rates,  
                                                        self.day_count,  
                                                        self.getSchedule(),
                                                        self.facevalue)
        
    def valuation(self,
                  underlying_spot,
                  yieldcurve,
                  volcurve,
                  dividendcurve,
                  steps=1000):

            underlying_quote = ql.SimpleQuote(underlying_spot)
            underlying_quote_handle = ql.QuoteHandle(underlying_quote)
            bsm_process = ql.BlackScholesMertonProcess(underlying_quote_handle,
                                                           dividendcurve.getCurveHandle(),
                                                           yieldcurve.getCurveHandle(),
                                                           volcurve.getCurveHandle())
            bondEngine = ql.BinomialConvertibleEngine(bsm_process,'crr',steps)
            
            self.bondobject.setPricingEngine(bondEngine)
            self.is_valued = True
            self.valuation_params.update({'yieldcurve':yieldcurve,
                                          'volcurve': volcurve,
                                          'dividendcurve': dividendcurve})
 

class FixedRateCallableBond(Bond):
    def __init__(self,setupparams):
        Bond.__init__(self,setupparams)
        self.coupon_rates = [setupparams['coupon_rates']]
        self.call_schedule = setupparams['call_schedule']
        self.put_schedule = setupparams['put_schedule']
        
        ## Create call and put schedule
        
        callability_schedule = ql.CallabilitySchedule()
        try:
            for call_date, call_price in zip(self.call_schedule[0],self.call_schedule[1]):
                callability_price = ql.CallabilityPrice(call_price,ql.CallabilityPrice.Clean)
                callability_schedule.append(ql.Callability(callability_price,
                                                           ql.Callability.Call,qlMaps.qlDates(call_date)))
        except:
            pass
        try:
            for put_date, put_price in zip(self.put_schedule[0],self.put_schedule[1]):
                puttability_price = ql.CallabilityPrice(put_price,ql.CallabilityPrice.Clean)
                callability_schedule.append(ql.Callability(puttability_price,
                                                           ql.Callability.Put,qlMaps.qlDates(put_date)))            
        except:
            pass
        #calc_date = ql.Settings.instance().evaluationDate
              
        self.bondobject = ql.CallableFixedRateBond(self.settlement_days,
                                                   self.facevalue,     
                                                   self.getSchedule(),
                                                   self.coupon_rates,
                                                   self.day_count,
                                                   self.business_convention,
                                                   self.facevalue,
                                                   qlMaps.qlDates(self.issue_date),
                                                   callability_schedule)

    def valuation(self,
                  yieldcurve,
                  mean_reversion=0.03,
                  rate_vol=0.12,
                  grid_points=40):

            short_rate_model = ql.HullWhite(yieldcurve.getCurveHandle(),
                                            mean_reversion,
                                            rate_vol)
    
            bondEngine = ql.TreeCallableFixedRateBondEngine(short_rate_model,
                                                            grid_points)
            
            self.bondobject.setPricingEngine(bondEngine)
            self.is_valued = True
            self.valuation_params.update({'yieldcurve':yieldcurve,
                                          'mean_reversion': mean_reversion,
                                          'rate_vol': rate_vol,
                                          'grid_points':grid_points})
                                               

        
        
