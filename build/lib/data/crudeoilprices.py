# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 20:49:38 2018

@author: Santosh Bag
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import requests
import datetime #import date, timedelta
from pandas import DataFrame
from bs4 import BeautifulSoup

import mrigutilities

def crude_download():
    print("Crude Oil Prices Download started", end =" ")
    engine = mrigutilities.sql_engine()
    
    url = 'https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm'
    
    s = requests.Session()
    response = s.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    price_table = soup.find_all(class_='DataB')
    WTI = [price_table[i].text for i in range(0,5)]
    price_table = soup.find_all(class_='Current2')
    WTI.append(price_table[0].text)
    price_table = soup.find_all(class_='DataB')
    BRENT = [price_table[i].text for i in range(5,10)]
    price_table = soup.find_all(class_='Current2')
    BRENT.append(price_table[1].text)
    
    date_table = soup.find_all(class_='Series5')
    dates = [date_table[i].text for i in range(0,6)]
    today = datetime.date.today()
    
    #print(WTI)
    #print(BRENT)
    #print(dates)
    
    for i in range(0,len(dates)):
        
        sql = "INSERT INTO crudeoil_prices (value_date, crude_benchmark, price, download_date) VALUES "\
               + "( '"+dates[i]+"','WTI','"+WTI[i]+"','"+today.strftime('%Y-%m-%d')+"'), " \
               + "( '"+dates[i]+"','BRENT','"+BRENT[i]+"','"+today.strftime('%Y-%m-%d')+"')"
        
        try:       
            #print(sql)
            engine.execute(sql)
        except:
            pass
    print("Crude Oil Prices Download finished \n")
if __name__ == '__main__':
    crude_download()