# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 20:49:38 2018

@author: Santosh Bag
"""

import sys
import requests
import datetime #import date, timedelta
from pandas import DataFrame
from bs4 import BeautifulSoup

import mrigutilities

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

print(WTI)
print(BRENT)
print(dates)

#sql = "INSERT INTO crudeoil_prices (value_date, crude_benchmark, price, download_date) VALUES "\
#       + "( '"+date+"','WTI','"+WTI+"','"+today.strftime('%Y-%m-%d')+"'), " \
#       + "( '"+date+"','BRENT','"+BRENT+"','"+today.strftime('%Y-%m-%d')+"')"
#       
#engine.execute(sql)