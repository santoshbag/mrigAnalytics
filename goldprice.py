# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 20:02:18 2018

@author: Santosh Bag
"""

import sys
import requests
import datetime #import date, timedelta
from pandas import DataFrame
from bs4 import BeautifulSoup

import mrigutilities

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