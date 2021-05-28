# -*- coding: utf-8 -*-
"""
Created on Thu Dec 27 11:51:58 2018

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import csv
import nsepy
import strategies.stocks as st
import datetime #import date, timedelta
from pandas import DataFrame
from sqlalchemy import create_engine
import mrigutilities as mu
from concurrent.futures import ThreadPoolExecutor as Executor
from time import sleep

#mfISINList_path = "F:\Mrig Analytics\Development\mrigAnalytics\\tempdata.csv"
#stklist = []
#with open(mfISINList_path, 'r') as csvfile:
#    sl = csv.reader(csvfile)
#    for row in sl:
#        stklist.append(row[0])
#def oc_download():
#    print("Stock Option Chains download started")
#    stocks = [key for key in nsepy.constants.symbol_list]
#    
#    engine = mu.sql_engine()
#    
#    today = datetime.date.today()
#    counter = 0
#    for stock in stocks:
#        counter = counter + 1
#        
#        """ Progress Animation routine starts"""
#        if len(stocks) < 50:
#            steps = len(stocks)
#        else:
#            steps = 50
#        sys.stdout.write("\r[%-*s] %d%%" % (steps,'='*int(counter/(len(stocks)/steps)), int(100/len(stocks)*counter)))
#        sys.stdout.flush()
#        """ Progress Animation routine ends"""    
#        
#        try:
#            stk = st.Stock(stock)
#            oc = stk.optionChain()
#            if not oc.empty:
#                oc = oc.reset_index()
#                oc = oc.to_string()
#                sql = "insert into option_chain_history (date,symbol,oc) values ('%s','%s','%s')"
#                sql = (sql %(today.strftime('%Y-%m-%d'),stock,oc))
#                try:
#                    engine.execute(sql)
#                except:
#                    pass
#        except:
#            pass    
#    print("Stock Option Chains download finished\n")

def oc_download(stock):
    timecounter = 0
    print(stock,end = ' ')
    while True:
        stk = st.Stock(stock)
        timecounter = timecounter + 1
        if mu.is_connected():
            oc = stk.optionChain()
            print("OC is")
            print(oc)
        if mu.is_connected() or timecounter > 5:
            break
        else:
            sleep(60)
    today = datetime.date.today()
    engine = mu.sql_engine()
    if not oc.empty:
        oc = oc.reset_index()
        oc = oc.to_string()
        sql = "insert into option_chain_history (date,symbol,oc) values ('%s','%s','%s')"
        sql = (sql %(today.strftime('%Y-%m-%d'),stock,oc))
        try:
            engine.execute(sql)
        except:
            pass

        return stock
    else:
        return None

def index_oc_download(stock):
    timecounter = 0
    while True:
        stk = st.Index(stock)
        timecounter = timecounter + 1
        if mu.is_connected():
            oc = stk.optionChain()
        if mu.is_connected() or timecounter > 5:
            break
        else:
            sleep(60)
    today = datetime.date.today()
    engine = mu.sql_engine()
    if not oc.empty:
        oc = oc.reset_index()
        oc = oc.to_string()
        sql = "insert into option_chain_history (date,symbol,oc) values ('%s','%s','%s')"
        sql = (sql %(today.strftime('%Y-%m-%d'),stock,oc))
        try:
            engine.execute(sql)
        except:
            pass

        return stock
    else:
        return None

def oc_download_all(progressbar=True):
    print("Stock Option Chains download started")
    stocks = [key for key in nsepy.constants.symbol_list]
    count,stkcount = 0,0
    with Executor(max_workers=5) as exe:
        jobs = [exe.submit(oc_download,stock) for stock in stocks]
        results = [job.result() for job in jobs]
        for result in results:
            stkcount = stkcount + 1
            """ Progress Animation routine starts"""
            if len(results) < 50:
                steps = len(results)
            else:
                steps = 50
            if progressbar:
                sys.stdout.write("\r[%-*s] %d%%" % (steps,'='*int(stkcount/(len(results)/steps)), int(100/len(results)*stkcount)))
                sys.stdout.flush()        
            """ Progress Animation routine ends"""

            if result != None:
                count = count + 1
    index_oc_download('NIFTY 50')
    print("Downloaded "+str(count)+" OCs out of "+str(len(stocks))+" stocks")
    print("Stock Option Chains download finished \n")

#def oc_download_all():
#    print("Stock Option Chains download started")
#    stocks = [key for key in nsepy.constants.symbol_list]
#    count = 0
#    with Executor(max_workers=5) as exe:
#        jobs = [exe.submit(oc_download,stock) for stock in stocks]
#        results = []
#        counter = 0
#        for job in jobs:
#            counter = counter + 1
#            """ Progress Animation routine starts"""
#            if len(jobs) < 50:
#                steps = len(jobs)
#            else:
#                steps = 50
#            sys.stdout.write("\r[%-*s] %d%%" % (steps,'='*int(counter/(len(jobs)/steps)), int(100/len(jobs)*counter)))
#            sys.stdout.flush()
#            """ Progress Animation routine ends"""    
#
#            results.append(job.result())
##        results = [job.result() for job in jobs]
#        for result in results:
#            if result != None:
#                count = count + 1
#    print("Downloaded "+str(count)+" OCs out of "+str(len(stocks))+" stocks")
#    print("Stock Option Chains download finished \n")


#        
if __name__ == '__main__':
    oc_download('SBIN')
#    oc_download_all()
