# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 20:16:07 2017

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from nsetools import Nse

nseStockList = open("nseStockList.txt","r")
nseStockPrices = open("nseStockPrices.txt","w+")

nsePrices = Nse()

stocks = [line.split("\n")[0] for line in nseStockList]

for stock in stocks:
    #print(stock)
    try:
        q = nsePrices.get_quote(stock)
        lastPrice = q.get('lastPrice')
        previousClose = q.get('previousClose')
        date = q.get('secDate')
        pChange = lastPrice/previousClose -1 
        #print(previousClose)
        priceLine = stock + "," + str(lastPrice) + "," + str(previousClose) + "," + str(pChange) + "," +date +"\r"
        #print(priceLine)
        nseStockPrices.write(priceLine)
    except:
        pass

nseStockPrices.close()


