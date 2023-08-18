# -*- coding: utf-8 -*-
"""
Created on Tue May  2 13:13:44 2023

@author: Santosh Bag
"""

import tkinter as tk
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# define a function to display the analytics for the selected stock
def display_analytics():
    # get the stock name from the entry box
    stock_name = stock_entry.get()
    
    # get the stock data from Yahoo Finance using pandas_datareader
    # data = pdr.get_data_yahoo(stock_name)
    data = yf.download(stock_name,period='1y')
    macd = ta.macd(data['Close'])
    print(data)
    data = pd.merge(data,macd,left_index=True,right_index=True)
    # create a new window to display the analytics
    window = tk.Toplevel(root)
    window.title("Stock Analytics")
    
    # create a figure to display the stock price chart
    figure = plt.Figure(figsize=(6, 4), dpi=100)
    ax = figure.add_subplot(111)
    ax1 = figure.add_subplot(222)
    ax.plot(data[['Close']])
    ax1.plot(data[['MACD_12_26_9','MACDs_12_26_9']])
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.set_title(f"{stock_name} Stock Price Chart")
    canvas = FigureCanvasTkAgg(figure, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()

    # calculate the mean, median, and standard deviation of the stock price
    mean = data['Close'].mean()
    median = data['Close'].median()
    std_dev = data['Close'].std()

    # create a label to display the mean, median, and standard deviation
    analytics_label = tk.Label(window, text=f"Mean: {mean:.2f}\nMedian: {median:.2f}\nStandard Deviation: {std_dev:.2f}")
    analytics_label.pack()

# create the main window
root = tk.Tk()
root.title("Stock Analytics")

# create a label and entry box to input the stock name
stock_label = tk.Label(root, text="Enter Stock Name:")
stock_label.pack()
stock_entry = tk.Entry(root)
stock_entry.pack()

# create a button to show the analytics for the selected stock
analytics_button = tk.Button(root, text="Show Analytics", command=display_analytics)
analytics_button.pack()

# start the main loop
root.mainloop()
