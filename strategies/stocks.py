# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 17:37:47 2018

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import mrigutilities as mu
import data.moneycontrol as mc
import mrigstatics
import datetime, dateutil.relativedelta
import pandas as pd
import numpy as np
import research.analytics as ra
#import matplotlib.pyplot as plt
#import statsmodels.api as sm
#import research.math as rm
import stockstats as ss
import requests
import instruments.termstructure as rates
from bs4 import BeautifulSoup
from pandas.tseries.offsets import BDay
from mrigquery import fundamentals as funda
import json
from pandas.io.json import json_normalize



class Stock():

    benchmark_index1 = 'NIFTY 50'
    benchmark_index2 = None

    def __init__(self,name):
        self.symbol = name
        self.quote = mu.getStockQuote(name)
        # print(self.quote['lastPrice'])
        metadata = mu.getSecMasterData(name)
        if 'industry' in metadata.keys():
            self.industry = metadata['industry']
        if 'stock_name' in metadata.keys():
            self.stock_name = metadata['stock_name']
        if 'isin' in metadata.keys():
            self.isin = metadata['isin']
        if 'benchmark' in metadata.keys():
            self.set_benchmark_index2(metadata['benchmark'])
        
        self.beta = None
        self.risk = {}

    def get_benchmark_index1(self):
        return self.benchmark_index1

    def set_benchmark_index1(self, index):
        self.benchmark_index1 = index

    def get_benchmark_index2(self):
        return self.benchmark_index2

    def set_benchmark_index2(self, index):
        self.benchmark_index2 = index
    
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
#        print(startdate)
        self.pricevol_data = mu.getStockData(self.symbol,
                                           startdate,
                                           today)
        self.pricevol_data['daily_logreturns'] = np.log(self.pricevol_data['close_adj']/self.pricevol_data['close_adj'].shift(1))
        
        dataset = self.pricevol_data[['open', 'high', 'low', 'close_adj']]
        dataset.rename(columns={'close_adj':'close'}, inplace=True) 
        #dataset.rename(columns={"open":"Open"}, inplace=True) 
        #dataset.rename(columns={"low":"Low"}, inplace=True) 
        #dataset.rename(columns={"high":"High"}, inplace=True)    
        #print(dataset)
#        print(dataset.head(5))
        dataset = ss.StockDataFrame.retype(dataset)
        #Preparing the dataset
