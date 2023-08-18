# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 10:46:54 2020

@author: Santosh Bag
"""
import sys
from os.path import isfile, join, dirname
#from sys.path import append 
sys.path.append(join(dirname(__file__), '..'))
import pandas as pd
#from datetime import datetime
from os import listdir
from shutil import move
from mrigutilities import sql_engine


datadir = dirname(__file__)
base = join(datadir, '..', '..', 'data','2020','Futures')  # ''F:\\Mrig Analytics\\Development\\data\\'
print(base)

onlyfiles = [(join(base,f),join(base,'loaded',f)) for f in listdir(base) if isfile(join(base, f))]

engine = sql_engine()
colmap = { 'INSTRUMENT' : 'instrument', 
          'SYMBOL' :  'symbol', 
          'EXPIRY_DT' :  'expiry', 
          'STRIKE_PR' :  'strike', 
          'OPTION_TYP' :  'option_type', 
          'OPEN' :  'open', 
          'HIGH' :  'high', 
          'LOW' :  'low', 
          'CLOSE' :  'close', 
          'SETTLE_PR' :  'settle_price', 
          'CONTRACTS' :  'contracts', 
          'OPEN_INT' :  'oi', 
          'CHG_IN_OI' :  'oi_change', 
          'TIMESTAMP' :  'date'}

for fo_csv in onlyfiles:
    fo_pd = pd.read_csv(fo_csv[0])
    fo_pd = fo_pd[list(colmap.keys())]
    fo_pd = fo_pd.rename(columns=colmap)
    fo_pd.to_sql('option_history', engine, if_exists='append', index=False)
    move(fo_csv[0], fo_csv[1])
