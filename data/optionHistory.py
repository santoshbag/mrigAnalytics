# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 18:23:17 2019

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from requests import get
from io import BytesIO
from zipfile import ZipFile
import pandas as pd
import mrigutilities as mu
import datetime
import re
import csv 

symbol_map = {'NIFTY' : 'NIFTY 50'}

def optionHistory_download(eod=None):
    #"https://www.nseindia.com/content/historical/DERIVATIVES/2019/MAR/fo03MAR2019bhav.csv.zip"
    bhavcopy = "https://www.nseindia.com/content/historical/DERIVATIVES/%s/%s/fo%sbhav.csv.zip"
    if not eod:
        today = datetime.date.today()
    else:
        today = eod
    
    engine = mu.sql_engine()
    request = get(bhavcopy%(today.strftime('%Y'),today.strftime('%b').upper(),today.strftime('%d%b%Y').upper()))
    if not (re.match(r'(4..)',str(request.status_code)) or re.match(r'(5..)',str(request.status_code))):
        zip_file = ZipFile(BytesIO(request.content))
        files = zip_file.namelist()
        options = []
        options_headers = ['instrument','symbol','expiry','strike','option_type','open','high','low','close','settle_price','contracts','val_inlakh','oi','oi_change','date']
        
        
        for line in zip_file.open(files[0]).readlines():
        #    print(line.decode('utf-8'))
            options.append(line.decode('utf-8').split(',')[:-1])
            try:
                options[1] = symbol_map[options[1]]
            except:
                pass
        
        if len(options) > 0:
            options = pd.DataFrame(options[1:],columns=options_headers)
            options.drop('val_inlakh',axis=1, inplace=True)
            
            options.to_sql('futures_options_history',engine,if_exists='append', index=False)
            print("Option/Futures History downloaded")
    else:
        print("No File")
        
def optionLot_download():
    #"https://www.nseindia.com/content/historical/DERIVATIVES/2019/MAR/fo03MAR2019bhav.csv.zip"
    bhavcopy = "https://www.nseindia.com/content/fo/fo_mktlots.csv"    

    engine = mu.sql_engine()
    request = get(bhavcopy)
    
    content = request.content.decode('utf-8')
        
    cr = csv.reader(content.splitlines(), delimiter=',')
    my_list = list(cr)
    sql = "insert into futures_option_lots values "
    for row in my_list:
        if row[1].strip() not in ['Symbol','SYMBOL']:
            sql = sql + "('%s','%s'),"%(row[1].strip(),row[2].strip())
    sql = sql.strip()[:-1] + " ON CONFLICT ON CONSTRAINT futures_option_lots_pkey DO UPDATE SET \
                     lot=EXCLUDED.lot"   
    engine.execute(sql)
    
if __name__ == '__main__':
    optionHistory_download()
    optionLot_download()