#        dataset['H-L'] = dataset['high'] - dataset['low']
#        dataset['O-C'] = dataset['close'] - dataset['open']
        self.pricevol_data['20_day_SMA'] = dataset.get('close_20_sma')
        self.pricevol_data['30_day_SMA'] = dataset.get('close_30_sma')
        self.pricevol_data['40_day_SMA'] = dataset.get('close_40_sma')
        self.pricevol_data['60_day_SMA'] = dataset.get('close_60_sma')
        self.pricevol_data['100_day_SMA'] = dataset.get('close_100_sma')
        self.pricevol_data['200_day_SMA'] = dataset.get('close_200_sma')
        self.pricevol_data['Std_dev']= dataset['close'].rolling(5).std()
        #dataset['RSI'] = talib.RSI(dataset['close'].values, timeperiod = 9)
        #dataset['Williams %R'] = talib.WILLR(dataset['High'].values, dataset['Low'].values, dataset['close'].values, 7)
        
        self.pricevol_data['RSI_9'] = dataset.get('rsi_9')
        self.pricevol_data['Williams_R_7'] = dataset.get('wr_7')
        self.pricevol_data['Bollinger_Band'] = dataset.get('boll')
        self.pricevol_data['Bollinger_UBand'] = dataset.get('boll_ub')
        self.pricevol_data['Bollinger_LBand'] = dataset.get('boll_lb')
        self.pricevol_data['MACD'] = dataset.get('macd')
        self.pricevol_data['MACDS'] = dataset.get('macds')

        
    def get_returns(self,period='1Y'):
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

        # sql = "select date, daily_log_returns from daily_returns where symbol='" + self.symbol + "' and date >='"+startdate.strftime('%Y-%m-%d')+"'"
        sql = """
        select date, symbol, daily_log_returns from daily_returns where symbol in ('{}','{}','{}') and date >='{}'
        """

        engine = mu.sql_engine()
        self.daily_logreturns = pd.read_sql(sql.format(self.symbol,self.benchmark_index1,self.benchmark_index2,startdate.strftime('%Y-%m-%d')),engine)
        if not self.daily_logreturns.empty:
            self.daily_logreturns.set_index('date',inplace=True)
            self.daily_logreturns.sort_index(inplace=True)

        
    # def get_ratios(self):
    #     sql = "select * from ratios where symbol='" + self.symbol + "' and ratio_date = "\
    #            + "(select ratio_date from ( select ratio_date,download_date from ratios where symbol='" + self.symbol + "' order by ratio_date desc,download_date desc limit 1) dt)"
    #     sql = "select * from (select * , rank() over (partition by ratio_date order by download_date desc) from ratios where symbol='" + self.symbol + "') rt where rank=1 order by ratio_date desc"
    #     engine = mu.sql_engine()
    #     self.ratio_data = pd.read_sql(sql,engine)
    #     if not self.ratio_data.empty:
    #         self.ratio_data.set_index('ratio_date',inplace=True)

    def get_ratios(self):
        data = funda.getResults(self.symbol,result_type='ratios')
        data.index.name = 'ratios'
        data.reset_index(inplace=True)
        self.ratio_data = data

    def get_income_statement(self):
        data = funda.getResults(self.symbol,result_type='income_statement')
        data.index.name = 'income_statement'
        data.reset_index(inplace=True)
        self.income_statement = data

    def get_balance_sheet(self):
        data_assets = funda.getResults(self.symbol, result_type='assets')
        data_assets_top = pd.DataFrame([['' for c in data_assets.columns]], columns=data_assets.columns,
                                       index=['Assets'])
        data_liabilities = funda.getResults(self.symbol, result_type='liabilities')
        data_liabilities_top = pd.DataFrame([['' for c in data_assets.columns]], columns=data_liabilities.columns,
                                            index=['Liabilities'])
        data = pd.concat([data_assets_top, data_assets, data_liabilities_top, data_liabilities])
        data = data.fillna('')
        for c in data.columns:
            if data.loc['assets',c] == '':
                data.drop(columns=[c],inplace=True)
        data.index.name = 'balance_sheet'
        data.reset_index(inplace=True)
        self.balance_sheet = data
    def futures(self):
        futures_data = pd.DataFrame()        
        sql = "select * from option_history where symbol='"+ self.symbol + \
              "' and instrument='FUTSTK' and expiry >= now()"
        
        engine = mu.sql_engine()
        futures_data = pd.read_sql(sql,engine)
        if not futures_data.empty:
            futures_data.set_index('date',inplace=True)
            futures_data.index = pd.to_datetime(futures_data.index)
            
        return futures_data

    def get_levels(self):
        res = ra.level_analysis([self.symbol])
        if res is not None:
            self.level_chart = res['level_chart']
            self.pcr = res['pcr']
            self.max_pain = res['max_pain']
        else:
            self.level_chart = None
            self.pcr = None
            self.max_pain = None


    def optionChain(self):
        Base_url =("https://www1.nseindia.com/live_market/dynaContent/"+
                   "live_watch/option_chain/optionKeys.jsp?symbolCode=2772&symbol=UBL&"+
                   "symbol=UBL&instrument=OPTSTK&date=-&segmentLink=17&segmentLink=17")
        Base_url = ("https://www.nseindia.com/live_market/dynaContent/"+
                    "live_watch/option_chain/optionKeys.jsp?segmentLink=17&instrument=OPTSTK"+
                    "&symbol=%s&date=%s")
        Base_url = ("https://www.nseindia.com/option-chain?segmentLink=17&instrument=OPTSTK"+
                    "&symbol=%s&date=%s")        
        expiries = mu.get_futures_expiry(datetime.date.today(),datetime.date.today())
        
        option_chain = []
        try:
            for dt in expiries:
                expdt = str(dt.day)+dt.strftime('%b').upper()+str(dt.year)
                headers = {'User-Agent': 'Mozilla/5.0'} 
                url = Base_url %(self.symbol,expdt)
                print(url)
                page = requests.get(url,headers=headers)
                page.status_code
                page.content
                
                soup = BeautifulSoup(page.content, 'html.parser')
