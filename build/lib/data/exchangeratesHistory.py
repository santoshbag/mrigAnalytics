# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 17:39:37 2018

@author: Santosh Bag
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import requests
import datetime #import date, timedelta
from pandas import DataFrame
from bs4 import BeautifulSoup

import mrigutilities

def exchange_rates_download(startdate=None,enddate=None):
    print("Exchange Rates download started", end =" ")
    engine = mrigutilities.sql_engine()
    
    url = 'https://www.xe.com/currencytables/?from=INR&date='
    
    arguments = sys.argv[1:]
    
    if (startdate == None or enddate == None):
        startdate= datetime.date.today() - datetime.timedelta(days=1)
        enddate= datetime.date.today()
    
    today = datetime.date.today().strftime('%Y-%m-%d')
    try:
        startdate= datetime.date(int(arguments[0][0:4]),int(arguments[0][4:6]),int(arguments[0][6:8]))
        enddate= datetime.date(int(arguments[1][0:4]),int(arguments[1][4:6]),int(arguments[1][6:8]))
    except:
        pass
    
    xrates_cols = ['value_date','currency','rate','download_date']
    xratesfile = open("xratesfile.csv","a+")
    xratelist = []
    date = startdate
    while date < enddate :
        datestr = date.strftime('%Y-%m-%d')
        cururl = url + datestr
        s= requests.Session()
        response = s.get(cururl)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find_all(class_='tablesorter historicalRateTable-table')
        rows = table[0].find_all("tr")
        #for i in range(1,4):
        INRs = rows[1].find_all("td")
        EURs = rows[2].find_all("td")
        GBPs = rows[3].find_all("td")
        xratelist.append([datestr,'INR',INRs[3].text,today])
        xratelist.append([datestr,EURs[0].text,str(float(INRs[3].text)/float(EURs[3].text)),today])
        xratelist.append([datestr,GBPs[0].text,str(float(INRs[3].text)/float(GBPs[3].text)),today])
        date = date  + datetime.timedelta(days=1)
    
    xratelist = DataFrame(xratelist,columns=xrates_cols)
    xratelist.to_csv(xratesfile,index=False,header=False)
    
    #dt_handling = "to_char(\"Date\",'dd-Mon-YYYY') as \"Date\""
    xratelist = mrigutilities.clean_df_db_dups(xratelist,'exchange_rates',engine,dup_cols=["value_date","currency"])[0]
    try:
        xratelist.to_sql('exchange_rates',engine, if_exists='append', index=False)
    except:
        pass
    xratesfile.close()
    print("Exchange Rates download finished\n")
    
if __name__ == '__main__':
    
    startdate,enddate = None,None
    
    arguments = sys.argv[1:]    
    try:
        startdate= datetime.date(int(arguments[0][0:4]),int(arguments[0][4:6]),int(arguments[0][6:8]))
        enddate= datetime.date(int(arguments[1][0:4]),int(arguments[1][4:6]),int(arguments[1][6:8]))
    except:
        pass

    exchange_rates_download(startdate,enddate)