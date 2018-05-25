# -*- coding: utf-8 -*-
"""
Created on Thu May 24 14:41:11 2018

@author: Santosh Bag

This module downloads yield curves for different currencies.
"""

import urllib,csv,requests
import datetime,pandas
from bs4 import BeautifulSoup
import mrigstatics

def get_yieldCurve(currency="INR"):
    
    s = requests.Session()
    response = s.get(mrigstatics.WGB_YIELD_URL[currency])
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    curve_date = str(soup.find_all('p')[0].find_all(class_='w3-small')[0].text).replace('Last Update: ',"").replace(' GMT+2',"").split(" ")
    curve_date = curve_date[0]+"-"+curve_date[1]+"-"+curve_date[2]
    curve_date = datetime.datetime.strptime(curve_date,'%d-%b-%Y' )
    tables = soup.find_all(class_="w3-table w3-bordered w3-border table-padding-xsmall w3-small font-family-arial")
    
    yield_table = []
    price_table = []
    
    yield_heads = tables[2].find_all('th')
    yield_table_cols = [col.text for col in yield_heads]
    
    for row in tables[2].find_all('tr'):
        cells = row.find_all('td')
        yield_table.append([str(cell.text).strip() for cell in cells][1:-1])
    
    price_heads = tables[3].find_all('th')
    price_table_cols = [col.text for col in price_heads]
    price_table_cols.pop(3)
    
    
    for row in tables[3].find_all('tr'):
        cells = row.find_all('td')
        price_table.append([str(cell.text).strip() for cell in cells][1:])    

    for items in yield_table:
        if items == []:
            yield_table.remove(items)
    
    for items in price_table:
        if items == []:
            price_table.remove(items)
            
    yield_tables = pandas.DataFrame(yield_table,columns=yield_table_cols[1:-1])
    price_tables = pandas.DataFrame(price_table[1:-1],columns=price_table_cols[1:])
    
    YC = {'Yield' : yield_tables,
          'Price' : price_tables}
    s.close()
    return YC