#                print(soup.prettify())
                
                table_it = soup.find_all(class_="opttbldata")
                table_cls_1 = soup.find_all(id="octable")
                
                
                col_list = []
                
                # The code given below will pull the headers of the Option Chain table
                for mytable in table_cls_1:
                    table_head = mytable.find('thead')
                    
                    try:
                        rows = table_head.find_all('tr')
                        for tr in rows: 
                            cols = tr.find_all('th')
                            for th in cols:
                                er = th.text
                                ee = er.encode('utf8')   
                                ee = str(ee, 'utf-8')
                                col_list.append(ee)
                                
                    except:
                        print ("no thead")
                    
                
                col_list_fnl = [e for e in col_list if e not in ('CALLS','PUTS','Chart','\xc2\xa0','\xa0')]
                if len(col_list_fnl) == 21:
                    for i in range(0,21):
                        col_list_fnl[i] = col_list_fnl[i].replace(' ' ,'_')
                        if i < 10:
                            col_list_fnl[i] = 'CALL_'+col_list_fnl[i]
                        if i > 10:
                            col_list_fnl[i] = 'PUT_'+col_list_fnl[i]
                                                    
                print (col_list_fnl)          
                
                table_cls_2 = soup.find(id="octable")
                all_trs = table_cls_2.find_all('tr')
                req_row = table_cls_2.find_all('tr')
#                print(len(list(enumerate(req_row))))
                new_table = pd.DataFrame(index=range(0,len(req_row)-3) , columns=col_list_fnl)
                row_marker = 0 
                
                for row_number, tr_nos in enumerate(req_row):
                     #print(row_number)
                     # This ensures that we use only the rows with values    
                     if row_number <=1 or row_number == len(req_row)-1:   
                         continue
                          
                     td_columns = tr_nos.find_all('td')
                     #print(td_columns[:1])
                     # This removes the graphs columns
                     select_cols = td_columns[1:22]                  
                     cols_horizontal = range(0,len(select_cols))
                     
                     for nu, column in enumerate(select_cols):
                         
                         utf_string = column.get_text()
                         utf_string = utf_string.strip('\n\r\t": ')
                         
                         tr = utf_string.encode('utf-8')
                         tr = str(tr, 'utf-8')
                         tr = tr.replace(',' , '')
                         new_table.iloc[row_marker,[nu]]= tr
                     row_marker += 1   
                new_table['Expiry'] = dt
                new_table.set_index('Expiry',inplace=True)
                option_chain.append(new_table)
        except:
            pass
        if len(option_chain) > 0:
            option_chain = pd.concat(option_chain)
        else:
            option_chain = pd.DataFrame()
        print (option_chain)
        return option_chain


    def max_drawdown(self,window_days=29, period_months=12):

        drawdown = mu.max_stock_drawdown(self.symbol,window_days,period_months)
        return drawdown

    def avg_drawdown(self,window_days=29, period_months=12):

        drawdown = mu.avg_stock_drawdown(self.symbol,window_days,period_months)
        return drawdown
        
    def get_risk(self,sym=None):
        beta, SD, VaR,sharpe,sortino = None,None,None,None,None
        if sym == None:
            sym = self.symbol
        return_sql = "select * from daily_returns dr where symbol in ('"+sym+"','NIFTY 50') and dr.date > (now() - interval '1 year')" #in ( select date from daily_returns where symbol = 'NIFTY 50' and price is not null and date > (now() - interval '1 year'))"      
        engine = mu.sql_engine()
        
        returns = pd.read_sql(return_sql,engine)
    
        datesql = "select curvedate from yieldcurve where curve='INR' order by curvedate desc limit 1"
        reference_date = engine.execute(datesql).fetchall()[0][0]
        riskfree_1y = rates.SpotZeroYieldCurve('INR',reference_date)
        riskfree_1y = riskfree_1y.getZeroRate(reference_date+datetime.timedelta(days=360))

        if not returns.empty:
            returns.set_index('symbol',inplace=True)
            A = list(returns[returns['date'].isin(set(returns['date'].loc['NIFTY 50']) & set(returns['date'].loc[sym]))]['daily_log_returns'].loc['NIFTY 50'])
            B = list(returns[returns['date'].isin(set(returns['date'].loc['NIFTY 50']) & set(returns['date'].loc[sym]))]['daily_log_returns'].loc[sym])
            try:
                beta = np.cov(A,B)[0][1]/np.var(A)
                self.risk.update = {'Beta':beta}
            except:
                pass
            try:
                SD = np.std(B)*np.sqrt(250)
                self.risk.update({'SD':SD})
            except:
                pass
            try:
