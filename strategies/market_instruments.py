# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 22:04:42 2019

@author: Santosh Bag
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import mrigutilities as mu
import datetime, dateutil
import pandas as pd
import instruments.options as options
import instruments.futures as futures
import instruments.termstructure as ts
import instruments.qlMaps as qlMaps

option_type_map = {'PE':'Put European',
                   'CE':'Call European',
                   'PA':'Put American',
                   'CA':'Call American'}

symbol_map = {'NIFTY 50': 'NIFTY'}
today = datetime.date.today()
class MarketOptions():
    def __init__(self,symbol,strike,expiry,option_type):
        self.symbol = symbol
        self.underlying_symbol = symbol
        self.strike = strike
        self.expiry = expiry
        self.option_type = option_type
        self.underlying = mu.price(symbol)
        self.analytics = None
        self.oh = pd.DataFrame()

        args = {'option_name':self.symbol+"_"+self.expiry.strftime('%d%b')+"_"+str(self.strike)+"_"+self.option_type,
                'underlying_name':self.symbol,
                'maturity_date':self.expiry,
                'option_type':option_type_map[self.option_type].split(' ')[0],
                'strike': self.strike,                               
                'exercise_type':option_type_map[self.option_type].split(' ')[1],
                'day_count':'30-360',
                'calendar':'India'}
        
        if mu.args_inspector(args)[0]:
            for arg_name in args:
                try:
                    args[arg_name] = qlMaps.QL[args[arg_name]]
                except:
                    pass
            self.option = options.VanillaEuropeanOption(args)
            self.discount_curve = None
            self.volatility_curve = None
            self.dividend_curve = None
            self.valuation_method = 'Black Scholes'

    def get_expiry(self):
        return self.expiry

    def get_underlying(self):
        return self.underlying_symbol

    def get_price_vol(self,period='1Y'):
        today = datetime.date.today()
        years=0
        months=0
        weeks=0
        days=0
        
        if period[-1] == 'Y':
            years = int(period[:-1])
        if period[-1] == 'M':
            months = int(period[:-1])
        if period[-1] == 'W':
            weeks = int(period[:-1])
        if period[-1] == 'D':
            days = int(period[:-1])

        startdate = today - dateutil.relativedelta.relativedelta(years=years,
                                                                 months=months,
                                                                 weeks=weeks,
                                                                 days=days)
        sql = "select foh.date,foh.close as ltp,foh.open,foh.high,foh.low, foh.oi, sh.close as underlying from futures_options_history foh \
                inner join stock_history sh on foh.symbol=sh.symbol where foh.symbol='%s' and \
                foh.strike='%s' and foh.option_type='%s' and expiry='%s' and foh.date=sh.date and \
                sh.date >= '%s' order by foh.date desc limit 10"    
        engine = mu.sql_engine()
    #    oh = nsepy.get_history(symbol,startdate,enddate,option_type=option_type,strike_price=strike,expiry_date=expiry)
    #    oh = oh[['Close','Open','High','Low','Open Interest','Underlying']]
        oh = pd.read_sql(sql%(self.symbol,str(self.strike),self.option_type,self.expiry.strftime('%Y-%m-%d'),startdate.strftime('%Y-%m-%d')),engine)

        if not oh.empty:
            oh.set_index('date',inplace=True)
            oh.rename(columns=lambda x: x.replace('ltp','Price').capitalize().replace('Oi','Open Interest'),inplace=True)            
            oh = oh.apply(pd.to_numeric,errors='coerce')
            oh = oh.dropna()
            self.oh = oh
        
        return self.oh

    def valuation(self,ltp,spot=None,rate=None,vol=None):
        
        """
        Option Greeks and Graphs--------------------------------------------------------------
        """
    
        """
        Set Interest Rate Curve
        """    
    
        args = {'day_count':'30-360',
                'calendar': 'India',
                'compounding' : 'Compounded',
                'compounding_frequency' :'Annual',
                'interpolation' : 'Linear',
                'shiftparameter' : None}
    
        if mu.args_inspector(args)[0]:
            for arg_name in args:
                try:
                    args[arg_name] = qlMaps.QL[args[arg_name]]
                except:
                    pass
    
        
        today = datetime.date.today()
        
        engine = mu.sql_engine()
        try:
            today = engine.execute("select curvedate from yieldcurve where curve='INR' order by curvedate desc limit 1").fetchall()[0][0]
        except:
            pass
        # self.discount_curve = ts.SpotZeroYieldCurve('INR',today)
        self.discount_curve = ts.FlatForwardYieldCurve(today,0.06)
        self.discount_curve.setupCurve(args)
    
        """
        Set Flat Volatility Curve
        """    
        spotVol = 0.30
        try:
            nse_vol = engine.execute("select nse_vol from stock_history where symbol='"+self.symbol+"' order by date desc limit 1").fetchall()
            nse_vol = nse_vol[0][0]
            # print(nse_vol)
            if nse_vol:
                spotVol = float(nse_vol)
        except:
            pass
        
        args = {'day_count':'30-360',
                'calendar': 'India',
                'spot_vols':spotVol,
                'compounding' : 'Compounded',
                'compounding_frequency' :'Annual',
                'interpolation' : 'Linear'}
    
        if mu.args_inspector(args)[0]:
            for arg_name in args:
                try:
                    args[arg_name] = qlMaps.QL[args[arg_name]]
                except:
                    pass
    
        
        self.volatility_curve = ts.FlatVolatilityCurve(today,spotVol)
        self.volatility_curve.setupCurve(args)
        
        """
        Set Flat Dividend Curve
        """    
        args = {'day_count':'30-360',
                'calendar': 'India',
                'flat_rate':0.01,
                'compounding' : 'Compounded',
                'compounding_frequency' :'Annual',
                'interpolation' : 'Linear'}
    
        if mu.args_inspector(args)[0]:
            for arg_name in args:
                try:
                    args[arg_name] = qlMaps.QL[args[arg_name]]
                except:
                    pass
    
        
        self.dividend_curve = ts.FlatDividendYieldCurve(today,args['flat_rate'])
        self.dividend_curve.setupCurve(args)
        
        """
        Set self.option Valuation and get Results
        """    
        self.valuation_method = 'Black Scholes'
        self.underlying_spot = self.underlying
        
        self.option.valuation(self.underlying_spot,
                         self.discount_curve,
                         self.volatility_curve,
                         self.dividend_curve,
                         self.valuation_method)
        
    #    if str(ltp).lstrip('-').replace('.','',1).isdigit():
        if str(ltp).replace('.','',1).isdigit():
            price = float(str(ltp))
            self.ltp = price
            try:
                spotVol = self.option.getImpliedVol(price)
                print('Implied Vol --> '+ str(spotVol))
            except:
                pass
        elif not self.oh.empty:
            print(self.oh)
            close = list(self.oh['Price'])
            if str(close[0]).replace('.','',1).isdigit():
                price = float(str(close[0]))
                self.ltp = price
                try:
                    spotVol = self.option.getImpliedVol(price)
                    print('Implied Vol --> ' + str(spotVol))
                except:
                    pass
        # self.ltp = price
            
            
        args = {'day_count':'30-360',
                'calendar': 'India',
                'spot_vols':spotVol,
                'compounding' : 'Compounded',
                'compounding_frequency' :'Annual',
                'interpolation' : 'Linear'}
    
        if mu.args_inspector(args)[0]:
            for arg_name in args:
                try:
                    args[arg_name] = qlMaps.QL[args[arg_name]]
                except:
                    pass
        
        self.volatility_curve = ts.FlatVolatilityCurve(today,args['spot_vols'])
        self.volatility_curve.setupCurve(args)
    
        self.option.valuation(self.underlying_spot,
                         self.discount_curve,
                         self.volatility_curve,
                         self.dividend_curve,
                         self.valuation_method)
    
        self.analytics = self.option.getAnalytics()
        self.analytics['volatility'] = spotVol
        self.analytics['Underlying'] =  self.underlying_spot
        return self.analytics
    
    def scenario_analysis(self,scenario=['SPOT'],scale=0.05):
        # if not scenario:
        #     if self.analytics:
        #         return self.analytics
        #     else:
        #         return self.valuation("-")
        #
        # spot = scenario['spot']

        val_date = today
        result = []
        print('Underlying -->'+ str(self.underlying))
        if 'TIME' in scenario:
            result = []
            step = max(1,int((self.expiry - today).days/100))
            while  val_date <= self.expiry:
                # print(val_date)
            # for spotprice in range(245,275):
            #     print(spotprice)
                self.option.valuation(self.underlying,
                         self.discount_curve,
                         self.volatility_curve,
                         self.dividend_curve,
                         self.valuation_method,
                          eval_date=val_date)
                res = self.option.getAnalytics()
                # print(res)
                result.append([val_date,res['NPV']])
                val_date = val_date + datetime.timedelta(days=step)
            result = pd.DataFrame(result,columns=['date','price'])

        if 'SPOT' in scenario:
            result = []
            # scale = 0.05
            interval = int(scale/0.01)
            first = int(self.underlying*(1-scale))
            last = int(self.underlying*(1+scale))
            # step = max(1,int((last-first)/(100*interval)))
            step = int((last - first) / (100 * interval))

            for spotprice in range(first,last,step):
                # print(spotprice)
                self.option.valuation(spotprice,
                         self.discount_curve,
                         self.volatility_curve,
                         self.dividend_curve,
                         self.valuation_method)
                res = self.option.getAnalytics()
                # print(res)
                result.append([spotprice,res['NPV']])
            result = pd.DataFrame(result,columns=['spot','price'])

        return result


