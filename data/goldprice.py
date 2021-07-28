# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 20:02:18 2018

@author: Santosh Bag
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import requests
import datetime #import date, timedelta
from pandas import DataFrame,read_excel
from bs4 import BeautifulSoup
import numpy as np

import mrigutilities

def gold_download():
    print("Gold Rates download started", end =" ")
    engine = mrigutilities.sql_engine()
    
    url = 'https://www.gold.org/data/gold-price'
    
    s = requests.Session()
    response = s.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    today = datetime.date.today()
    
    price_table = soup.find_all(class_='mid')
    
    #price = price_table[0].find_all(class_='value')[0].text.replace(",","")
    price = price_table[0].text.replace(",","")
    date = soup.find_all(class_='timestamp')[0].text.split(",")[0]
    date = datetime.datetime.strptime(date,'%d %B %Y').date()
    #print(price)
    #print(date)
    sql = "INSERT INTO gold_prices (value_date, price, download_date) VALUES ( '"\
                                   +date.strftime('%Y-%m-%d')+"','"\
                                   +price+"','"\
                                   +today.strftime('%Y-%m-%d')+"')"
    engine.execute(sql)
    print("Gold Rates download finished\n")
    

def gold_download_new():
    print("Gold Rates download started", end =" ")
    engine = mrigutilities.sql_engine()
    datadir = os.path.dirname(__file__)

    
    file = os.path.join(datadir,'..','..','data','input','Prices.xls')
#    file = "F:\\NSEDATA\\Daily\\Prices.xlsx"
    
    today = datetime.date.today()

    dfs = read_excel(file,sheet_name='Daily',skiprows=8,usecols='D:E')
    
    if not dfs.empty:
        dfs['download_date'] = today
        dfs = dfs.rename(columns={np.nan : 'price','Name':'value_date'})
        dfs.set_index('value_date',inplace=True)
        
        sql = 'delete from gold_prices'
        engine.execute(sql)
        
        dfs.to_sql('gold_prices',engine, if_exists='append', index=True)
        print(dfs.tail(10))

        print("Gold Rates download finished\n")
    
if __name__ == '__main__':
    gold_download_new()
