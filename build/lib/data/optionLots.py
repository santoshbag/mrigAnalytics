# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 17:20:53 2019

@author: Santosh Bag
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from requests import get
from io import BytesIO
from zipfile import ZipFile
import pandas as pd
import mrigutilities as mu
import csv
import re


def optionLot_download():
    #"https://www.nseindia.com/content/historical/DERIVATIVES/2019/MAR/fo03MAR2019bhav.csv.zip"
    bhavcopy = "https://www1.nseindia.com/content/fo/fo_mktlots.csv"    

    engine = mu.sql_engine()
    request = get(bhavcopy)
    
    content = request.content.decode('utf-8')
    
    cr = csv.reader(content.splitlines(), delimiter=',')
    my_list = list(cr)
    print(my_list)
    sql = "insert into futures_option_lots values "
    for row in my_list:
        if row[1].strip() not in ['Symbol','SYMBOL']:
            sql = sql + "('%s','%s'),"%(row[1].strip(),row[2].strip())
    sql = sql.strip()[:-1] + " ON CONFLICT ON CONSTRAINT futures_option_lots_pkey DO UPDATE SET \
                     lot=EXCLUDED.lot"   
    engine.execute(sql)
if __name__ == '__main__':
    optionLot_download()