class MarketFutures():
    def __init__(self, symbol, strike, expiry):
        self.symbol = symbol
        self.underlying_symbol = symbol
        self.strike = strike
        self.expiry = expiry
        self.underlying = mu.price(symbol)
        self.analytics = None
        self.oh = pd.DataFrame()

        args = {'futures_name': self.symbol + "_" + self.expiry.strftime('%d%b'),
                'underlying_name': self.symbol,
                'maturity_date': self.expiry,
                'strike': self.strike,
                'day_count': '30-360',
                'calendar': 'India'}

        if mu.args_inspector(args)[0]:
            for arg_name in args:
                try:
                    args[arg_name] = qlMaps.QL[args[arg_name]]
                except:
                    pass
            self.futures = futures.EquityFutures(args)
            self.discount_curve = None
            self.volatility_curve = None
            self.dividend_curve = None
            self.valuation_method = 'Black Scholes'

    def get_expiry(self):
        return self.expiry

    def get_underlying(self):
        return self.underlying_symbol

    def get_price_vol(self, period='1Y'):
        today = datetime.date.today()
        years = 0
        months = 0
        weeks = 0
        days = 0

        if period[-1] == 'Y':
            years = int(period[:-1])
        if period[-1] == 'M':
            months = int(period[:-1])
        if period[-1] == 'W':
            weeks = int(period[:-1])
        if period[-1] == 'D':
            days = int(period[:-1])

        startdate = today - dateutil.relativedelta.relativedelta(years=years,
                                                                 months=months,
                                                                 weeks=weeks,
                                                                 days=days)
        sql = "select foh.date,foh.close as ltp,foh.open,foh.high,foh.low, foh.oi, sh.close as underlying from futures_options_history foh \
                inner join stock_history sh on foh.symbol=sh.symbol where foh.symbol='%s' and \
                foh.option_type='%s' and expiry='%s' and foh.date=sh.date and \
                sh.date >= '%s' order by foh.date desc limit 10"
        engine = mu.sql_engine()
        #    oh = nsepy.get_history(symbol,startdate,enddate,option_type=option_type,strike_price=strike,expiry_date=expiry)
        #    oh = oh[['Close','Open','High','Low','Open Interest','Underlying']]
        oh = pd.read_sql(sql % (self.symbol, 'XX', self.expiry.strftime('%Y-%m-%d'), startdate.strftime('%Y-%m-%d')),
                         engine)

        if not oh.empty:
            oh.set_index('date', inplace=True)
            oh.rename(columns=lambda x: x.replace('ltp', 'Price').capitalize().replace('Oi', 'Open Interest'),
                      inplace=True)
            oh = oh.apply(pd.to_numeric, errors='coerce')
            oh = oh.dropna()
            self.oh = oh

        return self.oh

    def valuation(self, ltp, spot=None, rate=0.06, dividend=0):

        """
        Greeks and Graphs--------------------------------------------------------------
        """

        """
        Set Interest Rate Curve
        """

        """
        Set self.option Valuation and get Results
        """
        self.underlying_spot = self.underlying

        #    if str(ltp).lstrip('-').replace('.','',1).isdigit():
        if str(ltp).replace('.', '', 1).isdigit():
            price = float(str(ltp))
            self.ltp = price
        elif not self.oh.empty:
            print(self.oh)
            close = list(self.oh['Price'])
            if str(close[0]).replace('.', '', 1).isdigit():
                price = float(str(close[0]))
                self.ltp = price

        # self.ltp = price

        args = {'day_count': '30-360',
                'calendar': 'India',
                'compounding': 'Compounded',
                'compounding_frequency': 'Annual',
                'interpolation': 'Linear'}

        if mu.args_inspector(args)[0]:
            for arg_name in args:
                try:
                    args[arg_name] = qlMaps.QL[args[arg_name]]
                except:
                    pass

        self.futures.valuation(underlying_spot=self.underlying_spot,riskfree_rate=rate,dividend=dividend)

        self.analytics = self.futures.getAnalytics()
        self.analytics['Underlying'] = self.underlying_spot
        return self.analytics

    # def scenario_analysis(self,scenario=['SPOT']):
    #     # if not scenario:
    #     #     if self.analytics:
    #     #         return self.analytics
    #     #     else:
    #     #         return self.valuation("-")
    #     #
    #     # spot = scenario['spot']
    #
    #     val_date = today
    #     result = []
    #     print('Underlying -->'+ str(self.underlying))
    #     if 'TIME' in scenario:
    #         result = []
    #         step = max(1,int((self.expiry - today).days/100))
    #         while  val_date <= self.expiry:
    #             # print(val_date)
    #         # for spotprice in range(245,275):
    #         #     print(spotprice)
    #             self.option.valuation(self.underlying,
    #                      self.discount_curve,
    #                      self.volatility_curve,
    #                      self.dividend_curve,
    #                      self.valuation_method,
    #                       eval_date=val_date)
    #             res = self.option.getAnalytics()
    #             # print(res)
    #             result.append([val_date,res['NPV']])
    #             val_date = val_date + datetime.timedelta(days=step)
    #         result = pd.DataFrame(result,columns=['date','price'])
    #
    #     if 'SPOT' in scenario:
    #         result = []
    #         scale = 0.05
    #         first = int(self.underlying*(1-scale))
    #         last = int(self.underlying*(1+scale))
    #         step = max(1,int((last-first)/100))
    #
    #         for spotprice in range(first,last,step):
    #             # print(spotprice)
    #             self.option.valuation(spotprice,
    #                      self.discount_curve,
    #                      self.volatility_curve,
    #                      self.dividend_curve,
    #                      self.valuation_method)
    #             res = self.option.getAnalytics()
    #             # print(res)
    #             result.append([spotprice,res['NPV']])
    #         result = pd.DataFrame(result,columns=['spot','price'])
    #
    #     return result


if __name__ == '__main__':
    expiry = datetime.date(2023,10,26)
    dish = MarketOptions('NIFTY 50',20000,expiry,'PE')
    # dish.get_price_vol()
    # print(dish.oh)
    res = dish.valuation(382)
    # print(res)
    res = dish.scenario_analysis()
    print(res)
    res = dish.scenario_analysis(['TIME'])
    print(res)