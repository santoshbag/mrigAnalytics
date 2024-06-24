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
import mriggraphics as mg
import zipfile, re
import yfinance as yf
# from bs4 import BeautifulSoup
# from time import sleep
import csv
import research.screener_TA as sta
import numpy as np

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from PIL import Image, ImageTk

from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QHeaderView

# import kite.kite_account as ka
import kite.mrigkite as mk

# today = datetime.date.today()
today = datetime.datetime.now()

col_map = {'Instrument': 'instrument', 'Qty.': 'qty', 'Avg.': 'avg_price', 'LTP': 'ltp', 'P&L': 'pnl'}

pos_cols = ['Scrip', 'Instrument', 'LongShort', 'Quantity', 'Orig Liability', 'Curr Liability', 'Delta', 'Theta', 'PnL']

class tradingDB():

    kite_object = None
    engine= None

    def __init__(self):
        self.kite_object = mk.mrigkite()
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

    def level_analysis(self,scrip):
        m_expiry1 = mrigutilities.last_thursday_of_month(datetime.date.today())
        m_expiry2 = mrigutilities.last_thursday_of_month(m_expiry1 + datetime.timedelta(days=30))
        m_expiry3 = mrigutilities.last_thursday_of_month(m_expiry2 + datetime.timedelta(days=30))
        today = datetime.date.today()
        expiry_list = [m_expiry1, m_expiry2, m_expiry3]

        if ('NIFTY' in scrip):
            days = (3 - today.weekday() + 7) % 7
            expiry1 = today + datetime.timedelta(days=days)
            expiry2 = expiry1 + datetime.timedelta(days=7)
            expiry3 = expiry2 + datetime.timedelta(days=7)
            expiry4 = expiry3 + datetime.timedelta(days=7)
            expiry_list = [expiry1, expiry2, expiry3,expiry4]
            # print(expiry_list)

        if ('BANKNIFTY' in scrip):
            expiry_list = []
            days = (2 - today.weekday() + 7) % 7
            expiry1 = today + datetime.timedelta(days=days)
            expiry_list.append(m_expiry1) if ((m_expiry1 - expiry1).days == 1) else expiry_list.append(expiry1)
            expiry2 = expiry1 + datetime.timedelta(days=7)
            expiry_list.append(m_expiry1) if ((m_expiry1 - expiry2).days == 1) else expiry_list.append(expiry2)
            expiry3 = expiry2 + datetime.timedelta(days=7)
            expiry_list.append(m_expiry1) if ((m_expiry1 - expiry3).days == 1) else expiry_list.append(expiry3)
            # m_expiry = m_expiry1 if ((m_expiry1 - expiry3) == 1) else expiry3
            expiry4 = expiry3 + datetime.timedelta(days=7)
            expiry_list.append(m_expiry1) if ((m_expiry1 - expiry4).days == 1) else expiry_list.append(expiry4)
            # m_expiry = m_expiry1 if ((m_expiry1 - expiry4) == 1) else expiry4
            # expiry_list = [expiry1, expiry2, expiry3,expiry4,m_expiry1]


        # scrip = ['TATAPOWER', 'BANKNIFTY']
        oc = mrigutilities.kite_OC(scrip, expiry_list)
        # print(set(oc['expiry']))
        oc.reset_index(inplace=True)
        oi_tree = oc
        pcr = None
        # for expiry in sorted(set(list(oc['expiry'])), reverse=True):
        for expiry in expiry_list:
            print( expiry_list[0])
            ce_oi_sum = oc[(oc['tradingsymbol'].str[-2:] == 'CE') & (oc['expiry'] == expiry)][
                'oi'].sum()
            pe_oi_sum = oc[(oc['tradingsymbol'].str[-2:] == 'PE') & (oc['expiry'] == expiry)][
                'oi'].sum()
            oi_tree['oi_ce' + str(expiry)] = oc.loc[(oc['tradingsymbol'].str[-2:] == 'CE') & (
                        oc['expiry'] == expiry), 'oi'] / ce_oi_sum if ce_oi_sum else 0
            oi_tree['oi_pe' + str(expiry)] = -oc.loc[(oc['tradingsymbol'].str[-2:] == 'PE') & (
                        oc['expiry'] == expiry), 'oi'] / pe_oi_sum if pe_oi_sum else 0
            pcr = pe_oi_sum/ce_oi_sum if (expiry == expiry_list[0]) else pcr
        oi_tree.fillna(0, inplace=True)

        max_pain_oc = oc[oc['expiry'] == expiry_list[0]]
        last_price = self.kite_object.getQuoteLive(scrip[0])['last_price']

        max_pain_oc['itm x oi'] = max_pain_oc[['strike', 'tradingsymbol', 'oi']].apply(
            lambda x: max(last_price - x['strike'], 0) * x['oi'] if (x['tradingsymbol'][-2:] == 'CE') else max(
                x['strike'] - last_price, 0) * x['oi'], axis=1)
        max_pain_oc = max_pain_oc.groupby(by=['strike'], as_index=False)['itm x oi'].sum().fillna(0).round()
        max_pain = max_pain_oc.sort_values(['itm x oi'], ascending=False).head(1)['strike'].values[0]

        return [oi_tree,pcr,max_pain]

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
        positions['wtd_strike'] = positions[['type', 'qty', 'strike', 'avg_price']].apply(
            lambda x: np.absolute(x['qty'] * x['strike']) if (x['type'] != 'FUT') else np.absolute(
                x['qty'] * x['avg_price']), axis=1)
        positions['abs_qty'] = np.absolute(positions['qty'])

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

        scrips = set(list(df['scrip']))
        df['pivot_strike'] = 0
        for scrip in scrips:
            df.loc[((df['scrip'] == scrip) & (df['l_s'] == 'Long')), 'pivot_strike'] = \
            df[((df['scrip'] == scrip) & (df['l_s'] == 'Long'))]['wtd_strike'].sum() / \
            df[((df['scrip'] == scrip) & (df['l_s'] == 'Long'))]['abs_qty'].sum()
            df.loc[((df['scrip'] == scrip) & (df['l_s'] == 'Short')), 'pivot_strike'] = \
            df[((df['scrip'] == scrip) & (df['l_s'] == 'Short'))]['wtd_strike'].sum() / \
            df[((df['scrip'] == scrip) & (df['l_s'] == 'Short'))]['abs_qty'].sum()

        # df.set_index('scrip',inplace=True)
        # print(positions.groupby(by=['scrip']).sum()[['qty','orig_liab','curr_liab','delta','theta','pnl']])

        # df.loc[df['l_s'] == '',['strike']] = ''
        # for col in ['qty', 'orig_liab', 'curr_liab', 'delta (D)', 'theta (T)', 'T/D', 'pnl']:
        #     df[col] = df[col].map('{:,.0f}'.format)
        for col in ['qty', 'orig_liab', 'curr_liab', 'delta (D)', 'theta (T)', 'T/D', 'pnl', 'pivot_strike']:
            df[col] = df[col].map('{:,.0f}'.format)
        df.loc[df['pivot_strike'] == '0', 'pivot_strike'] = ''
        df.drop(columns=['wtd_strike', 'abs_qty'], axis=1, inplace=True)

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

    def market_snapshot(self):
        # scrips = ['NIFTY 50','NIFTY BANK', 'INDIA VIX']
        scrips = [('NIFTY 50','^NSEI'),
                  ('NIFTY BANK','^NSEBANK'),
                  ('USDINR','INR=X'),
                  ('CRUDE OIL','CL=F'),
                  ('GOLD','GC=F')]
        # kitecodemap = pd.read_csv(os.path.join(os.path.dirname(__file__),'kitensecodes.csv'))
        # scrips = [(kitecodemap[kitecodemap['tradingsymbol'] == scrip]['instrument_token'].values[0],scrip) for scrip in scrips]
        to_date = datetime.date.today()
        from_date = to_date - datetime.timedelta(days=70)
        hist_data = []
        graph_obj = []
        graph_obj1= []
        # for (token,scrip) in scrips:
        for (ticker,scrip) in scrips:
            print(scrip)
            data = yf.download(scrip,period='3mo',interval='1d')  #  THIS CAN BE GOT FROM DATABASE
            data['scrip'] = scrip
            data.reset_index(inplace=True)
            # print(data)
            # hist_data.append(data[data.columns[:-1]])
            hist_data.append(data)
            data_max_date = max(data['Date']).strftime('%d-%b-%y')
            print('data_max_date  ', data_max_date)
            # ticker = kitecodemap[kitecodemap['instrument_token'] == token]['tradingsymbol'].values[0]
            # graph_obj.append(['empty'])
            graph_obj.append(mg.candlestick_plot(ticker,data[data.columns[:-1]]))
            graph_obj1.append(mg.plotly_candlestick(ticker,data[data.columns],include_volume=False,data_date=data_max_date))

        ticker = 'INDIA VIX'
        print(ticker)
        data = mrigutilities.getIndexData(ticker, datetime.date.today() - datetime.timedelta(days=90), datetime.date.today())
        data.reset_index(inplace=True)
        data = data[['date', 'open', 'high', 'low', 'close', 'volume']]
        hist_data.append(data)
        data_max_date = max(data['date']).strftime('%d-%b-%y')
        print('data_max_date  ',data_max_date)
        graph_obj.append(mg.candlestick_plot(ticker, data[data.columns[:-1]]))
        graph_obj1.append(mg.plotly_candlestick(ticker, data[data.columns],include_volume=False,data_date=data_max_date))

        current_month = datetime.date.strftime(datetime.date.today(), '%b')
        next_month = datetime.date.strftime(datetime.date.today() + datetime.timedelta(days=31), '%b')
        current_year = datetime.date.strftime(datetime.date.today(), '%y')
        # crude = 'CRUDEOIL' + current_year + current_month.upper() + 'FUT'
        # usdinr = 'USDINR' + current_year + current_month.upper() + 'FUT'
        # gold = 'GOLD' + current_year + current_month.upper() + 'FUT'

        # ins = self.kite_object.getInstruments(exchange='CDS')
        # # usdinr = ins[(ins['name'] == 'USDINR') & (ins['instrument_type'] == 'FUT')].sort_values(by='expiry').head(1)['tradingsymbol']
        # # if not (usdinr in ins['tradingsymbol']):
        # #     usdinr = 'USDINR' + current_year + next_month.upper() + 'FUT'
        # #
        # # usdinr_token = ins[ins['tradingsymbol'] == usdinr]['instrument_token'].values[0]
        # usdinr_token = list(ins[(ins['name'] == 'USDINR') & (ins['instrument_type'] == 'FUT')].sort_values(by='expiry').head(2)['instrument_token'])
        # usdinr = list(ins[(ins['name'] == 'USDINR') & (ins['instrument_type'] == 'FUT')].sort_values(by='expiry').head(2)['tradingsymbol'])
        #
        #
        # ins = self.kite_object.getInstruments(exchange='MCX')
        # # print(crude)
        # # print(crude in ins['tradingsymbol'])
        # #
        # # if not (crude in ins['tradingsymbol']):
        # #     crude = 'CRUDEOIL' + current_year + next_month.upper() + 'FUT'
        # # crude_token = ins[ins['tradingsymbol'] == crude]['instrument_token'].values[0]
        # # crude_token = str(ins[(ins['name'] == 'CRUDEOIL') & (ins['instrument_type'] == 'FUT')].sort_values(by='expiry').head(1)['instrument_token'].values[0])
        # crude_token = list(ins[(ins['name'] == 'CRUDEOIL') & (ins['instrument_type'] == 'FUT')].sort_values(by='expiry').head(2)['instrument_token'])
        # crude = list(ins[(ins['name'] == 'CRUDEOIL') & (ins['instrument_type'] == 'FUT')].sort_values(by='expiry').head(2)['tradingsymbol'])
        #
        # ins = self.kite_object.getInstruments(exchange='MCX')
        # # print(gold)
        # # print(gold in ins['tradingsymbol'])
        # # if not (gold in ins['tradingsymbol']):
        # #     gold = 'GOLD' + current_year + next_month.upper() + 'FUT'
        # # print(gold)
        # # gold_token = ins[ins['tradingsymbol'] == gold]['instrument_token'].values[0]
        # gold_token = list(ins[(ins['name'] == 'GOLD') & (ins['instrument_type'] == 'FUT')].sort_values(by='expiry').head(2)['instrument_token'])
        # gold = list(ins[(ins['name'] == 'GOLD') & (ins['instrument_type'] == 'FUT')].sort_values(by='expiry').head(2)['tradingsymbol'])
        #
        # data = None
        # try:
        #     data = self.kite_object.getHistorical(usdinr_token[0], from_date, to_date, 'day')
        #     usdinr = usdinr[0]
        # except:
        #     pass
        # if (data is None):
        #     data = self.kite_object.getHistorical(usdinr_token[1], from_date, to_date, 'day')
        #     usdinr = usdinr[1]
        #
        # data = yf.download(scrip, period='3mo', interval='1d')
        # data['scrip'] = 'USDINR'
        # # hist_data.append(data[data.columns[:-1]])
        # hist_data.append(data)
        # graph_obj.append(mg.candlestick_plot(usdinr, data[data.columns[:-1]]))
        # graph_obj1.append(mg.plotly_candlestick(usdinr,data[data.columns]))
        #
        # data = None
        # try:
        #     data = self.kite_object.getHistorical(crude_token[0], from_date, to_date, 'day')
        #     crude = crude[0]
        # except:
        #     pass
        # if (data is None):
        #     data = self.kite_object.getHistorical(crude_token[1], from_date, to_date, 'day')
        #     crude = crude[1]
        # data['scrip'] = 'CRUDEOIL'
        # # data = self.kite_object.getHistorical(crude_token, from_date, to_date, 'day')
        # hist_data.append(data)
        # # hist_data.append(data[data.columns[:-1]])
        # graph_obj.append(mg.candlestick_plot(crude, data[data.columns[:-1]]))
        # graph_obj1.append(mg.plotly_candlestick(crude,data[data.columns]))
        #
        # data = None
        # try:
        #     data = self.kite_object.getHistorical(gold_token[0], from_date, to_date, 'day')
        #     gold = gold[0]
        # except:
        #     pass
        # if (data is None):
        #     data = self.kite_object.getHistorical(gold_token[1], from_date, to_date, 'day')
        #     gold = gold[1]
        #
        # data['scrip'] = 'GOLD'
        # # print(data)
        # # data = self.kite_object.getHistorical(gold_token, from_date, to_date, 'day')
        # # hist_data.append(data[data.columns[:-1]])
        # hist_data.append(data)
        # graph_obj.append(mg.candlestick_plot(gold, data[data.columns[:-1]]))
        # graph_obj1.append(mg.plotly_candlestick(gold,data[data.columns]))

        return [graph_obj,hist_data,graph_obj1]

if __name__ == '__main__':
    d = tradingDB()
    hist_data = d.market_snapshot()[1]
    print(hist_data[-1])