#                VaR = self.quote['securityVar']
                VaR95 = 1.65*np.std(B)
                self.risk.update({'VaR(95)':VaR95})
            except:
                pass
            try:
                return_1Y = sum(B)
                sharpe = (return_1Y - riskfree_1y)/SD
                self.risk.update({'Sharpe':sharpe})
            except:
                pass
            try:
                return_1Y = sum(B)
                B_Down = [a if a < 0 else 0 for a in B]
                sortino = (return_1Y - riskfree_1y)/np.std(B_Down)
                self.risk.update({'Sortino':sortino})
            except:
                pass

            try:
                return_1Y = sum(B)
                treynor = (return_1Y - riskfree_1y)/beta
                self.risk.update({'Treynor':treynor})
            except:
                pass
            
        return self.risk


class Index():
    def __init__(self,name):
        self.symbol = name
        self.quote = mc.get_NSELive()
        
    
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
#        print(startdate)
        self.pricevol_data = mu.getIndexData(self.symbol,
                                           startdate,
                                           today)
        self.pricevol_data['daily_logreturns'] = np.log(self.pricevol_data['close_adj']/self.pricevol_data['close_adj'].shift(1))
        
        dataset = self.pricevol_data[['open', 'high', 'low', 'close_adj']]
        dataset.rename(columns={'close_adj':'close'}, inplace=True) 
        #dataset.rename(columns={"open":"Open"}, inplace=True) 
        #dataset.rename(columns={"low":"Low"}, inplace=True) 
        #dataset.rename(columns={"high":"High"}, inplace=True)    
        #print(dataset)
#        print(dataset.head(5))
        dataset = ss.StockDataFrame.retype(dataset)
        #Preparing the dataset
#        dataset['H-L'] = dataset['high'] - dataset['low']
#        dataset['O-C'] = dataset['close'] - dataset['open']
        self.pricevol_data['20_day_SMA'] = dataset.get('close_20_sma')
        self.pricevol_data['30_day_SMA'] = dataset.get('close_30_sma')
        self.pricevol_data['40_day_SMA'] = dataset.get('close_40_sma')
        self.pricevol_data['60_day_SMA'] = dataset.get('close_60_sma')
        self.pricevol_data['100_day_SMA'] = dataset.get('close_100_sma')
        self.pricevol_data['200_day_SMA'] = dataset.get('close_200_sma')
        self.pricevol_data['Std_dev']= dataset['close'].rolling(5).std()
        #dataset['RSI'] = talib.RSI(dataset['close'].values, timeperiod = 9)
        #dataset['Williams %R'] = talib.WILLR(dataset['High'].values, dataset['Low'].values, dataset['close'].values, 7)
        
        self.pricevol_data['RSI_9'] = dataset.get('rsi_9')
        self.pricevol_data['Williams_R_7'] = dataset.get('wr_7')
        self.pricevol_data['Bollinger_Band'] = dataset.get('boll')
        self.pricevol_data['Bollinger_UBand'] = dataset.get('boll_ub')
        self.pricevol_data['Bollinger_LBand'] = dataset.get('boll_lb')
        self.pricevol_data['MACD'] = dataset.get('macd')
        self.pricevol_data['MACDS'] = dataset.get('macds')

        
    def get_returns(self,period='1Y'):
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

        sql = "select date, daily_log_returns from daily_returns where symbol='" + self.symbol + "' and date >='"+startdate.strftime('%Y-%m-%d')+"'"

        engine = mu.sql_engine()
        self.daily_logreturns = pd.read_sql(sql,engine)
        if not self.daily_logreturns.empty:
            self.daily_logreturns.set_index('date',inplace=True)

    def get_levels(self):
        res = ra.level_analysis([self.symbol])
        if res is not None:
            self.level_chart = res['level_chart']
            self.pcr = res['pcr']
            self.max_pain = res['max_pain']
        else:
            self.level_chart = None
            self.pcr = None
            self.max_pain = None

    def optionChain(self):
        Base_url =("https://www1.nseindia.com/live_market/dynaContent/"+
                   "live_watch/option_chain/optionKeys.jsp?symbolCode=2772&symbol=UBL&"+
                   "symbol=UBL&instrument=OPTSTK&date=-&segmentLink=17&segmentLink=17")
        Base_url = ("https://www1.nseindia.com/live_market/dynaContent/"+
                    "live_watch/option_chain/optionKeys.jsp?segmentLink=17&instrument=OPTIDX"+
                    "&symbol=%s&date=%s")
        
        expiries = mu.get_indexoptions_expiry()
