# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 11:22:01 2023

@author: Santosh Bag
"""

import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import datetime  # import date, timedelta
import pandas as pd  # import DataFrame
# from sqlalchemy import create_engine
import mrigutilities
import zipfile, re
import yfinance as yf
# from bs4 import BeautifulSoup
# from time import sleep
import csv
import research.screener_TA as sta

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from PIL import Image, ImageTk

from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QHeaderView

import kite.kite_account as ka

# today = datetime.date.today()
today = datetime.datetime.now()

col_map = {'Instrument': 'instrument', 'Qty.': 'qty', 'Avg.': 'avg_price', 'LTP': 'ltp', 'P&L': 'pnl'}

pos_cols = ['Scrip', 'Instrument', 'LongShort', 'Quantity', 'Orig Liability', 'Curr Liability', 'Delta', 'Theta', 'PnL']

class tradingDB():

    kite_object = None
    engine= None

    def __init__(self):
        self.kite_object = ka.kite_account()
        self.engine = mrigutilities.sql_engine()

    def price(self,scrip):
        price = None
        yahoo_map = {'NIFTY': '^NSEI', 'BANKNIFTY': '^NSEBANK'}
        yahooid = scrip + '.NS'
        if (scrip == 'NIFTY' or scrip == 'BANKNIFTY'):
            yahooid = yahoo_map[scrip]
        if len(yahooid) > 0:
            if yahooid is not None:
                try:
                    price = yf.download(yahooid, period='1d').Close.values[0]
                except:
                    None

        return price


    def __num_pos(self,s):
        return re.search(r"\d", s).start()


    def load_DB(self,flag=True, diagnostic=False):
        filename = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])

        if filename != None:

            positions = pd.read_csv(filename)
            positions = positions[positions['Product'] == 'NRML']
            positions['type'] = positions['Instrument'].apply(lambda x: x[-2:])
            positions['type'] = positions['type'].apply(lambda x: 'FUT' if (x == 'UT') else x)
            positions['scrip'] = positions['Instrument'].apply(lambda x: x[:self.__num_pos(x)])
            positions['strike'] = positions['Instrument'].apply(lambda x: x[self.__num_pos(x) + 5:-2])
            positions['strike'] = positions['strike'].apply(lambda x: 0 if (x == 'F') else x)
            positions['expiry'] = positions['Instrument'].apply(
                lambda x: datetime.datetime.strptime(x[self.__num_pos(x):self.__num_pos(x) + 5] + '27', '%y%b%d'))
            positions.drop(columns=['Chg.', 'Product'], inplace=True)
            positions.rename(columns=col_map, inplace=True)
            positions['pos_date'] = today
            positions['snapshot'] = int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

            if diagnostic:
                print(positions)

            write_flag = flag

            if write_flag:
                positions.to_sql('live_positions', self.engine, index=False, if_exists='append')


    def showAnalytics(self):
        def highlight(s):
            if s.l_s == '':
                return ['background-color: yellow'] * len(s)
            else:
                return ['background-color: white'] * len(s)

        volfile = 'vol.csv'
        vol_pd = pd.read_csv(volfile)
        vol_pd.drop(columns=['Date', 'Underlying Close Price (A)', 'Underlying Previous Day Close Price (B)',
                             'Underlying Log Returns (C) = LN(A/B)', 'Previous Day Underlying Volatility (D)'],
                    inplace=True)
        vol_pd.set_index('Symbol', inplace=True)
        vol_pd.rename(columns={'Underlying Annualised Volatility (F) = E*Sqrt(365)': 'vol'}, inplace=True)
        hist_vol = vol_pd.to_dict()

        hist_vol = hist_vol['vol']

        hist_vol['NIFTY'] = 0.09
        hist_vol['BANKNIFTY'] = 0.14
        sql = 'select * from live_positions where snapshot = \
        (select snapshot from live_positions where pos_date = \
        (select pos_date from live_positions order by pos_date desc limit 1)\
        order by snapshot desc limit 1)'

        positions = pd.read_sql(sql, self.engine)
        positions['l_s'] = positions[['type', 'qty']].apply(lambda x: 'Short' if (
                    ((x['type'] == 'CE' or x['type'] == 'FUT') and x['qty'] < 0) or (
                        x['type'] == 'PE' and x['qty'] > 0)) else 'Long', axis=1)

        positions['orig_liab'] = positions[['type', 'qty', 'avg_price']].apply(
            lambda x: x['qty'] * x['avg_price'] if (x['qty'] < 0 and x['type'] != 'FUT') else 0, axis=1)
        positions['curr_liab'] = positions[['type', 'qty', 'ltp']].apply(
            lambda x: x['qty'] * x['ltp'] if (x['qty'] < 0 and x['type'] != 'FUT') else 0, axis=1)
        positions['max_profit'] = positions['orig_liab'].apply(lambda x: -x if (x < 0) else 'infinite')

        positions['max_loss'] = positions[['type', 'qty', 'avg_price', 'orig_liab']].apply(
            lambda x: -x['qty'] * x['avg_price'] if (x['orig_liab'] == 0 and x['type'] != 'FUT') else 'infinite', axis=1)
        positions['spot'] = positions['scrip'].apply(lambda x: self.price(x))
        positions['histVol'] = positions['scrip'].apply(lambda x: float(hist_vol[x]))

        positions['impVol'] = -1
        positions['impVol'] = positions[['type', 'spot', 'strike', 'expiry', 'ltp']].apply(
            lambda x: mrigutilities.impVol(x['spot'], x['strike'], abs((x['expiry'] - today).days) / 365, x['ltp'],
                                           opt=x['type']), axis=1)
        positions['impVol'] = positions[['impVol', 'histVol']].apply(
            lambda x: x['histVol'] if (x['impVol'] == -1) else x['impVol'], axis=1)
        positions['delta'] = positions[['type', 'qty', 'spot', 'strike', 'expiry', 'impVol']].apply(
            lambda x: x['qty'] * mrigutilities.bs_delta(x['spot'], x['strike'], abs((x['expiry'] - today).days) / 365,
                                                        x['impVol'], opt=x['type']), axis=1)
        positions['theta'] = positions[['type', 'qty', 'spot', 'strike', 'expiry', 'impVol']].apply(
            lambda x: x['qty'] * mrigutilities.bs_theta(x['spot'], x['strike'], abs((x['expiry'] - today).days) / 365,
                                                        x['impVol'], opt=x['type']), axis=1)
        positions['theta/delta'] = positions[['qty', 'delta', 'theta']].apply(
            lambda x: abs(x['theta'] / x['delta']) if (x['delta'] != 0 and x['qty'] < 0) else 0, axis=1)

        df1 = positions.groupby(by=['scrip', 'instrument', 'l_s'], as_index=False)[
            'qty', 'strike', 'orig_liab', 'curr_liab', 'delta', 'theta', 'theta/delta', 'pnl'].sum().fillna(0).round()

        df2 = df1.groupby(by=['scrip', 'l_s'], as_index=False)[
            'qty', 'strike', 'orig_liab', 'curr_liab', 'delta', 'theta', 'theta/delta', 'pnl'].sum().fillna(
            0).round().assign(instrument='')

        df3 = df1.groupby(by=['scrip'], as_index=False)[
            'qty', 'strike', 'orig_liab', 'curr_liab', 'delta', 'theta', 'theta/delta', 'pnl'].sum().fillna(
            0).round().assign(l_s='')

        df = (pd.concat([df1, df3])
              .reindex(df1.columns, axis=1)
              .fillna('')
              .sort_values(['scrip', 'l_s'], ascending=True, ignore_index=True))
        # df.set_index('scrip',inplace=True)
        # print(positions.groupby(by=['scrip']).sum()[['qty','orig_liab','curr_liab','delta','theta','pnl']])

        return [positions, df]


    def showAnalytics_live(self):
        def highlight(s):
            if s.l_s == '':
                return ['background-color: yellow'] * len(s)
            else:
                return ['background-color: white'] * len(s)

        volfile = 'vol.csv'
        vol_pd = pd.read_csv(volfile)
        vol_pd.drop(columns=['Date', 'Underlying Close Price (A)', 'Underlying Previous Day Close Price (B)',
                             'Underlying Log Returns (C) = LN(A/B)', 'Previous Day Underlying Volatility (D)'],
                    inplace=True)
        vol_pd.set_index('Symbol', inplace=True)
        vol_pd.rename(columns={'Underlying Annualised Volatility (F) = E*Sqrt(365)': 'vol'}, inplace=True)
        hist_vol = vol_pd.to_dict()

        hist_vol = hist_vol['vol']

        hist_vol['NIFTY'] = 0.09
        hist_vol['BANKNIFTY'] = 0.14

        live_positions = self.kite_object.getPositions()
        # print(live_positions)

        positions = live_positions.loc[live_positions['exchange'] == 'NFO',
            ['tradingsymbol', 'instrument_token', 'product', 'quantity', 'average_price', 'last_price', 'pnl']]
        positions.rename(columns={'tradingsymbol': 'Instrument',
                                  'quantity': 'qty',
                                  'average_price': 'avg_price',
                                  'last_price': 'ltp'}, inplace=True)
        positions['type'] = positions['Instrument'].apply(lambda x: x[-2:])
        positions['type'] = positions['type'].apply(lambda x: 'FUT' if (x == 'UT') else x)
        positions['scrip'] = positions['Instrument'].apply(lambda x: x[:self.__num_pos(x)])
        positions['strike'] = positions['Instrument'].apply(lambda x: x[self.__num_pos(x) + 5:-2])
        positions['strike'] = positions['strike'].apply(lambda x: 0 if (x == 'F') else x)
        positions['strike'] = pd.to_numeric(positions['strike'], errors='ignore')
        positions['expiry'] = positions['Instrument'].apply(
            lambda x: datetime.datetime.strptime(x[self.__num_pos(x):self.__num_pos(x) + 5] + '27', '%y%b%d'))
        # positions.drop(columns=['Chg.', 'Product'], inplace=True)
        positions.rename(columns=col_map, inplace=True)
        positions['pos_date'] = today

        # positions = pd.read_sql(sql, engine)
        positions['l_s'] = positions[['type', 'qty']].apply(lambda x: 'Short' if (
                ((x['type'] == 'CE' or x['type'] == 'FUT') and x['qty'] < 0) or (
                x['type'] == 'PE' and x['qty'] > 0)) else 'Long', axis=1)

        positions['orig_liab'] = positions[['type', 'qty', 'avg_price']].apply(
            lambda x: x['qty'] * x['avg_price'] if (x['qty'] < 0 and x['type'] != 'FUT') else 0, axis=1)
        positions['curr_liab'] = positions[['type', 'qty', 'ltp']].apply(
            lambda x: x['qty'] * x['ltp'] if (x['qty'] < 0 and x['type'] != 'FUT') else 0, axis=1)
        positions['max_profit'] = positions['orig_liab'].apply(lambda x: -x if (x < 0) else 'infinite')

        positions['max_loss'] = positions[['type', 'qty', 'avg_price', 'orig_liab']].apply(
            lambda x: -x['qty'] * x['avg_price'] if (x['orig_liab'] == 0 and x['type'] != 'FUT') else 'infinite', axis=1)
        positions['spot'] = positions['scrip'].apply(lambda x: self.price(x))
        positions['histVol'] = positions['scrip'].apply(lambda x: float(hist_vol[x]))

        positions['impVol'] = -1
        positions['impVol'] = positions[['type', 'spot', 'strike', 'expiry', 'ltp']].apply(
            lambda x: mrigutilities.impVol(x['spot'], x['strike'], abs((x['expiry'] - today).days) / 365, x['ltp'],
                                           opt=x['type']), axis=1)
        positions['impVol'] = positions[['impVol', 'histVol']].apply(
            lambda x: x['histVol'] if (x['impVol'] == -1) else x['impVol'], axis=1)
        positions['delta (D)'] = positions[['type', 'qty', 'spot', 'strike', 'expiry', 'impVol']].apply(
            lambda x: x['qty'] * mrigutilities.bs_delta(x['spot'], x['strike'], abs((x['expiry'] - today).days) / 365,
                                                        x['impVol'], opt=x['type']), axis=1)
        positions['theta (T)'] = positions[['type', 'qty', 'spot', 'strike', 'expiry', 'impVol']].apply(
            lambda x: x['qty'] * mrigutilities.bs_theta(x['spot'], x['strike'], abs((x['expiry'] - today).days) / 365,
                                                        x['impVol'], opt=x['type']), axis=1)
        positions['T/D'] = positions[['qty', 'delta (D)', 'theta (T)']].apply(
            lambda x: abs(x['theta (T)'] / x['delta (D)']) if (x['delta (D)'] != 0 and x['qty'] < 0) else 0, axis=1)

        positions['strike'] = positions['strike'].map('{:,.0f}'.format)
        df1 = positions.groupby(by=['scrip', 'instrument', 'l_s', 'strike'], as_index=False)[
            'qty', 'orig_liab', 'curr_liab', 'delta (D)', 'theta (T)', 'T/D', 'pnl'].sum().fillna(0).round()

        # df2 = df1.groupby(by=['scrip', 'l_s'], as_index=False)[
        #     'qty', 'strike', 'orig_liab', 'curr_liab', 'delta (D)', 'theta (T)', 'T/D', 'pnl'].sum().fillna(
        #     0).round().assign(instrument='')

        df3 = df1.groupby(by=['scrip'], as_index=False)[
            'qty', 'orig_liab', 'curr_liab', 'delta (D)', 'theta (T)', 'T/D', 'pnl'].sum().fillna(
            0).round().assign(l_s='')

        df = (pd.concat([df1, df3])
              .reindex(df1.columns, axis=1)
              .fillna('')
              .sort_values(['scrip', 'l_s'], ascending=True, ignore_index=True))
        # df.set_index('scrip',inplace=True)
        # print(positions.groupby(by=['scrip']).sum()[['qty','orig_liab','curr_liab','delta','theta','pnl']])

        # df.loc[df['l_s'] == '',['strike']] = ''
        # for col in ['qty', 'orig_liab', 'curr_liab', 'delta (D)', 'theta (T)', 'T/D', 'pnl']:
        #     df[col] = df[col].map('{:,.0f}'.format)

        return [positions, df]




    def showDB(self,flag=False, diagnostic=False):
        today = datetime.date.today()
        engine = mrigutilities.sql_engine()

        col_map = {'Instrument': 'instrument', 'Qty.': 'qty', 'Avg.': 'avg_price', 'LTP': 'ltp', 'P&L': 'pnl'}
        file = 'positions.csv'
        positions = pd.read_csv(file)
        positions = positions[positions['Product'] == 'NRML']
        positions['type'] = positions['Instrument'].apply(lambda x: x[-2:])
        positions['type'] = positions['type'].apply(lambda x: 'FUT' if (x == 'UT') else x)
        positions['scrip'] = positions['Instrument'].apply(lambda x: x[:self.__num_pos(x)])
        positions['strike'] = positions['Instrument'].apply(lambda x: x[self.__num_pos(x) + 5:-2])
        positions['strike'] = positions['strike'].apply(lambda x: 0 if (x == 'F') else x)
        positions['expiry'] = positions['Instrument'].apply(
            lambda x: datetime.datetime.strptime(x[self.__num_pos(x):self.__num_pos(x) + 5] + '27', '%y%b%d'))
        positions.drop(columns=['Chg.', 'Product'], inplace=True)
        positions.rename(columns=col_map, inplace=True)
        positions['pos_date'] = today
        positions['snapshot'] = int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

        if diagnostic:
            print(positions)

        write_flag = flag

        if write_flag:
            positions.to_sql('live_positions', engine, index=False, if_exists='append')

        def price(scrip):
            price = None
            yahoo_map = {'NIFTY': '^NSEI', 'BANKNIFTY': '^NSEBANK'}
            yahooid = scrip + '.NS'
            if (scrip == 'NIFTY' or scrip == 'BANKNIFTY'):
                yahooid = yahoo_map[scrip]
            if len(yahooid) > 0:
                if yahooid is not None:
                    try:
                        price = yf.download(yahooid, period='1d').Close.values[0]
                    except:
                        None

            return price

        def highlight(s):
            if s.l_s == '':
                return ['background-color: yellow'] * len(s)
            else:
                return ['background-color: white'] * len(s)

        volfile = 'vol.csv'
        vol_pd = pd.read_csv(volfile)
        vol_pd.drop(columns=['Date', 'Underlying Close Price (A)', 'Underlying Previous Day Close Price (B)',
                             'Underlying Log Returns (C) = LN(A/B)', 'Previous Day Underlying Volatility (D)'],
                    inplace=True)
        vol_pd.set_index('Symbol', inplace=True)
        vol_pd.rename(columns={'Underlying Annualised Volatility (F) = E*Sqrt(365)': 'vol'}, inplace=True)
        hist_vol = vol_pd.to_dict()

        hist_vol = hist_vol['vol']

        hist_vol['NIFTY'] = 0.09
        hist_vol['BANKNIFTY'] = 0.14
        sql = 'select * from live_positions where snapshot = \
        (select snapshot from live_positions where pos_date = \
        (select pos_date from live_positions order by pos_date desc limit 1)\
        order by snapshot desc limit 1)'

        positions = pd.read_sql(sql, engine)
        positions['l_s'] = positions[['type', 'qty']].apply(lambda x: 'Short' if (
                    ((x['type'] == 'CE' or x['type'] == 'FUT') and x['qty'] < 0) or (
                        x['type'] == 'PE' and x['qty'] > 0)) else 'Long', axis=1)

        positions['orig_liab'] = positions[['type', 'qty', 'avg_price']].apply(
            lambda x: x['qty'] * x['avg_price'] if (x['qty'] < 0 and x['type'] != 'FUT') else 0, axis=1)
        positions['curr_liab'] = positions[['type', 'qty', 'ltp']].apply(
            lambda x: x['qty'] * x['ltp'] if (x['qty'] < 0 and x['type'] != 'FUT') else 0, axis=1)
        positions['max_profit'] = positions['orig_liab'].apply(lambda x: -x if (x < 0) else 'infinite')

        positions['max_loss'] = positions[['type', 'qty', 'avg_price', 'orig_liab']].apply(
            lambda x: -x['qty'] * x['avg_price'] if (x['orig_liab'] == 0 and x['type'] != 'FUT') else 'infinite', axis=1)
        positions['spot'] = positions['scrip'].apply(lambda x: price(x))
        positions['histVol'] = positions['scrip'].apply(lambda x: float(hist_vol[x]))

        positions['impVol'] = -1
        positions['impVol'] = positions[['type', 'spot', 'strike', 'expiry', 'ltp']].apply(
            lambda x: mrigutilities.impVol(x['spot'], x['strike'], abs((x['expiry'] - today).days) / 365, x['ltp'],
                                           opt=x['type']), axis=1)
        positions['impVol'] = positions[['impVol', 'histVol']].apply(
            lambda x: x['histVol'] if (x['impVol'] == -1) else x['impVol'], axis=1)
        positions['delta'] = positions[['type', 'qty', 'spot', 'strike', 'expiry', 'impVol']].apply(
            lambda x: x['qty'] * mrigutilities.bs_delta(x['spot'], x['strike'], abs((x['expiry'] - today).days) / 365,
                                                        x['impVol'], opt=x['type']), axis=1)
        positions['theta'] = positions[['type', 'qty', 'spot', 'strike', 'expiry', 'impVol']].apply(
            lambda x: x['qty'] * mrigutilities.bs_theta(x['spot'], x['strike'], abs((x['expiry'] - today).days) / 365,
                                                        x['impVol'], opt=x['type']), axis=1)

        df1 = positions.groupby(by=['scrip', 'instrument', 'l_s'], as_index=False)[
            'qty', 'orig_liab', 'curr_liab', 'delta', 'theta', 'pnl'].sum().fillna(0).round()

        df2 = df1.groupby(by=['scrip', 'l_s'], as_index=False)[
            'qty', 'orig_liab', 'curr_liab', 'delta', 'theta', 'pnl'].sum().fillna(0).round().assign(instrument='')

        df3 = df1.groupby(by=['scrip'], as_index=False)[
            'qty', 'orig_liab', 'curr_liab', 'delta', 'theta', 'pnl'].sum().fillna(0).round().assign(l_s='')

        df = (pd.concat([df1, df3])
              .reindex(df1.columns, axis=1)
              .fillna('')
              .sort_values(['scrip', 'l_s'], ascending=True, ignore_index=True))
        # df.set_index('scrip',inplace=True)
        # print(positions.groupby(by=['scrip']).sum()[['qty','orig_liab','curr_liab','delta','theta','pnl']])

        if diagnostic:
            print(df)
        return positions




