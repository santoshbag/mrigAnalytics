# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 11:22:01 2023

@author: Santosh Bag
"""
import base64
import sys,os
import time
from io import StringIO

import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import datetime #import date, timedelta
import pandas as pd #import DataFrame
#from sqlalchemy import create_engine
import mrigutilities
import mrigstatics as ms
import zipfile,re
import yfinance as yf
#from bs4 import BeautifulSoup
#from time import sleep
import csv
import research.screener_TA as sta
import matplotlib.pyplot as plt
import tradingDB as tdb
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import strategies.market_instruments as mo
import research.analytics as ra

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
NavigationToolbar2Tk)
import tkcalendar

from PIL import Image, ImageTk

from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QHeaderView


import kite.kite_account as ka
import kite.mrigkite as mk
# kite_object = ka.kite_account()
kite_object = mk.mrigkite()

# today = datetime.date.today()
today = datetime.datetime.now()
engine = mrigutilities.sql_engine()


col_map = {'Instrument':'instrument','Qty.':'qty','Avg.':'avg_price','LTP':'ltp','P&L':'pnl'}

pos_cols = ['Scrip','Instrument','LongShort','Quantity','Orig Liability','Curr Liability','Delta','Theta','PnL']

class TableWidget(QTableWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setRowCount(len(data))
        self.setColumnCount(len(data[0]))
        self.setHorizontalHeaderLabels(pos_cols)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fill_table()

    def fill_table(self):
        for i, row in enumerate(self.data):
            for j, cell in enumerate(row):
                item = QTableWidgetItem(str(cell))
                self.setItem(i, j, item)


def price(scrip):
    price = None
    yahoo_map = {'NIFTY':'^NSEI','BANKNIFTY':'^NSEBANK'}
    yahooid = scrip+'.NS'
    if (scrip == 'NIFTY' or scrip == 'BANKNIFTY'):
        yahooid = yahoo_map[scrip]
    if len(yahooid) > 0:
        if yahooid is not None:
            try:
                price = yf.download(yahooid,period='1d').Close.values[0]
            except:
                None
                
    return price

def num_pos(s):
    return re.search(r"\d", s).start()

def load_DB(flag=True,diagnostic=False):
    filename = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
    
    if filename != None:
        
        positions = pd.read_csv(filename)
        positions = positions[positions['Product'] == 'NRML']
        positions['type'] = positions['Instrument'].apply(lambda x : x[-2:])
        positions['type'] = positions['type'].apply(lambda x : 'FUT' if(x == 'UT') else x)
        positions['scrip'] = positions['Instrument'].apply(lambda x : x[:num_pos(x)])
        positions['strike'] = positions['Instrument'].apply(lambda x : x[num_pos(x)+5:-2])
        positions['strike'] = positions['strike'].apply(lambda x : 0 if(x == 'F') else x)
        positions['expiry'] = positions['Instrument'].apply(lambda x : datetime.datetime.strptime(x[num_pos(x):num_pos(x)+5]+'27','%y%b%d'))
        positions.drop(columns=['Chg.','Product'],inplace=True)
        positions.rename(columns=col_map,inplace=True)
        positions['pos_date'] = today
        positions['snapshot'] = int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        
        if diagnostic:
            print(positions)
        
        write_flag=flag
        
        if write_flag:
            positions.to_sql('live_positions',engine,index=False,if_exists='append')
    

def showAnalytics():
    def highlight(s):
        if s.l_s == '':
            return ['background-color: yellow'] * len(s)
        else:
            return ['background-color: white'] * len(s)
        
    volfile = 'vol.csv'
    vol_pd = pd.read_csv(volfile)
    vol_pd.drop(columns=['Date','Underlying Close Price (A)','Underlying Previous Day Close Price (B)','Underlying Log Returns (C) = LN(A/B)','Previous Day Underlying Volatility (D)'],inplace=True)
    vol_pd.set_index('Symbol',inplace=True)
    vol_pd.rename(columns={'Underlying Annualised Volatility (F) = E*Sqrt(365)' : 'vol'},inplace=True)
    hist_vol = vol_pd.to_dict()    
    
    hist_vol = hist_vol['vol']
    
    hist_vol['NIFTY'] =  0.09
    hist_vol['BANKNIFTY'] = 0.14
    sql = 'select * from live_positions where snapshot = \
    (select snapshot from live_positions where pos_date = \
    (select pos_date from live_positions order by pos_date desc limit 1)\
    order by snapshot desc limit 1)'
    
    positions = pd.read_sql(sql, engine)
    positions['l_s'] = positions[['type','qty']].apply(lambda x: 'Short' if(((x['type'] == 'CE' or x['type'] == 'FUT') and x['qty'] < 0 ) or (x['type'] == 'PE' and x['qty'] > 0 )) else 'Long', axis=1)
    
    positions['orig_liab'] = positions[['type','qty','avg_price']].apply(lambda x: x['qty']*x['avg_price'] if(x['qty'] < 0 and x['type'] != 'FUT') else 0, axis= 1)
    positions['curr_liab'] = positions[['type','qty','ltp']].apply(lambda x: x['qty']*x['ltp'] if(x['qty'] < 0 and x['type'] != 'FUT') else 0, axis= 1)
    positions['max_profit'] = positions['orig_liab'].apply(lambda x: -x if (x< 0) else 'infinite')
    
    positions['max_loss'] = positions[['type','qty','avg_price','orig_liab']].apply(lambda x: -x['qty']*x['avg_price'] if(x['orig_liab'] == 0 and x['type'] != 'FUT') else 'infinite', axis= 1)
    positions['spot'] = positions['scrip'].apply(lambda x: price(x))
    positions['histVol'] = positions['scrip'].apply(lambda x: float(hist_vol[x]))
    
    positions['impVol'] = -1
    positions['impVol'] = positions[['type','spot','strike','expiry','ltp']].apply(lambda x : mrigutilities.impVol(x['spot'],x['strike'],abs((x['expiry']-today).days)/365,x['ltp'],opt=x['type']), axis=1)
    positions['impVol'] = positions[['impVol','histVol']].apply(lambda x : x['histVol'] if(x['impVol'] == -1) else x['impVol'],axis=1)
    positions['delta'] = positions[['type','qty','spot','strike','expiry','impVol']].apply(lambda x : x['qty']*mrigutilities.bs_delta(x['spot'],x['strike'],abs((x['expiry']-today).days)/365,x['impVol'],opt=x['type']), axis=1)
    positions['theta'] = positions[['type','qty','spot','strike','expiry','impVol']].apply(lambda x : x['qty']*mrigutilities.bs_theta(x['spot'],x['strike'],abs((x['expiry']-today).days)/365,x['impVol'],opt=x['type']), axis=1)
    positions['theta/delta'] = positions[['qty','delta','theta']].apply(lambda x : abs(x['theta']/x['delta']) if (x['delta'] != 0 and x['qty'] < 0)  else 0, axis=1)
    
    
    df1 = positions.groupby(by=['scrip','instrument','l_s'], as_index=False)['qty','strike','orig_liab','curr_liab','delta','theta','theta/delta','pnl'].sum().fillna(0).round()
    
    df2 = df1.groupby(by=['scrip','l_s'], as_index=False)['qty','strike','orig_liab','curr_liab','delta','theta','theta/delta','pnl'].sum().fillna(0).round().assign(instrument = '')
    
    df3 = df1.groupby(by=['scrip'], as_index=False)['qty','strike','orig_liab','curr_liab','delta','theta','theta/delta','pnl'].sum().fillna(0).round().assign(l_s = '')
    
    
    df = (pd.concat([df1, df3])
            .reindex(df1.columns, axis=1)
            .fillna('')
            .sort_values(['scrip','l_s'], ascending=True,ignore_index=True))
    #df.set_index('scrip',inplace=True)    
    # print(positions.groupby(by=['scrip']).sum()[['qty','orig_liab','curr_liab','delta','theta','pnl']])


    return [positions,df]


def showAnalytics_live():
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

    live_positions = kite_object.getPositions()
    print(live_positions)

    positions = live_positions.loc[live_positions['exchange'] == 'NFO',
    ['tradingsymbol', 'instrument_token', 'product', 'quantity', 'average_price', 'last_price', 'pnl']]
    positions.rename(columns={'tradingsymbol':'Instrument',
                              'quantity' : 'qty',
                              'average_price' : 'avg_price',
                              'last_price':'ltp'},inplace=True)
    positions['type'] = positions['Instrument'].apply(lambda x: x[-2:])
    positions['type'] = positions['type'].apply(lambda x: 'FUT' if (x == 'UT') else x)
    positions['scrip'] = positions['Instrument'].apply(lambda x: x[:num_pos(x)])
    positions['strike'] = positions['Instrument'].apply(lambda x: x[num_pos(x) + 5:-2])
    positions['strike'] = positions['strike'].apply(lambda x: 0 if (x == 'F') else x)
    positions['strike'] = pd.to_numeric(positions['strike'],errors='ignore')
    positions['expiry'] = datetime.datetime.strptime('24MAY09','%y%b%d')
    try:
        positions['expiry'] = positions['Instrument'].apply(
            lambda x: datetime.datetime.strptime(x[num_pos(x):num_pos(x) + 5] + '27', '%y%b%d'))
    except:
        pass
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
    positions['wtd_strike'] = positions[['type', 'qty', 'strike','avg_price']].apply(
        lambda x: np.absolute(x['qty'] * x['strike']) if (x['type'] != 'FUT') else np.absolute(x['qty'] * x['avg_price']), axis=1)
    positions['abs_qty'] = np.absolute(positions['qty'])
    positions['max_profit'] = positions['orig_liab'].apply(lambda x: -x if (x < 0) else 'infinite')

    positions['breakeven'] = positions[['type', 'strike','avg_price']].apply(
        lambda x: (x['avg_price']+x['strike']) if (x['type'] != 'PE') else (x['strike'] - x['avg_price']), axis=1)
    positions['wtd_breakeven'] = positions[['qty', 'breakeven']].apply(
        lambda x: np.absolute(x['qty'] * x['breakeven']) , axis=1)

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
    positions['delta (D)'] = positions[['type', 'qty', 'spot', 'strike', 'expiry', 'impVol']].apply(
        lambda x: x['qty'] * mrigutilities.bs_delta(x['spot'], x['strike'], abs((x['expiry'] - today).days) / 365,
                                                    x['impVol'], opt=x['type']), axis=1)
    positions['theta (T)'] = positions[['type', 'qty', 'spot', 'strike', 'expiry', 'impVol']].apply(
        lambda x: x['qty'] * mrigutilities.bs_theta(x['spot'], x['strike'], abs((x['expiry'] - today).days) / 365,
                                                    x['impVol'], opt=x['type']), axis=1)
    positions['T/D'] = positions[['qty', 'delta (D)', 'theta (T)']].apply(
        lambda x: abs(x['theta (T)'] / x['delta (D)']) if (x['delta (D)'] != 0 and x['qty'] < 0) else 0, axis=1)

    positions['underlying'] = positions[['scrip']].apply(lambda x: kite_object.getQuoteLive(x['scrip'])['last_price'],axis=1)
    positions['Intrinsic Value'] = positions[['strike','type','qty','underlying']].apply(
        lambda x : x['qty']* max((x['underlying'] - x['strike']),0) if (x['type'] == 'CE') else
        (x['qty']* max((x['strike'] - x['underlying']),0) if (x['type'] == 'PE') else 0),axis=1)
    positions['Time Value'] = positions[['type','pnl','Intrinsic Value']].apply(
        lambda x : (x['pnl'] - x['Intrinsic Value']) if (x['type'] != 'FUT') else 0 ,axis=1)

    positions['strike'] = positions['strike'].map('{:,.0f}'.format)

    df1 = positions.groupby(by=['scrip', 'instrument', 'l_s','strike'], as_index=False)[
        'qty', 'orig_liab', 'curr_liab', 'delta (D)', 'theta (T)', 'T/D', 'pnl','Intrinsic Value','Time Value','wtd_strike','abs_qty','breakeven','wtd_breakeven'].sum().fillna(0).round()


    df2 = df1.groupby(by=['scrip', 'l_s'], as_index=False)[
        'qty', 'strike', 'orig_liab', 'curr_liab', 'delta (D)', 'theta (T)', 'T/D', 'pnl','Intrinsic Value','Time Value','wtd_strike','abs_qty','breakeven','wtd_breakeven'].sum().fillna(
        0).round().assign(instrument='')

    df3 = df1.groupby(by=['scrip'], as_index=False)[
        'qty', 'orig_liab', 'curr_liab', 'delta (D)', 'theta (T)', 'T/D', 'pnl','Intrinsic Value','Time Value','wtd_strike','abs_qty','breakeven','wtd_breakeven'].sum().fillna(
        0).round().assign(l_s='')


    df = (pd.concat([df1, df2, df3])
          .reindex(df1.columns, axis=1)
          .fillna('')
          .sort_values(['scrip', 'l_s','instrument'], ascending=True, ignore_index=True))

    scrips = set(list(df['scrip']))
    # df['pivot_strike'] = 0
    wtd_items = {}
    for scrip in scrips:
        # df.loc[((df['scrip'] == scrip) & (df['l_s'] == 'Long')),'pivot_strike'] = df[((df['scrip'] == scrip) & (df['l_s'] == 'Long'))]['wtd_strike'].sum()/df[((df['scrip'] == scrip) & (df['l_s'] == 'Long'))]['abs_qty'].sum()
        # df.loc[((df['scrip'] == scrip) & (df['l_s'] == 'Short')),'pivot_strike'] = df[((df['scrip'] == scrip) & (df['l_s'] == 'Short'))]['wtd_strike'].sum()/df[((df['scrip'] == scrip) & (df['l_s'] == 'Short'))]['abs_qty'].sum()
        # df.loc[((df['scrip'] == scrip) & (df['l_s'] == 'Long')),'breakeven'] = df[((df['scrip'] == scrip) & (df['l_s'] == 'Long'))]['wtd_breakeven'].sum()/df[((df['scrip'] == scrip) & (df['l_s'] == 'Long'))]['abs_qty'].sum()
        # df.loc[((df['scrip'] == scrip) & (df['l_s'] == 'Short')),'breakeven'] = df[((df['scrip'] == scrip) & (df['l_s'] == 'Short'))]['wtd_breakeven'].sum()/df[((df['scrip'] == scrip) & (df['l_s'] == 'Short'))]['abs_qty'].sum()
        wtd_items[(scrip,'Long','pivot_strike')] = '{:,.0f}'.format(df[((df['scrip'] == scrip) & (df['l_s'] == 'Long'))]['wtd_strike'].sum()/df[((df['scrip'] == scrip) & (df['l_s'] == 'Long'))]['abs_qty'].sum())
        wtd_items[(scrip,'Short','pivot_strike')] = '{:,.0f}'.format(df[((df['scrip'] == scrip) & (df['l_s'] == 'Short'))]['wtd_strike'].sum()/df[((df['scrip'] == scrip) & (df['l_s'] == 'Short'))]['abs_qty'].sum())
        wtd_items[(scrip,'Long', 'breakeven')] = df[((df['scrip'] == scrip) & (df['l_s'] == 'Long'))]['wtd_breakeven'].sum()/df[((df['scrip'] == scrip) & (df['l_s'] == 'Long'))]['abs_qty'].sum()
        wtd_items[(scrip,'Short','breakeven')] = df[((df['scrip'] == scrip) & (df['l_s'] == 'Short'))]['wtd_breakeven'].sum()/df[((df['scrip'] == scrip) & (df['l_s'] == 'Short'))]['abs_qty'].sum()


    for scrip in df['scrip']:
        # sec = scrip
        # if scrip == 'NIFTY':
        #     sec = 'NIFTY 50'
        # elif scrip == 'BANKNIFTY':
        #     sec = 'NIFTY BANK'
        # print(scrip+'-------->'+sec)
        df.loc[((df['scrip'] == scrip) & (df['l_s'] == '')),'instrument'] = 'Last Price ---> '+str(kite_object.getQuoteLive(scrip)['last_price'])
        df.loc[((df['scrip'] == scrip) & (df['l_s'] == 'Long') & (df['instrument'] == '')),'strike'] = wtd_items[(scrip,'Long','pivot_strike')]
        df.loc[((df['scrip'] == scrip) & (df['l_s'] == 'Short') & (df['instrument'] == '')),'strike'] = wtd_items[(scrip,'Short','pivot_strike')]
        df.loc[((df['scrip'] == scrip) & (df['l_s'] == 'Long') & (df['instrument'] == '')),'breakeven'] = wtd_items[(scrip,'Long','breakeven')]
        df.loc[((df['scrip'] == scrip) & (df['l_s'] == 'Short') & (df['instrument'] == '')),'breakeven'] = wtd_items[(scrip,'Short','breakeven')]

    # df.set_index('scrip',inplace=True)
    # print(positions.groupby(by=['scrip']).sum()[['qty','orig_liab','curr_liab','delta','theta','pnl']])

    # df.loc[df['l_s'] == '',['strike']] = ''
    for col in ['qty', 'orig_liab', 'curr_liab', 'delta (D)', 'theta (T)', 'T/D', 'pnl','Intrinsic Value','Time Value','breakeven']:
        df[col] = df[col].map('{:,.0f}'.format)
    # df.loc[df['pivot_strike'] == '0','pivot_strike'] = ''
    # df.loc[df['pivot_strike'] == '','breakeven'] = ''
    # df.loc[df['instrument'] == '', 'breakeven'] = ''
    df.drop(columns=['wtd_strike','abs_qty','wtd_breakeven'],axis=1,inplace=True)

    # print(df.columns)
    df.rename(columns=ms.trade_display_analytics, inplace=True)

    return [positions, df]


def display_dataframe():

    # create the main window
    win = tk.Tk()
    win.title("Position Analytics and Greeks")

    win.geometry("1200x800")
    win.resizable()#width=False, height=False)

    frame = tk.Frame(win)
    frame.pack()

    blankframe = tk.Frame(win)
    blankframe.pack()

    blanklabel = tk.Label(blankframe,text='              ',pady=5)
    blanklabel.pack()

    tree = ttk.Treeview(win)

    # df = showAnalytics()[1]
    df = showAnalytics_live()[1]
    def build_tree(df=None,tree=None):
        # global tree
        if tree is not None:
            tree.destroy()
            win.update()
        style=ttk.Style()
        style.configure("Treeview", bg = 'lightgreen')
        style.configure("Treeview.Heading", bg ="#00337f", font=('Poppins bold', 12),borderwidth="1")


        # create a treeview widget to display the DataFrame

        tree = ttk.Treeview(win, columns=list(df.columns), show="headings")

        tree.tag_configure('subtotal', background='yellow',font=('Arial bold', 12))
        tree.tag_configure('subtotal_ls', background='cyan', font=('Arial bold', 10))
        tree.tag_configure('even', background='lightgreen')
        tree.tag_configure('odd', background='lightgray')

        # Constructing vertical scrollbar
        # with treeview
        verscrlbar = ttk.Scrollbar(win,
                                   orient="vertical",
                                   command=tree.yview)

        # Calling pack method w.r.to vertical
        # scrollbar
        verscrlbar.pack(side='right', fill='y')

        # Constructing horizontal scrollbar
        # with treeview
        horscrlbar = ttk.Scrollbar(win,
                                   orient="horizontal",
                                   command=tree.xview)

        # Calling pack method w.r.to horizontal
        # scrollbar
        horscrlbar.pack(side='bottom', fill='x')

        # Configuring treeview
        tree.configure(xscrollcommand=verscrlbar.set)
        # for i in len(df.columns):
        #     tree.column('"#' + str(i)+'"', width=200, stretch=0)

        tree.column("#1", width=100, stretch=0, anchor=tk.CENTER)
        tree.column("#2", width=200, stretch=0, anchor=tk.CENTER)
        tree.column("#3", width=50, stretch=0, anchor=tk.CENTER)
        tree.column("#4", width=50, stretch=0, anchor=tk.E)
        tree.column("#5", width=60, stretch=0, anchor=tk.E)
        tree.column("#6", width=100, stretch=0, anchor=tk.E)
        tree.column("#7", width=100, stretch=0, anchor=tk.E)
        tree.column("#8", width=80, stretch=0, anchor=tk.E)
        tree.column("#9", width=80, stretch=0, anchor=tk.E)
        tree.column("#10", width=50, stretch=0, anchor=tk.E)
        tree.column("#11", width=100, stretch=0, anchor=tk.E)
        tree.column("#12", width=100, stretch=0, anchor=tk.E)
        tree.column("#13", width=100, stretch=0, anchor=tk.E)
        tree.column("#14", width=100, stretch=0, anchor=tk.E)
        # tree.column("#15", width=100, stretch=0, anchor=tk.E)



        for col in df.columns:
            tree.heading(col, text=col)

        # add the data to the table
        cnt = 0
        for i, row in df.iterrows():
            if row[['l_s']].values == '':
                tree.insert("", "end", values=list(row), tags=('subtotal',))
            else:
                if row[['instrument']].values == '':
                    tree.insert("", "end", values=list(row), tags=('subtotal_ls',))
                else:
                    if cnt % 2 == 0:
                        tree.insert("", "end", values=list(row),tags=('even',))
                    else:
                        # print(list(row))
                        tree.insert("", "end", values=list(row), tags=('odd',))
            cnt = cnt + 1

        def OnDoubleClick(event):
            item = tree.identify('item',event.x,event.y)
            scrip = tree.item(item)['values'][0]
            print("you clicked on "+ scrip)
            level_screen(scrip)

        tree.bind("<Double-1>", OnDoubleClick)
        tree.pack(side=tk.LEFT, expand=1, fill='y')

    # pack the treeview widget


    build_tree(df)

    def refresh():
        # tree.destroy()
        df = showAnalytics_live()[1]
        build_tree(df,tree)


    # refresh_button = tk.Button(frame, text="Refresh", font=('Poppins bold', 16), command=refresh)
    # refresh_button.grid(row=0,column=0)

    # refresh_button.pack(side = tk.LEFT)
    
    def close_win():
        win.destroy()


    close_win_button = tk.Button(frame, text= "Close", font=('Poppins bold', 16), command=close_win)
    # close_win_button.grid(row=0,column=1)
    close_win_button.pack(side = tk.LEFT)

    


def level_screen(scrip):
    lscreen =  tdb.tradingDB()
    levels = ra.level_analysis([scrip])
    fig = levels['level_chart']
    oi_tree = levels['oi_tree']
    pcr = levels['pcr']
    max_pain = levels['max_pain']
    print(set(oi_tree['expiry']))
    oi_tree.sort_values(by=['expiry', 'strike'], ascending=[True, True], inplace=True)
    num_charts = 4 if scrip in ['NIFTY','BANKNIFTY'] else 3
    fig, ax = plt.subplots(1, num_charts, figsize=(20, 10), squeeze=False)

    # oi_tree[['oi_ce','oi_pe']].plot(kind='barh')
    i = 0
    last_price = kite_object.getQuoteLive(scrip)['last_price']
    bar_height = min(10,0.003*last_price) if last_price < 30000 else min(20,0.003*last_price)
    print_expiries = sorted(set(list(oi_tree['expiry'])))
    for exp in print_expiries[0:min(4, len(print_expiries))]:
        print(exp)
        ax1 = ax[0, i]
        ax1.set_title(exp)
        ax1.grid()
        ax2 = ax[0, i].twinx()
        x_data = oi_tree[oi_tree['expiry'] == exp]['strike']
        y1_data = oi_tree[oi_tree['expiry'] == exp]['oi_ce' + str(exp)]
        y2_data = oi_tree[oi_tree['expiry'] == exp]['oi_pe' + str(exp)]
        if i == 0:
            ax1.set_ylabel('STRIKE', fontsize=16)
        else:
            ax1.set_ylabel('', fontsize=16)
        ax1.set_xlabel('OPEN INTEREST', fontsize=16)
        ax1.tick_params(axis='y', labelsize=12)

        ax1.barh(x_data, y1_data, color='b', height=bar_height)
        ax1.autoscale()

        # ax2.set_ylabel('STRIKE')

        # ax2.tick_params(axis='y', labelsize=10)
        ax2.barh(x_data, y2_data, color='g', height=bar_height)
        ax2.get_yaxis().set_visible(False)
        ax2.autoscale()

        i += 1

    win = tk.Tk()
    win.title(scrip +" ("+str(last_price)+") "+" Levels ")

    win.geometry("1200x800")
    win.resizable(width=False, height=False)

    frame = tk.Frame(win)
    frame.pack()

    blanklabel = tk.Label(frame, text=scrip +" ("+str(last_price)+") "+" PCR ("+str(round(pcr,2))+") "+" MaxPain ("+str(round(max_pain,2))+") " ' - Open Interest and Levels                 ',font=('Poppins bold', 16), pady=10)
    blanklabel.pack(side=tk.LEFT)

    canvas = FigureCanvasTkAgg(fig,master=win)
    # print(levels)
    # level_chart = base64.b64decode(fig)#.decode('utf-8').replace('\n', '')
    # f= open(level_chart ,'rb')
    # level_chart = ImageTk.PhotoImage(Image.open(f))
    # canvas = FigureCanvasTkAgg(fig,master=win)

    canvas.draw()

    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().pack()

    # creating the Matplotlib toolbar
    toolbar = NavigationToolbar2Tk(canvas,win)
    toolbar.update()

    # placing the toolbar on the Tkinter window
    canvas.get_tk_widget().pack()

    def close_win():
        win.destroy()

    close_win_button = tk.Button(frame, text="Close", font=('Poppins bold', 14), command=close_win)
    # close_win_button.grid(row=0,column=1)
    close_win_button.pack(side=tk.RIGHT)

def ta_screen():
    # create the main window
    win = tk.Tk()
    win.title("Technical Screener")

    win.geometry("1200x800")
    win.resizable(width=False, height=False)

    frame = tk.Frame(win)
    frame.pack()


    rvar = tk.StringVar(frame)
    bottomframe = tk.Frame(win)
    bottomframe.pack( side = tk.BOTTOM )

    df = sta.display_analytics()
    
    def get_df():
        df = sta.display_analytics(str(rvar.get()))

    style=ttk.Style()
    style.configure("screener", background = 'lightgreen',font=('Poppins bold', 12),borderwidth="1")
    style.configure("screener.Heading", background ="#00337f", font=('Poppins bold', 12),borderwidth="1")


    # create a treeview widget to display the DataFrame

    tree = ttk.Treeview(win, columns=list(df.columns), show="headings")

    # Constructing vertical scrollbar
    # with treeview
    verscrlbar = ttk.Scrollbar(win,
                               orient ="vertical",
                               command = tree.yview)
     
    # Calling pack method w.r.to vertical
    # scrollbar
    verscrlbar.pack(side ='right', fill ='x')
     
    # Configuring treeview
    tree.configure(xscrollcommand = verscrlbar.set)

    tree.tag_configure('odd', background='cyan')
    tree.tag_configure('even', background='lightgreen')

    # for i in len(df.columns):
    #     tree.column('"#' + str(i)+'"', width=200, stretch=0)
    
    tree.column("#1", width=100, stretch=0,anchor='e')
    tree.column("#2", width=100, stretch=0, anchor='center')
    tree.column("#3", width=100, stretch=0, anchor='center')
    tree.column("#4", width=100, stretch=0, anchor='center')
    tree.column("#5", width=100, stretch=0, anchor='center')
    tree.column("#6", width=100, stretch=0, anchor='center')
    tree.column("#7", width=100, stretch=0, anchor='center')
    tree.column("#8", width=100, stretch=0, anchor='center')
    tree.column("#9", width=100, stretch=0, anchor='center')
    tree.column("#10", width=100, stretch=0, anchor='center')
    tree.column("#11", width=100, stretch=0, anchor='center')


    for col in df.columns:
        tree.heading(col, text=col)

    # add the data to the table
    
    cnt = 0
    for i, row in df.iterrows():
        if cnt % 2 == 0:
            tree.insert("", "end" ,values=list(row), tag=  ('even',))
        else:
            tree.insert("", "end" ,values=list(row),tag=  ('odd',))
        cnt = cnt + 1
    
    

    # pack the treeview widget
    R1 = tk.Radiobutton(frame, text="NIFTY 50", variable=rvar, value='NIFTY 50', command=get_df)
    R1.pack(side = tk.LEFT)
    R1.select()
    print('-------'+rvar.get())
    R2 = tk.Radiobutton(frame, text="NIFTY 100", variable=rvar, value='NIFTY 100', command=get_df)
    R2.pack(side = tk.LEFT)
    
    refresh_button = tk.Button(frame, text="Refresh", font=('Poppins bold', 16), command=ta_screen)
    # refresh_button.grid(row=0,column=0)

    refresh_button.pack(side = tk.LEFT)
    
    def close_win():
        win.destroy()
    
    close_win_button = tk.Button(frame, text= "Close", font=('Poppins bold', 16), command=close_win)
    # close_win_button.grid(row=0,column=1)
    close_win_button.pack(side = tk.LEFT)


    def download_file():
        filename = filedialog.asksaveasfilename(filetypes=[('CSV Files', '*.csv')])
        if filename != None:
            
            df.to_csv(filename)
            filename.close()
            
    download_button = tk.Button(frame, text="", command=download_file,padx=10,pady=10)
    try:
        downloadIcon = tk.PhotoImage(file="resources/excel_icon.png",master=frame)
        download_button.config(image=downloadIcon)
        download_button.image = downloadIcon

    except:
        pass    
    download_button.pack(side=tk.RIGHT)

                

    # refresh_button.grid(row=0,column=0)

    refresh_button.pack(side = tk.LEFT)
    

    
    tree.pack(side=tk.LEFT, expand = 1, fill = 'y')


def display_analytics():
    app = QApplication(sys.argv)
    # df = showAnalytics()[1]
    df = showAnalytics_live()[1]
    table = TableWidget(list(df.values))
    table.show()
    sys.exit(app.exec_())
    root.mainloop()

def close_root():
    root.destroy()
    win.destroy()
        
def showDB(flag=False,diagnostic=False):
    today = datetime.date.today()
    engine = mrigutilities.sql_engine()
    
    
    col_map = {'Instrument':'instrument','Qty.':'qty','Avg.':'avg_price','LTP':'ltp','P&L':'pnl'}
    file = 'positions.csv'
    positions = pd.read_csv(file)
    positions = positions[positions['Product'] == 'NRML']
    positions['type'] = positions['Instrument'].apply(lambda x : x[-2:])
    positions['type'] = positions['type'].apply(lambda x : 'FUT' if(x == 'UT') else x)
    positions['scrip'] = positions['Instrument'].apply(lambda x : x[:num_pos(x)])
    positions['strike'] = positions['Instrument'].apply(lambda x : x[num_pos(x)+5:-2])
    positions['strike'] = positions['strike'].apply(lambda x : 0 if(x == 'F') else x)
    positions['expiry'] = positions['Instrument'].apply(lambda x : datetime.datetime.strptime(x[num_pos(x):num_pos(x)+5]+'27','%y%b%d'))
    positions.drop(columns=['Chg.','Product'],inplace=True)
    positions.rename(columns=col_map,inplace=True)
    positions['pos_date'] = today
    positions['snapshot'] = int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    
    if diagnostic:
        print(positions)
    
    write_flag=flag
    
    if write_flag:
        positions.to_sql('live_positions',engine,index=False,if_exists='append')
    
    def price(scrip):
        price = None
        yahoo_map = {'NIFTY':'^NSEI','BANKNIFTY':'^NSEBANK'}
        yahooid = scrip+'.NS'
        if (scrip == 'NIFTY' or scrip == 'BANKNIFTY'):
            yahooid = yahoo_map[scrip]
        if len(yahooid) > 0:
            if yahooid is not None:
                try:
                    price = yf.download(yahooid,period='1d').Close.values[0]
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
    vol_pd.drop(columns=['Date','Underlying Close Price (A)','Underlying Previous Day Close Price (B)','Underlying Log Returns (C) = LN(A/B)','Previous Day Underlying Volatility (D)'],inplace=True)
    vol_pd.set_index('Symbol',inplace=True)
    vol_pd.rename(columns={'Underlying Annualised Volatility (F) = E*Sqrt(365)' : 'vol'},inplace=True)
    hist_vol = vol_pd.to_dict()    
    
    hist_vol = hist_vol['vol']
    
    hist_vol['NIFTY'] =  0.09
    hist_vol['BANKNIFTY'] = 0.14
    sql = 'select * from live_positions where snapshot = \
    (select snapshot from live_positions where pos_date = \
    (select pos_date from live_positions order by pos_date desc limit 1)\
    order by snapshot desc limit 1)'
    
    positions = pd.read_sql(sql, engine)
    positions['l_s'] = positions[['type','qty']].apply(lambda x: 'Short' if(((x['type'] == 'CE' or x['type'] == 'FUT') and x['qty'] < 0 ) or (x['type'] == 'PE' and x['qty'] > 0 )) else 'Long', axis=1)
    
    positions['orig_liab'] = positions[['type','qty','avg_price']].apply(lambda x: x['qty']*x['avg_price'] if(x['qty'] < 0 and x['type'] != 'FUT') else 0, axis= 1)
    positions['curr_liab'] = positions[['type','qty','ltp']].apply(lambda x: x['qty']*x['ltp'] if(x['qty'] < 0 and x['type'] != 'FUT') else 0, axis= 1)
    positions['max_profit'] = positions['orig_liab'].apply(lambda x: -x if (x< 0) else 'infinite')
    
    positions['max_loss'] = positions[['type','qty','avg_price','orig_liab']].apply(lambda x: -x['qty']*x['avg_price'] if(x['orig_liab'] == 0 and x['type'] != 'FUT') else 'infinite', axis= 1)
    positions['spot'] = positions['scrip'].apply(lambda x: price(x))
    positions['histVol'] = positions['scrip'].apply(lambda x: float(hist_vol[x]))
    
    positions['impVol'] = -1
    positions['impVol'] = positions[['type','spot','strike','expiry','ltp']].apply(lambda x : mrigutilities.impVol(x['spot'],x['strike'],abs((x['expiry']-today).days)/365,x['ltp'],opt=x['type']), axis=1)
    positions['impVol'] = positions[['impVol','histVol']].apply(lambda x : x['histVol'] if(x['impVol'] == -1) else x['impVol'],axis=1)
    positions['delta'] = positions[['type','qty','spot','strike','expiry','impVol']].apply(lambda x : x['qty']*mrigutilities.bs_delta(x['spot'],x['strike'],abs((x['expiry']-today).days)/365,x['impVol'],opt=x['type']), axis=1)
    positions['theta'] = positions[['type','qty','spot','strike','expiry','impVol']].apply(lambda x : x['qty']*mrigutilities.bs_theta(x['spot'],x['strike'],abs((x['expiry']-today).days)/365,x['impVol'],opt=x['type']), axis=1)
    
    df1 = positions.groupby(by=['scrip','instrument','l_s'], as_index=False)['qty','orig_liab','curr_liab','delta','theta','pnl'].sum().fillna(0).round()
    
    df2 = df1.groupby(by=['scrip','l_s'], as_index=False)['qty','orig_liab','curr_liab','delta','theta','pnl'].sum().fillna(0).round().assign(instrument = '')
    
    df3 = df1.groupby(by=['scrip'], as_index=False)['qty','orig_liab','curr_liab','delta','theta','pnl'].sum().fillna(0).round().assign(l_s = '')
    
    
    df = (pd.concat([df1, df3])
            .reindex(df1.columns, axis=1)
            .fillna('')
            .sort_values(['scrip','l_s'], ascending=True,ignore_index=True))
    #df.set_index('scrip',inplace=True)    
    # print(positions.groupby(by=['scrip']).sum()[['qty','orig_liab','curr_liab','delta','theta','pnl']])

    if diagnostic:
        print(df)    
    return positions

def option_screen():
    def all_children(window):
        _list = window.winfo_children()

        for item in _list:
            if item.winfo_children():
                _list.extend(item.winfo_children())

        return _list

    scrip_var = tk.StringVar()
    call_put = ['CALL', 'PUT']
    spot_var = tk.StringVar()
    type_var = tk.StringVar()
    type_var.set('CALL')
    strike_var = tk.StringVar()
    cmp_var = tk.StringVar()
    vol_var = tk.StringVar()
    rate_var = tk.StringVar()
    expiry_var = tkcalendar.DateEntry()

    def analyze():
        # global scrip_var
        # global expiry
        # global spot_var
        # global type_var
        # global strike_var
        # global cmp_var
        # global vol_var
        # global rate_var

        print('scrip -- >', scrip_var.get())
        print('spot -- >', spot_var.get())
        print('expiry -- >', expiry_var.get_date())

        print('type -- >', type_var.get())
        print('strike -- >', strike_var.get())
        print('ccmp -- >', cmp_var.get())
        print('vol -- >', vol_var.get())
        print('rate -- >', rate_var.get())

        widget_list = all_children(win_lFrame2)
        for item in widget_list:
            print('item deleting')
            item.pack_forget()

        # expiry = datetime.datetime.strptime(expiry_var.get_date(),'%Y-%m-%d').date()
        ce_pe = 'CE' if type_var.get() == 'CALL' else 'PE'
        cmp = float(cmp_var.get()) if len(cmp_var.get()) > 0 else 0
        spot = float(spot_var.get()) if len(spot_var.get()) > 0 else 0
        scrip = scrip_var.get()
        strike = float(strike_var.get())

        op = mo.MarketOptions(scrip, strike, expiry_var.get_date(), ce_pe)
        res = op.valuation(cmp)

        for key in res.keys():
            tk.Label(win_lFrame2, text=key + ' -- >' + str(round(res[key], 2)), font=('calibre', 10, 'normal'),
                     padx=10).pack()

        res = pd.DataFrame()
        scenarios = ['SPOT']
        res = op.scenario_analysis(scenarios)
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        res.plot(x=res.columns[0], y='price', ax=ax, grid=(True, 'r'), title=scenarios[0] + ' Scenarios')

        canvas = FigureCanvasTkAgg(fig, master=win_lFrame2)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # canvas.get_tk_widget().grid(row=0, column=0)


    # win_option = tk.Tk()
    win_option = tk.Toplevel()
    win_option.title("Option Analytics and Greeks")

    win_option.geometry("1000x900")

    win_lFrame0 = tk.LabelFrame(win_option, pady=10)
    win_lFrame0.pack()

    label0 = tk.Label(win_lFrame0, text="Option Analytics and Greeks",
                      font=('Poppins bold', 16))
    label0.pack()

    win_lFrame1 = tk.LabelFrame(win_option, pady=10, bg='cyan')
    win_lFrame1.pack()

    win_lFrame2 = tk.LabelFrame(win_option, pady=10, bg='cyan')
    win_lFrame2.pack()

    label1 = tk.Label(win_lFrame1, text="Option Entry",
                      font=('Poppins bold', 16), bg='cyan')
    label1.pack()



    pad_x = 5
    scripFrame = tk.Frame(win_lFrame1, padx=pad_x, bg='cyan')
    scripFrame.pack(side=tk.LEFT)
    scrip_label = tk.Label(scripFrame, text='SCRIP', font=('calibre', 10, 'normal'), padx=10, width=8)
    scrip_label.pack(side=tk.TOP)

    typeFrame = tk.Frame(win_lFrame1, padx=pad_x, bg='cyan')
    typeFrame.pack(side=tk.LEFT)
    type_label = tk.Label(typeFrame, text='TYPE', font=('calibre', 10, 'normal'), padx=10, width=8)
    type_label.pack(side=tk.TOP)

    expiryFrame = tk.Frame(win_lFrame1, padx=pad_x, bg='cyan')
    expiryFrame.pack(side=tk.LEFT)
    expiry_label = tk.Label(expiryFrame, text='EXPIRY', font=('calibre', 10, 'normal'), padx=10, width=8)
    expiry_label.pack(side=tk.TOP)

    spotFrame = tk.Frame(win_lFrame1, padx=pad_x, bg='cyan')
    spotFrame.pack(side=tk.LEFT)
    spot_label = tk.Label(spotFrame, text='SPOT', font=('calibre', 10, 'normal'), padx=10, width=8)
    spot_label.pack(side=tk.TOP)

    strikeFrame = tk.Frame(win_lFrame1, padx=pad_x, bg='cyan')
    strikeFrame.pack(side=tk.LEFT)
    strike_label = tk.Label(strikeFrame, text='STRIKE', font=('calibre', 10, 'normal'), padx=10, width=8)
    strike_label.pack(side=tk.TOP)

    rateFrame = tk.Frame(win_lFrame1, padx=pad_x, bg='cyan')
    rateFrame.pack(side=tk.LEFT)
    rate_label = tk.Label(rateFrame, text='RATE', font=('calibre', 10, 'normal'), padx=10, width=8)
    rate_label.pack(side=tk.TOP)

    volFrame = tk.Frame(win_lFrame1, padx=pad_x, bg='cyan')
    volFrame.pack(side=tk.LEFT)
    vol_label = tk.Label(volFrame, text='VOL', font=('calibre', 10, 'normal'), padx=10, width=8)
    vol_label.pack(side=tk.TOP)

    cmpFrame = tk.Frame(win_lFrame1, padx=pad_x, bg='cyan')
    cmpFrame.pack(side=tk.LEFT)
    cmp_label = tk.Label(cmpFrame, text='CMP', font=('calibre', 10, 'normal'), padx=10, width=8)
    cmp_label.pack(side=tk.TOP)

    # blanklabel = tk.Label(win_lFrame1,text=" ")

    # blanklabel.pack()
    # cmp_label1 = tk.Label(win_lFrame1,text = 'CMP', font=('calibre',10,'normal'),padx=10)
    # cmp_label1.pack(side = tk.LEFT)

    scrip_var.set("NIFTY")
    scrip = ['NIFTY', 'BANKNIFTY'] + sorted(set(ms.NIFTY_100))
    scrip_options = tk.OptionMenu(scripFrame, scrip_var, *scrip)
    # level_options = ttk.Combobox( lFrame1 , textvariable=level_option_clicked , values=level_option_items)

    scrip_options.config(font=('calibre', 10))
    scripFrame.nametowidget(scrip_options.menuname).config(font=('calibre', 10))
    # scrip_options = tk.Entry(scripFrame,textvariable = scrip_var, font=('calibre',10,'normal'),width=12)
    scrip_options.pack(side=tk.BOTTOM)

    spot_entry = tk.Entry(spotFrame, textvariable=spot_var, font=('calibre', 10, 'normal'), width=12)
    spot_entry.pack(side=tk.BOTTOM)

    type_entry = tk.OptionMenu(typeFrame, type_var, *call_put, )
    typeFrame.nametowidget(type_entry.menuname).config(font=('calibre', 10))
    type_entry.pack(side=tk.BOTTOM)

    # expiry = Calendar(expiryFrame, selectmode = 'day',
    #                year = datetime.date.today().year, month = datetime.date.today().month,
    #                day = datetime.date.today().day)

    # expiry.pack(pady = 20)

    expiry_var = tkcalendar.DateEntry(expiryFrame, date_pattern='mm/dd/yyyy', locale='en_US')
    expiry_var.pack()

    strike_entry = tk.Entry(strikeFrame, textvariable=strike_var, font=('calibre', 10, 'normal'), width=12)
    strike_entry.pack(side=tk.BOTTOM)

    rate_entry = tk.Entry(rateFrame, textvariable=rate_var, font=('calibre', 10, 'normal'), width=12)
    rate_entry.pack(side=tk.BOTTOM)

    vol_entry = tk.Entry(volFrame, textvariable=vol_var, font=('calibre', 10, 'normal'), width=12)
    vol_entry.pack(side=tk.BOTTOM)

    cmp_entry = tk.Entry(cmpFrame, textvariable=cmp_var, font=('calibre', 10, 'normal'), width=12)
    cmp_entry.pack(side=tk.BOTTOM)


    # def setargs():
    args = {}
    args['scrip_var'] = scrip_var
    args['expiry'] = expiry_var
    # args['spot_var'] = spot_var.get()
    args['type_var'] = type_var
    # print(strike_var,strike_var.get())
    # args['strike_var'] = strike_var.get()
    # args['cmp_var'] = cmp_var.get()
    # args['vol_var'] = vol_var.get()
    # args['rate_var'] = rate_var.get()
        # analyze(win_lFrame2, args)

    option_button = tk.Button(win_lFrame1, text="Analyze",
                              font=('Poppins bold', 16), padx=10, pady=5,
                              command=lambda: analyze())

    inputtxt = None

    option_button.pack()

    win_option.mainloop()


inputtxt = None

def managelogin():
    top = tk.Toplevel(root)
    top.geometry("400x250")
    top.title("Login")
    login_label = tk.Label(top,text='Zerodha Auth Token')
    login_label.pack()
    inputtxt = tk.Text(top,
                       height=5,
                       width=150)

    inputtxt.pack()

    def login():
        token = inputtxt.get(1.0, "end-1c")
        kite_object.kiteLogin(token)
        print(token)
        top.destroy()
        login_button.destroy()
        refresh_login_button()

    log_button = tk.Button(top, text="Login", font=('Poppins bold', 14), command=login)
    log_button.pack()




# if __name__ == '__main__':
# create the main window
root = tk.Tk()
# root = tk.Toplevel()
root.title("Trade and Financial Analytics")
root.geometry("700x900")
root.resizable(width=False, height=False)


win = None

image = Image.open("mrigtrading1.png")

resize_image = image.resize((700, 90))
img = ImageTk.PhotoImage(resize_image)


Im = []

frame0 = tk.Frame(root,pady=10)
frame0.pack()


# start the main loop

lFrame0 = tk.LabelFrame(root, pady=10)
lFrame0.pack()

bg = tk.PhotoImage(file = "mrigtrading1.png",master=frame0)

label1 = tk.Label(lFrame0,text = 'Trading Analytics',
                  font=('Poppins bold', 16), padx=10,pady=5,fg='maroon')#,image=bg)
label1.pack()

frame1 = tk.Frame(root,pady=5)
frame1.pack()

blank1 = tk.Label(frame1,text= " ")
blank1.pack()

lFrame1 = tk.LabelFrame(root, pady=10)
lFrame1.pack()

label2 = tk.Label(lFrame1,text = 'Security Analytics',
                  font=('Poppins bold', 16), padx=10,pady=5,fg='maroon')
label2.pack()

option_button = tk.Button(lFrame1, text="Option", 
                        font=('Poppins bold', 14), padx=10,pady=5,
                        command=option_screen)
option_button.pack(side = tk.LEFT)

screener_button = tk.Button(lFrame1, text="TA Screener", 
                        font=('Poppins bold', 14), padx=10,pady=5,
                        command=ta_screen)
screener_button.pack(side = tk.LEFT)

level_option_clicked = tk.StringVar()
level_option_clicked.set( "NIFTY" )
level_option_items = ['NIFTY', 'BANKNIFTY'] + sorted(set(ms.NIFTY_100))
level_options = tk.OptionMenu( lFrame1 , level_option_clicked , *level_option_items)
# level_options = ttk.Combobox( lFrame1 , textvariable=level_option_clicked , values=level_option_items)

level_options.config(font=('Poppins bold', 12))
lFrame1.nametowidget(level_options.menuname).config(font=('Poppins bold', 10))

level_options.pack(side = tk.LEFT)

level_button = tk.Button(lFrame1, text="Level Analysis",
                        font=('Poppins bold', 14), padx=10,pady=5,
                        command=lambda :level_screen(level_option_clicked.get()))
level_button.pack(side = tk.LEFT)


frame2 = tk.Frame(root,pady=5)
frame2.pack()
blank2 = tk.Label(frame2,text= " ")
blank2.pack()

lFrame2 = tk.LabelFrame(root, pady=10)
lFrame2.pack(side=tk.BOTTOM)

label3 = tk.Label(lFrame2,text = 'Market Snapshot',
                  font=('Poppins bold', 16), padx=10,pady=5,fg='maroon')
label3.pack()


def bigger_snapshot(event):

    marketdb1 = tdb.tradingDB()
    market_graphs1 = marketdb1.market_snapshot()
    snapshot_win = tk.Tk()
    # snapshot_win = tk.Toplevel()
    snapshot_win.geometry("1050x900")
    snapshot_win.title('M A R K E T      S N A P S H O T')
    market_canvas1 = tk.Canvas(snapshot_win, width=900, height=900)
    # market_canvas1.create_line(15, 25, 200, 25)
    # nifty_chart1 = ImageTk.PhotoImage(nifty_chart.resize((300, 300)),master=market_canvas1)
    nifty_chart1 = ImageTk.PhotoImage(Image.open(market_graphs1[0][0]).resize((300, 300)),master=market_canvas1)
    Im.append(nifty_chart1)
    banknifty_chart1 = ImageTk.PhotoImage(Image.open(market_graphs1[0][1]).resize((300, 300)),master=market_canvas1)
    Im.append(banknifty_chart1)
    vix_chart1 = ImageTk.PhotoImage(Image.open(market_graphs1[0][2]).resize((300, 300)),master=market_canvas1)
    Im.append(vix_chart1)
    usdinr_chart1 = ImageTk.PhotoImage(Image.open(market_graphs1[0][3]).resize((300, 300)),master=market_canvas1)
    Im.append(usdinr_chart1)
    crude_chart1 = ImageTk.PhotoImage(Image.open(market_graphs1[0][4]).resize((300, 300)),master=market_canvas1)
    Im.append(crude_chart1)
    gold_chart1 = ImageTk.PhotoImage(Image.open(market_graphs1[0][5]).resize((300, 300)),master=market_canvas1)
    Im.append(gold_chart1)

    market_canvas1.create_image((200, 200), image=nifty_chart1)
    market_canvas1.create_image((520, 200), image=banknifty_chart1)
    market_canvas1.create_image((840, 200), image=vix_chart1)
    market_canvas1.create_image((200, 520), image=usdinr_chart1)
    market_canvas1.create_image((520, 520), image=crude_chart1)
    market_canvas1.create_image((840, 520), image=gold_chart1)
    market_canvas1.pack(fill="both", expand=True)


# placing the canvas on the Tkinter window
bottomframe = tk.Frame(root)
bottomframe.pack( side = tk.BOTTOM )
# create a button to display the DataFrame
file_button = tk.Button(lFrame0, text="Load Positions", 
                        font=('Poppins bold', 14), padx=10,pady=5,
                        command=load_DB)
file_button.pack(side = tk.LEFT)

# display_button = tk.Button(root, text="Display Analytics", command=display_analytics)
# display_button.pack()

display_button = tk.Button(lFrame0, text="Display Analytics", 
                           font=('Poppins bold', 14), padx=10,pady=5,
                           command=display_dataframe)
display_button.pack(side = tk.LEFT)

canvas1 = tk.Canvas(frame0, width = 700,height = 90)
  
canvas1.pack(fill = "both", expand = True)
  
# Display image
canvas1.create_image( 0, 0, image = img, 
                      anchor = "nw")

def small_snapshot():
    marketdb = tdb.tradingDB()
    market_graphs = marketdb.market_snapshot()

    nifty_chart = Image.open(market_graphs[0][0])
    banknifty_chart = Image.open(market_graphs[0][1])
    vix_chart = Image.open(market_graphs[0][2])
    usdinr_chart = Image.open(market_graphs[0][3])
    crude_chart = Image.open(market_graphs[0][4])
    gold_chart = Image.open(market_graphs[0][5])

    nifty_chart = ImageTk.PhotoImage(nifty_chart.resize((200, 180)))
    Im.append(nifty_chart)
    banknifty_chart = ImageTk.PhotoImage(banknifty_chart.resize((200, 180)))
    Im.append(banknifty_chart)
    vix_chart = ImageTk.PhotoImage(vix_chart.resize((200, 180)))
    Im.append(vix_chart)
    usdinr_chart = ImageTk.PhotoImage(usdinr_chart.resize((200, 180)))
    Im.append(usdinr_chart)
    crude_chart = ImageTk.PhotoImage(crude_chart.resize((200, 180)))
    Im.append(crude_chart)
    gold_chart = ImageTk.PhotoImage(gold_chart.resize((200, 180)))
    Im.append(gold_chart)

    market_canvas = tk.Canvas(lFrame2, width=700, height=600)
    market_canvas.create_image((140, 100), image=nifty_chart)
    market_canvas.create_image((350, 100), image=banknifty_chart)
    market_canvas.create_image((560, 100), image=vix_chart)
    market_canvas.create_image((140, 300), image=usdinr_chart)
    market_canvas.create_image((350, 300), image=crude_chart)
    market_canvas.create_image((560, 300), image=gold_chart)
    market_canvas.bind("<Double-Button-1>", bigger_snapshot)
    market_canvas.pack(fill="both", expand=True)

def refresh_login_button():
    global login_button
    if kite_object.getStatus() == 1:
        vendor_connection = "Zerodha \n Active"
        small_snapshot()
        fg = None
    else:
        vendor_connection = "Zerodha \n InActive"
        fg='Red'


    login_button = tk.Button(frame0, text=vendor_connection, font=('Poppins bold', 12),fg=fg)
    login_button['state'] = tk.DISABLED
    login_button.place(x=520,y=20)
    if kite_object.getStatus() == 1:
        login_button['disabledforeground'] = 'darkgreen'

refresh_login_button()

close_button = tk.Button(frame0, text= "Close", font=('Poppins bold', 14), command=close_root)
close_button.place(x=620,y=25)
# close_button.pack(side = tk.LEFT)


    # marketdb = tdb.tradingDB()
    # market_graphs = marketdb.market_snapshot()


if kite_object.getStatus() == 1:
    small_snapshot()


root.mainloop()