#        print(expiries)
        today = datetime.date.today()
#        expiries = [dt if dt >= today else dt for dt in expiries]
        
        option_chain = []
        try:
            for dt in expiries:
                expdt = str(dt.day)+dt.strftime('%b').upper()+str(dt.year)
                url = Base_url %(mrigstatics.INDEX_MAP_FOR_OC[self.symbol],expdt)
#                print(url)
                headers = {'User-Agent': 'Mozilla/5.0'}                
                page = requests.get(url,headers=headers)
                page.status_code
                page.content
                
                soup = BeautifulSoup(page.content, 'html.parser')
#                print(soup.prettify())
                
                table_it = soup.find_all(class_="opttbldata")
                table_cls_1 = soup.find_all(id="octable")
                
                
                col_list = []
                
                # The code given below will pull the headers of the Option Chain table
                for mytable in table_cls_1:
                    table_head = mytable.find('thead')
                    
                    try:
                        rows = table_head.find_all('tr')
                        for tr in rows: 
                            cols = tr.find_all('th')
                            for th in cols:
                                er = th.text
                                ee = er.encode('utf8')   
                                ee = str(ee, 'utf-8')
                                col_list.append(ee)
                                
                    except:
                        print ("no thead")
                    
                
                col_list_fnl = [e for e in col_list if e not in ('CALLS','PUTS','Chart','\xc2\xa0','\xa0')]
                if len(col_list_fnl) == 21:
                    for i in range(0,21):
                        col_list_fnl[i] = col_list_fnl[i].replace(' ' ,'_')
                        if i < 10:
                            col_list_fnl[i] = 'CALL_'+col_list_fnl[i]
                        if i > 10:
                            col_list_fnl[i] = 'PUT_'+col_list_fnl[i]
                                                    
#                print (col_list_fnl)          
                
                table_cls_2 = soup.find(id="octable")
                all_trs = table_cls_2.find_all('tr')
                req_row = table_cls_2.find_all('tr')
                
                new_table = pd.DataFrame(index=range(0,len(req_row)-3) , columns=col_list_fnl)
#                print("new table")
#                print(new_table)
                row_marker = 0 
                
                for row_number, tr_nos in enumerate(req_row):
                     
                     # This ensures that we use only the rows with values    
                     if row_number <=1 or row_number == len(req_row)-1:   
                         continue
                          
                     td_columns = tr_nos.find_all('td')
                     
                     # This removes the graphs columns
                     select_cols = td_columns[1:22]                  
                     cols_horizontal = range(0,len(select_cols))
                      
                     for nu, column in enumerate(select_cols):
                         
                         utf_string = column.get_text()
                         utf_string = utf_string.strip('\n\r\t": ')
                         
                         tr = utf_string.encode('utf-8')
                         tr = str(tr, 'utf-8')
                         tr = tr.replace(',' , '')
                         new_table.iloc[row_marker,[nu]]= tr
                         
                     row_marker += 1   
                new_table['Expiry'] = dt
                new_table.set_index('Expiry',inplace=True)
