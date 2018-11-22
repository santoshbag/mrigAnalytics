# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 17:37:47 2018

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import mrigutilities as mu
import datetime, dateutil.relativedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import research.math as rm
import stockstats as ss
import requests
from bs4 import BeautifulSoup




class Stock():
    def __init__(self,name):
        self.symbol = name
        self.quote = mu.getStockQuote(name)
        self.industry = mu.getIndustry(name)
        
    
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
        print(startdate)
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
        self.pricevol_data['10_day_SMA'] = dataset.get('close_10_sma')
        self.pricevol_data['30_day_SMA'] = dataset.get('close_30_sma')
        self.pricevol_data['50_day_SMA'] = dataset.get('close_50_sma')
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

        
    def get_ratios(self):    
        sql = "select * from ratios where symbol='" + self.symbol + "' and ratio_date = "\
               + "(select ratio_date from ( select ratio_date,download_date from ratios where symbol='" + self.symbol + "' order by ratio_date desc,download_date desc limit 1) dt)"
        sql = "select * from (select * , rank() over (partition by ratio_date order by download_date desc) from ratios where symbol='" + self.symbol + "') rt where rank=1 order by ratio_date desc"                      
        engine = mu.sql_engine()
        self.ratio_data = pd.read_sql(sql,engine)
        if not self.ratio_data.empty:
            self.ratio_data.set_index('ratio_date',inplace=True)
            
    def optionChain(self):
        Base_url =("https://www.nseindia.com/live_market/dynaContent/"+
                   "live_watch/option_chain/optionKeys.jsp?symbolCode=2772&symbol=UBL&"+
                   "symbol=UBL&instrument=OPTSTK&date=-&segmentLink=17&segmentLink=17")
        Base_url = ("https://www.nseindia.com/live_market/dynaContent/"+
                    "live_watch/option_chain/optionKeys.jsp?segmentLink=17&instrument=OPTSTK"+
                    "&symbol=%s&date=%s")
        
        expiries = mu.get_futures_expiry(datetime.date.today(),datetime.date.today())
        
        option_chain = []
        for dt in expiries:
            expdt = str(dt.day)+dt.strftime('%b').upper()+str(dt.year)
            page = requests.get(Base_url %(self.symbol,expdt))
            page.status_code
            page.content
            
            soup = BeautifulSoup(page.content, 'html.parser')
            #print(soup.prettify())
            
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
                            
    #        print (col_list_fnl)          
            
            table_cls_2 = soup.find(id="octable")
            all_trs = table_cls_2.find_all('tr')
            req_row = table_cls_2.find_all('tr')
            
            new_table = pd.DataFrame(index=range(0,len(req_row)-3) , columns=col_list_fnl)
            
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
                     new_table.ix[row_marker,[nu]]= tr
                     
                 row_marker += 1   
            new_table['Expiry'] = dt
            new_table.set_index('Expiry',inplace=True)
            option_chain.append(new_table)
        option_chain = pd.concat(option_chain)
    #    print (optionchain)
        return option_chain

class Index():
    def __init__(self,name):
        self.symbol = name
        self.quote = mu.getIndexQuote(name)
        
    
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
        print(startdate)
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
        self.pricevol_data['10_day_SMA'] = dataset.get('close_10_sma')
        self.pricevol_data['30_day_SMA'] = dataset.get('close_30_sma')
        self.pricevol_data['50_day_SMA'] = dataset.get('close_50_sma')
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
    stock_adjust()