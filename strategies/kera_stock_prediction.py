#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 13:36:17 2018

@author: Devang
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import mrigutilities as mu
import datetime, dateutil
#Importing Libraries  
import numpy as np
import pandas as pd
import stockstats as ss

#Setting the random seed to a fixed number
import random
random.seed(42)

#Importing the dataset
stocksymbol = 'HDFCBANK'
enddate = datetime.date.today()
startdate = enddate - dateutil.relativedelta.relativedelta(years=3)
dataset = mu.getStockData(stocksymbol,startdate,enddate)

#dataset = dataset.dropna()
#print(dataset)

dataset = dataset[['open', 'high', 'low', 'close_adj']]
dataset.rename(columns={'close_adj':'close'}, inplace=True) 
#dataset.rename(columns={"open":"Open"}, inplace=True) 
#dataset.rename(columns={"low":"Low"}, inplace=True) 
#dataset.rename(columns={"high":"High"}, inplace=True)    
#print(dataset)
print(dataset.head(5))
ss_dataset = ss.StockDataFrame.retype(dataset)
#Preparing the dataset
dataset['H-L'] = dataset['high'] - dataset['low']
dataset['O-C'] = dataset['close'] - dataset['open']
dataset['3day MA'] = dataset['close'].shift(1).rolling(window = 3).mean()
dataset['10day MA'] = dataset['close'].shift(1).rolling(window = 10).mean()
dataset['30day MA'] = dataset['close'].shift(1).rolling(window = 30).mean()
dataset['Std_dev']= dataset['close'].rolling(5).std()
#dataset['RSI'] = talib.RSI(dataset['close'].values, timeperiod = 9)
#dataset['Williams %R'] = talib.WILLR(dataset['High'].values, dataset['Low'].values, dataset['close'].values, 7)

dataset['RSI'] = ss_dataset.get('rsi_9')
dataset['Williams %R'] = ss_dataset.get('wr_7')


dataset['Price_Rise'] = np.where(dataset['close'].shift(-1) > dataset['close'], 1, 0)

dataset = dataset.dropna()
dataset.drop(['close_-1_s','close_-1_d','rs_9','rsi_9','wr_7'],axis=1,inplace=True)
print(dataset.head(5))
X = dataset.iloc[:, 4:-1]
y = dataset.iloc[:, -1]

#Splitting the dataset
split = int(len(dataset)*0.8)
X_train, X_test, y_train, y_test = X[:split], X[split:], y[:split], y[split:]

#print(X)
#print(X_train)
#Feature Scaling
from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

#Building the Artificial Neural Network
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout

classifier = Sequential()

classifier.add(Dense(
        units = 128, 
        kernel_initializer = 'uniform', 
        activation = 'relu', 
        input_dim = X.shape[1]
        ))
classifier.add(Dense(
        units = 128, 
        kernel_initializer = 'uniform', 
        activation = 'relu'
        ))
classifier.add(Dense(
        units = 1, 
        kernel_initializer = 'uniform', 
        activation = 'sigmoid'
        ))
classifier.compile(
                   optimizer = 'adam', 
                   loss = 'mean_squared_error', 
                   metrics = ['accuracy']
                   )

classifier.fit(X_train, y_train, batch_size = 10, epochs = 200)

scores = classifier.evaluate(X_train,y_train)
#Predicting the movement of the stock
y_pred = classifier.predict(X_test)
y_pred = (y_pred > 0.5)

dataset['y_pred'] = np.NaN
dataset.iloc[(len(dataset) - len(y_pred)):,-1:] = y_pred
trade_dataset = dataset.dropna()

#Computing Strategy Returns
trade_dataset['Tomorrows Returns'] = 0.
trade_dataset['Tomorrows Returns'] = np.log(trade_dataset['close']/trade_dataset['close'].shift(1))
trade_dataset['Tomorrows Returns'] = trade_dataset['Tomorrows Returns'].shift(-1)

trade_dataset['Strategy Returns'] = 0.
trade_dataset['Strategy Returns'] = np.where(
                    trade_dataset['y_pred'] == True, 
                    trade_dataset['Tomorrows Returns'], 
                    - trade_dataset['Tomorrows Returns']
                    )

trade_dataset['Cumulative Market Returns'] = np.cumsum(trade_dataset['Tomorrows Returns'])
trade_dataset['Cumulative Strategy Returns'] = np.cumsum(trade_dataset['Strategy Returns'])

#Plotting the graph of returns
import matplotlib.pyplot as plt
plt.figure(figsize=(10,5))
plt.plot(trade_dataset['Cumulative Market Returns'], color='r', label='Market Returns')
plt.plot(trade_dataset['Cumulative Strategy Returns'], color='g', label='Strategy Returns')
plt.legend()
plt.show()
print(trade_dataset[['close','y_pred','Price_Rise','Tomorrows Returns','Strategy Returns']])
print(scores[1]*100)