#                print(new_table)
                option_chain.append(new_table)
        except:
            pass
        if len(option_chain) > 0:
            option_chain = pd.concat(option_chain)
        else:
            option_chain = pd.DataFrame()
    #    print (optionchain)
        return option_chain

    def get_ratios(self):
        today = pd.datetime.today() - BDay(1)
        sql = "select date, pe,pb,div_yield from stock_history where symbol='%s' \
        and series='IN' and date in (SELECT date '%s' - interval '1' month * s.a AS date \
        FROM generate_series(0,10,1) AS s(a)) order by date desc "
        
        engine = mu.sql_engine()
        self.ratio_data = pd.read_sql(sql%(self.symbol,today.strftime('%Y-%m-%d')),engine)
        if not self.ratio_data.empty:
            self.ratio_data.set_index('date',inplace=True)


    def get_risk(self,sym=None):
        beta, SD, VaR,sharpe,sortino = None,None,None,None,None
        if sym == None:
            sym = self.symbol
        return_sql = "select * from daily_returns dr where symbol in ('"+sym+"','NIFTY 50') and dr.date > (now() - interval '1 year')" #in ( select date from daily_returns where symbol = 'NIFTY 50' and price is not null and date > (now() - interval '1 year'))"      
        engine = mu.sql_engine()
        
        returns = pd.read_sql(return_sql,engine)
    
        datesql = "select curvedate from yieldcurve where curve='INR' order by curvedate desc limit 1"
        reference_date = engine.execute(datesql).fetchall()[0][0]
        riskfree_1y = rates.SpotZeroYieldCurve('INR',reference_date)
        riskfree_1y = riskfree_1y.getZeroRate(reference_date+datetime.timedelta(days=360))

        if not returns.empty:
            returns.set_index('symbol',inplace=True)
            A = list(returns[returns['date'].isin(set(returns['date'].loc['NIFTY 50']) & set(returns['date'].loc[sym]))]['daily_log_returns'].loc['NIFTY 50'])
            B = list(returns[returns['date'].isin(set(returns['date'].loc['NIFTY 50']) & set(returns['date'].loc[sym]))]['daily_log_returns'].loc[sym])
            try:
                beta = np.cov(A,B)[0][1]/np.var(A)
                self.risk = {'Beta':beta}
            except:
                pass
            try:
                SD = np.std(B)*np.sqrt(250)
                self.risk.update({'SD':SD})
            except:
                pass
            try:
#                VaR = self.quote['securityVar']
                VaR95 = 1.65*np.std(B)
                self.risk.update({'VaR(95)':VaR95})
            except:
                pass
            try:
                return_1Y = sum(B)
                sharpe = (return_1Y - riskfree_1y)/SD
                self.risk.update({'Sharpe':sharpe})
            except:
                pass
            try:
                return_1Y = sum(B)
                B_Down = [a if a < 0 else 0 for a in B]
                sortino = (return_1Y - riskfree_1y)/np.std(B_Down)
                self.risk.update({'Sortino':sortino})
            except:
                pass

            try:
                return_1Y = sum(B)
                treynor = (return_1Y - riskfree_1y)/beta
                self.risk.update({'Treynor':treynor})
            except:
                pass
            
        return self.risk


