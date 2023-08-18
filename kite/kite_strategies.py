# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 12:13:17 2023

@author: Santosh Bag
"""

from kite_trade import *
import pandas as pd
import pandas_ta as ta
import json
import time,datetime,pytz
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf


file = open('settings.json')
enctoken = json.load(file)
token = enctoken["encauth"]
session = KiteApp(enctoken=token)

kite_instruments = json.load(open("settings.json"))
kite_instruments_df = pd.DataFrame(kite_instruments['kite_instruments'])

positions = session.positions()

columnmap = {'MACD_12_26_9': 'Macd',
             'MACDh_12_26_9': 'Macd_h',
             'MACDs_12_26_9': 'Macd_s',
             'SUPERT_7_3.0': 'Supertrend',
             'BBL_20_2.0': 'BB_l',
             'BBM_20_2.0': 'BB_m',
             'BBU_20_2.0': 'BB_u',
             'STOCHRSIk_14_14_3_3': 'sRSI_k',
             'STOCHRSId_14_14_3_3': 'sRSI_d'}


             # df = pd.DataFrame.from_dict(pd.json_normalize(positions), orient='columns')
# pos = pd.DataFrame.from_dict(pd.json_normalize(df['net'][0]), orient='columns')
# # pos.to_csv('live_pos.csv')
# print(pos)

counter=100
five_min_candles = pd.DataFrame()

scrips = ['NIFTY 50',
          'NIFTY BANK']

lookback_days = 90
today = datetime.datetime.now()
from_d = today- datetime.timedelta(days = lookback_days)
interval = '5minute'

print(scrips[1])
hist_data = session.historical_data(8963586, from_d, today, interval='5minute')
for pr in hist_data:
    five_min_candles.loc[pd.to_datetime(pr['date']),['open','high','low','close','volume']] = [pr['open'],pr['high'],pr['low'],pr['close'],pr['volume']]
# price_data.sort_index()
# print(price_data.tail(4))

# price_data1 = price_data['close']
# print(price_data1)
    macd = ta.macd(five_min_candles['close'])
    supertrend = ta.supertrend(five_min_candles['high'], five_min_candles['low'], five_min_candles['close'], period=7, multiplier=3)
    bb = ta.bbands(five_min_candles['close'], length=20, std=2)
    stocRSI = ta.stochrsi(five_min_candles['close'])

    five_min_candles = pd.merge(five_min_candles, supertrend['SUPERT_7_3.0'], left_index=True, right_index=True)
    five_min_candles = pd.merge(five_min_candles, macd, left_index=True, right_index=True)
    five_min_candles = pd.merge(five_min_candles, bb[['BBL_20_2.0', 'BBM_20_2.0', 'BBU_20_2.0']], left_index=True, right_index=True)
    five_min_candles = pd.merge(five_min_candles, stocRSI[['STOCHRSIk_14_14_3_3', 'STOCHRSId_14_14_3_3']], left_index=True, right_index=True)
    # mpf.plot(price_data, type='candle', style='yahoo', title='Five-Minute Candles')
    five_min_candles.rename(columnmap, axis=1, inplace=True)
    # five_min_candles.loc[(five_min_candles['close'] > five_min_candles['Supertrend']) & (five_min_candles['Macd'] > five_min_candles['Macd_s']) , ['action']] = 'BUY'
    # five_min_candles.loc[(five_min_candles['close'] < five_min_candles['Supertrend']) & (five_min_candles['Macd'] < five_min_candles['Macd_s']) , ['action']] = 'SELL'
    #
    # five_min_candles.loc[(five_min_candles['Macd_h'] > 1) , ['action']] = 'BUY'
    # five_min_candles.loc[(five_min_candles['Macd_h'] < -1) , ['action']] = 'SELL'

    print(five_min_candles.tail(4)[['close','Supertrend','Macd','Macd_s']])


    time.sleep(1)
    counter = counter -1

# buy_price = -1
# sell_price = -1
# pnl = 0
# long = 1
# # for index, rows in five_min_candles.iterrows():
# #     if long == 1:
# #         if (rows['action'] == 'BUY') and (buy_price == -1):
# #             buy_price = rows['close']
# #             five_min_candles.loc[index,['BP']] = buy_price
# #             sell_price = -1
# #
# #         if (rows['action'] == 'SELL') and (sell_price == -1):
# #             sell_price = rows['close']
# #             five_min_candles.loc[index, ['SP']] = sell_price
# #             pnl = pnl + 15*(sell_price - buy_price)
# #             five_min_candles.loc[index, ['PNL']] = pnl
# #             buy_price = -1
# #             long=0
# # #Short Position
# #     else:
# #         if (rows['action'] == 'SELL') and (sell_price == -1):
# #             sell_price = rows['close']
# #             five_min_candles.loc[index,['SP']] = sell_price
# #             buy_price = -1
# #         if (rows['action'] == 'BUY') and (buy_price == -1):
# #             buy_price = rows['close']
# #             five_min_candles.loc[index, ['BP']] = buy_price
# #             pnl = pnl + 15*(sell_price - buy_price)
# #             five_min_candles.loc[index, ['PNL']] = pnl
# #             sell_price = -1
# #             long=1
#
# for index, rows in five_min_candles.iterrows():
#     if long == 1:
#         if (rows['Macd_h'] == 'BUY') and (buy_price == -1):
#             buy_price = rows['close']
#             five_min_candles.loc[index,['BP']] = buy_price
#             sell_price = -1
#
#         if (rows['action'] == 'SELL') and (sell_price == -1):
#             sell_price = rows['close']
#             five_min_candles.loc[index, ['SP']] = sell_price
#             pnl = pnl + 15*(sell_price - buy_price)
#             five_min_candles.loc[index, ['PNL']] = pnl
#             buy_price = -1
#             long=0
# #Short Position
#     else:
#         if (rows['action'] == 'SELL') and (sell_price == -1):
#             sell_price = rows['close']
#             five_min_candles.loc[index,['SP']] = sell_price
#             buy_price = -1
#         if (rows['action'] == 'BUY') and (buy_price == -1):
#             buy_price = rows['close']
#             five_min_candles.loc[index, ['BP']] = buy_price
#             pnl = pnl + 15*(sell_price - buy_price)
#             five_min_candles.loc[index, ['PNL']] = pnl
#             sell_price = -1
#             long=1
#
# print(pnl)
# five_min_candles.to_csv('backtest.csv')
# print(five_min_candles.tail(50)[['close','Supertrend','action','BP','SP','PNL']])


# print(price_data)
# while counter <= 100:
#     qt = session.quote(["NFO:BANKNIFTY23AUGFUT"])
#     print(qt)
#     price_data.loc[pd.to_datetime(qt["NFO:BANKNIFTY23AUGFUT"]['timestamp']),['last_price']] = qt["NFO:BANKNIFTY23AUGFUT"]['last_price']
#     # print(price_data)
#     five_min_candles = price_data.resample('5T').agg({'last_price': 'ohlc'})
#     print(five_min_candles['last_price'])
#
#
#     counter = counter -1
#     time.sleep(1)

# margins = session.margins()
# print(margins)

# df = pd.DataFrame.from_dict(pd.json_normalize(margins), orient='columns')
# marg = pd.DataFrame.from_dict(pd.json_normalize(df['net'][0]), orient='columns')
# print(df.columns)



# print(orders)