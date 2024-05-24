# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 12:13:17 2023

@author: Santosh Bag
"""

# from kite_trade import *
import sys, os
import pandas as pd
import pandas_ta as ta
import json
import mrigutilities as mu
import time,datetime,pytz
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class kite_account:

    session = None

    def __init__(self):
        self.session = None #mu.getKiteSession()

    def getKiteSession(self):
        return self.session

    def setKiteSession(self):
        session = mu.getKiteSession()

    def getStatus(self):
        if self.session is not None:
            return 1
        else:
            return 0

    def kiteLogin(self,token):
        engine = mu.sql_engine()

        sql = "update auth set token='"+token+"' where vendor='zerodha'"
        engine.execute(sql)
        self.session = mu.getKiteSession()

    def getInstruments(self,exchange):
        instruments = self.session.instruments(exchange=exchange)
        return pd.DataFrame(instruments)

    def getPositions(self):
        positions = self.session.positions()

        positions = pd.DataFrame(positions['net'])

        # print(positions.columns)
        # print(positions.head(1).to_string())
        return positions

    def getQuoteLive(self,scrip):
        sec = scrip
        if scrip == 'NIFTY':
            sec = 'NIFTY 50'
        elif scrip == 'BANKNIFTY':
            sec = 'NIFTY BANK'
        return pd.DataFrame(self.session.quote('NSE:'+sec))['NSE:'+sec]

    def getHistorical(self,token,from_date,to_date,interval):
        data = self.session.historical_data(token,from_date,to_date,interval)
        return pd.DataFrame(data)