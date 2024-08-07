# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 11:22:01 2023

@author: Santosh Bag
"""

import sys,os
import time
import webbrowser

import mrigstatics
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'data'))
# sys.path.append(os.path.join(os.path.dirname(__file__), 'mrigweb'))
# sys.path.append(os.path.join(os.path.dirname(__file__), 'mrigweb','mrigwebapp'))

import datetime #import date, timedelta
import pandas as pd #import DataFrame
#from sqlalchemy import create_engine
import threading
import mrigutilities
from data import datarun as drun
from data import webserver_load as wload
from data import stockHistoryNew as sh
from kite import mrigkite as mk
from data import mutual_funds as mf
from data import financial_results as fr

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

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
NavigationToolbar2Tk)
import tkcalendar

from PIL import Image, ImageTk

from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QHeaderView


import kite.kite_account as ka

# kite_object = ka.kite_account()
kite_object = mk.mrigkite()

# today = datetime.date.today()
today = datetime.datetime.now()
engine = mrigutilities.sql_engine()
engine_mrigweb = mrigutilities.sql_engine(dbname=mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])

def close_root():
    root.destroy()
    win.destroy()



inputtxt = None
api_key_input = None
api_secret_input = None

def managelogin():
    top = tk.Toplevel(root)
    top.geometry("400x250")
    top.title("Login")
    login_label = tk.Label(top,text='Zerodha Auth Token')
    login_label.pack()

    login_url_label = tk.Label(top,text='Click URL to get access token',cursor= "hand2", foreground= "green")
    login_url_label.pack()


    inputtxt = tk.Text(top,
                       height=5,
                       width=150)

    inputtxt.pack()

    def open_url(url):
        webbrowser.open_new_tab(url)

    login_url_label.bind("<Button-1>", lambda e: open_url(kite_object.login_url
                                                          ))
    def login():
        token = inputtxt.get(1.0, "end-1c")
        kite_object.kite_login(token)
        top.destroy()
        login_button.destroy()
        refresh_login_button()

    log_button = tk.Button(top, text="Login", font=('Poppins bold', 14), command=login)
    log_button.pack()

def credentials():
    top = tk.Toplevel(root)
    top.geometry("400x250")
    top.title("ZERODHA API KEYS")
    cred_label1 = tk.Label(top,text='ZERODHA API KEY')
    cred_label1.pack()
    api_key_input = tk.Text(top,
                       height=2,
                       width=150)

    api_key_input.pack()
    cred_label2 = tk.Label(top,text='ZERODHA API SECRET')
    cred_label2.pack()

    api_secret_input = tk.Text(top,
                       height=2,
                       width=150)

    api_secret_input.pack()

    def cred():
        cred = {}
        cred['api_key'] = api_key_input.get(1.0, "end-1c")
        cred['api_secret'] = api_secret_input.get(1.0, "end-1c")

        kite_object.set_credentials(cred)
        top.destroy()
        submit_button.destroy()
        # refresh_login_button()

    submit_button = tk.Button(top, text="Submit", font=('Poppins bold', 14), command=cred)
    submit_button.pack()


def data_status():
    stock_date = pd.read_sql("select series as item,max(date) as last_date from stock_history where series in ('EQ','IN') group by series", engine)
    fo_date = pd.read_sql("select 'FO' as item,max(date) as last_date from futures_options_history", engine)
    ins_date = pd.read_sql("select 'MI' as item,max(instrument_date) as last_date from market_instruments", engine)
    mf_date = pd.read_sql("select 'MF' as item ,max(nav_date) as last_date from mf_history", engine)
    webpage_date = pd.read_sql("select 'WEBPG' as item, max(load_date) as last_date from webpages", engine_mrigweb)
    # df = pd.concat([stock_date, fo_date, mf_date, webpage_date]).set_index('item').transpose()
    df = pd.concat([stock_date, fo_date,ins_date, mf_date, webpage_date])
    df['last_date'] = df['last_date'].apply(lambda x: x.strftime('%d-%b-%Y'))
    df = df.set_index('item').transpose()
    # df = [list(df), df.values.tolist()[0]]
    return df

def daily_datarun():
    drun.daily_datarun()

def webserver_load():
    wload.market_db_load()
    wload.mrigweb_stock_load()

def results_load():
    fr.results_download_all()

def adHoc_stock():
    # sdate = datetime.datetime.strptime(startcal.get_date(),'%Y/%m/%d')
    # edate = datetime.datetime.strptime(endcal.get_date(), '%Y/%m/%d')
    sdate = startcal.get_date()
    edate = endcal.get_date()
    sh.stockHistoryNew_download(sdate,edate)

def adHoc_mf():
    wload.market_db_load()
    wload.mrigweb_stock_load()

# def django_start():
#     thread = threading.Thread(target=manage.mrigserverstart())
#     thread.start()
# def start_new_thread():
#     thread = threading.Thread(target=django_start)
#     thread.start()

# if __name__ == '__main__':
# create the main window
root = tk.Tk()
# root = tk.Toplevel()
root.title("Mrig Analytisc Administration")
root.geometry("900x500")
root.resizable(width=False, height=False)


win = None

image = Image.open("mrigtrading1.png")

resize_image = image.resize((900, 90))
img = ImageTk.PhotoImage(resize_image)


Im = []

frame0 = tk.Frame(root,pady=10)
frame0.pack()


# start the main loop

lFrame0 = tk.LabelFrame(root, pady=10)
lFrame0.pack()

bg = tk.PhotoImage(file = "mrigtrading1.png",master=frame0)

label1 = tk.Label(lFrame0,text = 'Mrig Analytics Administration',
                  font=('Poppins bold', 16), padx=10,pady=5,fg='maroon')#,image=bg)
label1.pack()

label2 = tk.Label(lFrame0,text = '('+today.strftime('%d-%b-%Y')+')',
                  font=('Poppins bold', 12), padx=10,pady=2,fg='maroon')#,image=bg)
label2.pack()


# create a button to display the DataFrame
dailyrun_button = tk.Button(lFrame0, text="Daily Datarun",
                        font=('Poppins bold', 12), padx=10,pady=5,
                        command=daily_datarun)
dailyrun_button.pack(side = tk.LEFT)

# display_button = tk.Button(root, text="Display Analytics", command=display_analytics)
# display_button.pack()

webload_button = tk.Button(lFrame0, text="Web Server Load",
                           font=('Poppins bold', 12), padx=10,pady=5,
                           command=webserver_load)
webload_button.pack(side = tk.LEFT)

resload_button = tk.Button(lFrame0, text="Results Load",
                           font=('Poppins bold', 12), padx=10,pady=5,
                           command=results_load)
resload_button.pack(side = tk.LEFT)

stock_button = tk.Button(lFrame0, text="AdHoc Stock Load",
                        font=('Poppins bold', 12), padx=10,pady=5,
                        command=adHoc_stock)
stock_button.pack(side = tk.LEFT)

# display_button = tk.Button(root, text="Display Analytics", command=display_analytics)
# display_button.pack()

mf_button = tk.Button(lFrame0, text="AdHoc MF Load",
                           font=('Poppins bold', 12), padx=10,pady=5,
                           command=webserver_load)
mf_button.pack(side = tk.LEFT)

# django_button = tk.Button(lFrame0, text="Mrig Django",
#                            font=('Poppins bold', 12), padx=10,pady=5,
#                            command=django_start)
# django_button.pack(side = tk.LEFT)

canvas1 = tk.Canvas(frame0, width = 900,height = 90)
  
canvas1.pack(fill = "both", expand = True)
  
# Display image
canvas1.create_image( 0, 0, image = img, 
                      anchor = "nw")


def refresh_login_button():
    global login_button
    if kite_object.getStatus() == 1:
        vendor_connection = "Zerodha \n Active"
        fg = None
    else:
        vendor_connection = "Zerodha \n InActive"
        fg='Red'


    login_button = tk.Button(frame0, text=vendor_connection, font=('Poppins bold', 12),fg=fg, command=managelogin)
    login_button.place(x=620,y=20)
    if kite_object.getStatus() == 1:
        login_button['state'] = tk.DISABLED
        login_button['disabledforeground'] = 'darkgreen'

refresh_login_button()

cred_button = tk.Button(frame0, text='Set \n Credential', font=('Poppins bold', 12), command=credentials)
cred_button.place(x=720,y=20)

refresh_login_button()

close_button = tk.Button(frame0, text= "Close", font=('Poppins bold', 14), command=close_root)
close_button.place(x=820,y=25)
# close_button.pack(side = tk.LEFT)

blank_Frame = tk.LabelFrame(root, pady=20)
blank_Frame.pack()

df = data_status()
status = ""
for col in df.columns:
    status = status +  ' || '+col+' - '+df[col].values
dtable0 = tk.Entry(blank_Frame,width=100,font=('Poppins bold', 12),justify='center')
dtable0.grid(rows=1,columns=1)
dtable0.insert(tk.END,status)
dtable0.pack()

# for i in range(1,len(df)):
#     for j in range(1,len(df[0])):
#     # print(col,colnum)
#         dtable0 = tk.Entry(blank_Frame,width=15,font=('Poppins bold', 10))
#         dtable0.grid(rows=i,columns=j)
#         dtable0.insert(tk.END,df[i-1][j-1])
        # dtable1 = tk.Entry(blank_Frame,width=15,font=('Poppins bold', 10))
        # dtable1.grid(rows=2,columns=colnum)
        # dtable1.insert(tk.END,df[col].values[0].strftime('%d-%m-%Y'))


# blanklabel = tk.Label(blank_Frame, text='              ', pady=5)
# blanklabel.pack()

lFrame1 = tk.LabelFrame(root)
lFrame1.pack()


lFrame1_1 = tk.LabelFrame(lFrame1,  padx=10,pady=10)
lFrame1_1.pack(side=tk.LEFT)
label1_1 = tk.Label(lFrame1_1,text = 'Start Date',
                  font=('Poppins bold', 16), padx=10,pady=5,fg='maroon')#,image=bg)
label1_1.pack()

lFrame1_2 = tk.LabelFrame(lFrame1, padx=10,pady=10)
lFrame1_2.pack(side=tk.LEFT)
label1_2 = tk.Label(lFrame1_2,text = 'End Date',
                  font=('Poppins bold', 16), padx=10,pady=5,fg='maroon')#,image=bg)
label1_2.pack()


# endcal= tkcalendar.Calendar(lFrame2, firstweekday='sunday',
#                          selectmode="day",
#                          showweeknumbers=False ,
#                          date_pattern='y/mm/dd',
#                          year=datetime.date.today().year ,
#                          month=datetime.date.today().month,
#                          day=datetime.date.today().day)

endcal= tkcalendar.DateEntry(lFrame1_2, firstweekday='sunday',
                         selectmode="day",
                         showweeknumbers=False ,
                         date_pattern='y/mm/dd')

# startcal= tkcalendar.Calendar(lFrame1, firstweekday='sunday',
#                          selectmode="day",
#                          showweeknumbers=False ,
#                          date_pattern='y/mm/dd')

startcal= tkcalendar.DateEntry(lFrame1_1, firstweekday='sunday',
                         selectmode="day",
                         showweeknumbers=False ,
                         date_pattern='y/mm/dd',
                         year=(datetime.date.today() - datetime.timedelta(days=1)).year ,
                         month=(datetime.date.today() - datetime.timedelta(days=1)).month,
                         day=(datetime.date.today() - datetime.timedelta(days=1)).day
                               )

    # marketdb = tdb.tradingDB()
    # market_graphs = marketdb.market_snapshot()

endcal.pack(side=tk.LEFT)
startcal.pack(side=tk.LEFT)

root.mainloop()