class MutualFunds():
    benchmark_index1 = 'NIFTY 50'
    benchmark_index2 = None

    def __init__(self, name):
        self.symbol = name
        nav = mu.getMFNAV([name])
        if len(nav) > 0:
            nav = "{:.2f}".format(nav.head(1)['nav'].values[0])
        else:
            nav = ''
        self.quote = nav
        # print(self.quote['lastPrice'])
        metadata = mu.getMFSecMasterData(name)
        if 'amc' in metadata.keys():
            self.amc = metadata['amc']
        if 'scheme_subscrip_type' in metadata.keys():
            self.subscription_type = metadata['scheme_subscrip_type']
        if 'isin' in metadata.keys():
            self.isin = metadata['isin']
        if 'launch_date' in metadata.keys():
            self.launch_date = metadata['launch_date']
        if 'scheme_asset_type_1' in metadata.keys():
            self.asset_type_1 = metadata['scheme_asset_type_1']
        if 'scheme_asset_type_2' in metadata.keys():
            self.asset_type_2 = metadata['scheme_asset_type_2']
        if 'scheme_plan_type_1' in metadata.keys():
            self.plan_type_1 = metadata['scheme_plan_type_1']
        if 'scheme_plan_type_2' in metadata.keys():
            self.plan_type_2 = metadata['scheme_plan_type_2']
        if 'min_inv_amt' in metadata.keys():
            self.min_inv_amt = metadata['min_inv_amt']
        if 'aum' in metadata.keys():
            self.aum = metadata['aum']
        if 'benchmark' in metadata.keys():
            self.set_benchmark_index2(metadata['benchmark'])

        self.beta = None
        self.risk = {}

    def get_benchmark_index1(self):
        return self.benchmark_index1

    def set_benchmark_index1(self, index):
        self.benchmark_index1 = index

    def get_benchmark_index2(self):
        return self.benchmark_index2

    def set_benchmark_index2(self, index):
        self.benchmark_index2 = index

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
        #        print(startdate)
        self.pricevol_data = mu.getMFNAV([self.symbol],
                                             startdate)
        self.pricevol_data['daily_logreturns'] = np.log(
            self.pricevol_data['nav'] / self.pricevol_data['nav'].shift(1))

    def get_returns(self, period='1Y'):
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

        # sql = "select date, daily_log_returns from daily_returns where symbol='" + self.symbol + "' and date >='"+startdate.strftime('%Y-%m-%d')+"'"
        sql = """
        select nav_date, scheme_name as symbol, daily_log_return as daily_log_returns from mf_returns where scheme_name in ('{}') and nav_date >='{}'
        """

        engine = mu.sql_engine()
        self.daily_logreturns = pd.read_sql(
            sql.format(self.symbol, startdate.strftime('%Y-%m-%d')),
            engine)
        if not self.daily_logreturns.empty:
            self.daily_logreturns.set_index('nav_date', inplace=True)
            self.daily_logreturns.sort_index(inplace=True)

    # def get_ratios(self):
    #     sql = "select * from ratios where symbol='" + self.symbol + "' and ratio_date = "\
    #            + "(select ratio_date from ( select ratio_date,download_date from ratios where symbol='" + self.symbol + "' order by ratio_date desc,download_date desc limit 1) dt)"
    #     sql = "select * from (select * , rank() over (partition by ratio_date order by download_date desc) from ratios where symbol='" + self.symbol + "') rt where rank=1 order by ratio_date desc"
    #     engine = mu.sql_engine()
    #     self.ratio_data = pd.read_sql(sql,engine)
    #     if not self.ratio_data.empty:
    #         self.ratio_data.set_index('ratio_date',inplace=True)


def stock_adjust():
    
    #List of Stocks to adjust
    today = datetime.date.today()
    engine = mu.sql_engine()
    disable_sql = "alter table stock_history disable trigger return_trigger"
    enable_sql = "alter table stock_history enable trigger return_trigger"

    sql = "select symbol, ex_date, factor from corp_action_view order by symbol desc, ex_date desc" #where download_date = (select download_date from corp_action_view order by download_date desc limit 1)"
    
    engine.execute(disable_sql)                                                                                     
    updates = engine.execute(sql).fetchall()
    
    sql = ""
    for update in updates:
        stock = update[0]
        exdate = update[1]
        factor = update[2]
        
        if exdate <=today:
            sql = sql + " UPDATE stock_history set "\
                + " close_adj = close * "+str(factor)+", "\
                +" volume_adj = volume /"+str(factor)+" "\
                +" where symbol = '"+stock+"' "\
                +" and date < '"+exdate.strftime('%Y-%m-%d')+"'; "
    

    #print(sql)
    engine.execute(sql)
    engine.execute(enable_sql)

if __name__ == '__main__':
    nifty = Stock('SGBAUG28V')
#    print(nifty.quote)
#    nifty.get_ratios()
    # nifty.optionChain()
    
#    print(niftyoc)
