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
class MarketFutures():
    def __init__(self,symbol,strike,expiry):
        self.symbol = symbol
        self.strike = strike
        self.expiry = expiry
        self.underlying = mu.price(symbol)
        self.analytics = None
        self.oh = pd.DataFrame()

        args = {'futures_name':self.symbol+"_"+self.expiry.strftime('%d%b'),
                'underlying_name':self.symbol,
                'maturity_date':self.expiry,
                'strike': self.strike,
                'day_count':'30-360',
                'calendar':'India'}
        
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
                foh.option_type='%s' and expiry='%s' and foh.date=sh.date and \
                sh.date >= '%s' order by foh.date desc limit 10"    
        engine = mu.sql_engine()
    #    oh = nsepy.get_history(symbol,startdate,enddate,option_type=option_type,strike_price=strike,expiry_date=expiry)
    #    oh = oh[['Close','Open','High','Low','Open Interest','Underlying']]
        oh = pd.read_sql(sql%(self.symbol,'XX',self.expiry.strftime('%Y-%m-%d'),startdate.strftime('%Y-%m-%d')),engine)

        if not oh.empty:
            oh.set_index('date',inplace=True)
            oh.rename(columns=lambda x: x.replace('ltp','Price').capitalize().replace('Oi','Open Interest'),inplace=True)            
            oh = oh.apply(pd.to_numeric,errors='coerce')
            oh = oh.dropna()
            self.oh = oh
        
        return self.oh

    def valuation(self,ltp,spot=None,rate=None,vol=None):
        
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
        if str(ltp).replace('.','',1).isdigit():
            price = float(str(ltp))
            self.ltp = price
        elif not self.oh.empty:
            print(self.oh)
            close = list(self.oh['Price'])
            if str(close[0]).replace('.','',1).isdigit():
                price = float(str(close[0]))
                self.ltp = price

        # self.ltp = price
            
            
        args = {'day_count':'30-360',
                'calendar': 'India',
                'compounding' : 'Compounded',
                'compounding_frequency' :'Annual',
                'interpolation' : 'Linear'}
    
        if mu.args_inspector(args)[0]:
            for arg_name in args:
                try:
                    args[arg_name] = qlMaps.QL[args[arg_name]]
                except:
                    pass

        self.futures.valuation(ltp)
    
        self.analytics = self.futures.getAnalytics()
        self.analytics['Underlying'] =  self.underlying_spot
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
    expiry = datetime.date(2024,5,30)
    dish = MarketFutures('NIFTY',20000,expiry)
    # dish.get_price_vol()
    # print(dish.oh)
    res = dish.valuation(22006)
    print(res)
