# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 20:05:05 2018

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import mrigutilities as mu
import datetime, dateutil
import numpy as np
import matplotlib.pyplot as plt

#importing required libraries
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM

#creating dataframe
stocksymbol = 'HDFCBANK'
enddate = datetime.date.today()
startdate = enddate - dateutil.relativedelta.relativedelta(years=3)
dataset = mu.getStockData(stocksymbol,startdate,enddate)

dataset = dataset['close_adj']
new_data = dataset
#dataset.rename(columns={'close_adj':'close'}, inplace=True)
#data = df.sort_index(ascending=True, axis=0)
#new_data = pd.DataFrame(index=range(0,len(df)),columns=['Date', 'Close'])
#for i in range(0,len(data)):
#    new_data['Date'][i] = data['Date'][i]
#    new_data['close'][i] = data['close'][i]
#
##setting index
#new_data.index = new_data.Date
#new_data.drop('Date', axis=1, inplace=True)

#creating train and test sets
dataset = dataset.values

train = dataset[0:300,]
valid = dataset[300:,]

#converting dataset into x_train and y_train
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(dataset)

x_train, y_train = [], []
for i in range(60,len(train)):
    x_train.append(scaled_data[i-60:i,])
    y_train.append(scaled_data[i:,])
x_train, y_train = np.array(x_train), np.array(y_train)

x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1]))
#y_train = np.reshape(y_train,(y_train.shape[0],1))

# create and fit the LSTM network
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1],1)))
model.add(LSTM(units=50))
model.add(Dense(1))

model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(x_train, y_train, epochs=1, batch_size=1, verbose=2)

#predicting 246 values, using past 60 from the train data
inputs = new_data[len(new_data) - len(valid) - 60:].values
inputs = inputs.reshape(-1,1)
inputs  = scaler.transform(inputs)

X_test = []
for i in range(60,inputs.shape[0]):
    X_test.append(inputs[i-60:i,])
X_test = np.array(X_test)

X_test = np.reshape(X_test, (X_test.shape[0],X_test.shape[1],1))
closing_price = model.predict(X_test)
closing_price = scaler.inverse_transform(closing_price)

valid['Predictions'] = 0 
valid['Predictions'] = closing_price
rms=np.sqrt(np.mean(np.power((np.array(valid['close'])-np.array(valid['Predictions'])),2)))


#for plotting
train = new_data[:300]
valid = new_data[300:]

plt.plot(train['close'])
plt.plot(valid[['close','Predictions']])
