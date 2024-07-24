# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 17:37:47 2018

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import mrigutilities as mu
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import research.math as rm
import research.analytics as ra

class Strategy():
    def __init__(self):
        self.name = "Strategy"

class st_macd(Strategy):
    def __init__(self):
        self.name = "SUPERTREND and MACD Strategy"
        self.signals = pd.DataFrame()
        self.positions = pd.DataFrame()
        self.portfolio = pd.DataFrame()

    def getSignals(self):
        stocksdf = pd.DataFrame()
        TA = ra.display_tech_analysis()
        print('TA --------',TA)
        for stock in sorted(set(TA['symbol'])):
            print(stock)
            df = TA[TA['symbol'] == stock].tail(5)
            df['opinion'] = 'NAL'
            # try:
            if len(df) > 3:
                # print(df[['symbol','close','SUPERT_7_3.0',  'SUPERTd_7_3.0','MACD_12_26_9','opinion']])
                df = pd.DataFrame() if (
                            df.head(1)['SUPERTd_7_3.0'].values[0] == df.tail(1)['SUPERTd_7_3.0'].values[0]) else df
                if len(df.columns) > 0:
                    # print(df[['symbol','close','SUPERT_7_3.0',  'SUPERTd_7_3.0','MACD_12_26_9','opinion']])
                    if ((df.tail(1)['MACD_12_26_9'].values[0] > 0) and (df.tail(1)['SUPERTd_7_3.0'].values[0] > 0)):
                        # print('BUY')
                        df['opinion'] = 'BUY'
                        df = df.tail(1)
                    elif ((df.tail(1)['MACD_12_26_9'].values[0] < 0) and (df.tail(1)['SUPERTd_7_3.0'].values[0] < 0)):
                        df['opinion'] = 'SELL'
                        df = df.tail(1)
                        # print('SELL')
                    elif ((df.tail(1)['MACD_12_26_9'].values[0] > 0) and (df.tail(1)['SUPERTd_7_3.0'].values[0] < 0)):
                        df['opinion'] = 'CAUTIOUS SELL'
                        df = df.tail(1)
                        # print('SELL')
                    elif ((df.tail(1)['MACD_12_26_9'].values[0] < 0) and (df.tail(1)['SUPERTd_7_3.0'].values[0] > 0)):
                        df['opinion'] = 'CAUTIOUS BUY'
                        df = df.tail(1)
                        # print('SELL')
                    else:
                        df['opinion'] = 'NA'
            # except:
            # pass
            # print(df.head(1)['SUPERTd_7_3.0'].values,df.tail(1)['SUPERTd_7_3.0'].values)
            stocksdf = pd.concat([stocksdf,df])
        stocksdf = stocksdf[['symbol', 'close', 'SUPERT_7_3.0', 'SUPERTd_7_3.0', 'MACD_12_26_9', 'opinion']]
        # print(stocksdf)
        self.signals = stocksdf
        return stocksdf

class Momentum(Strategy):
    def __init__(self):
        self.name = "Momentum Strategy"
        self.signals = pd.DataFrame()
        self.positions = pd.DataFrame()
        self.portfolio = pd.DataFrame()

class MovingCrossover(Momentum):
    def __init__(self,symbol,short_lookback=40,long_lookback=100):
        Momentum.__init__(self)
        self.symbol = symbol
        self.short_lookback = short_lookback
        self.long_lookback = long_lookback
        self.end_date = datetime.date.today()
        self.start_date = self.end_date - datetime.timedelta(days=long_lookback)
        
    def implement(self):
        self.symbol_data = mu.getStockData(self.symbol,
                                           self.start_date,
                                           self.end_date)
        
        if self.symbol == 'BAJFINANCE':
            for i in self.symbol_data.index:
                if i >= datetime.date(2016,9,8):
                    self.symbol_data.loc[i,'close'] = self.symbol_data.loc[i,'close']*10
        
        if not self.symbol_data.empty:
            # Initialize the `signals` DataFrame with the `signal` column
            self.signals = pd.DataFrame(index=self.symbol_data.index)
            #self.signals = symbol_data
            self.signals['signal'] = 0.0
            
            # Create short simple moving average over the short window
            self.signals['short_mavg'] = self.symbol_data['close'].rolling(window=self.short_lookback,
                                                                            min_periods=1,
                                                                            center=False).mean()
    
            # Create long simple moving average over the long window
            self.signals['long_mavg'] = self.symbol_data['close'].rolling(window=self.long_lookback,
                                                                            min_periods=1, 
                                                                            center=False).mean()
    
            # Create signals
            self.signals['signal'][self.short_lookback:] = np.where(self.signals['short_mavg'][self.short_lookback:] > self.signals['long_mavg'][self.short_lookback:], 1.0, 0.0)
            
            # Generate trading orders
            self.signals['positions'] = self.signals['signal'].diff()
            return True
        else:
            print("No Data for "+ self.symbol)
            return False
    
    def pnl(self):
        if not self.signals.empty:
            # Set the initial capital
            initial_capital= float(1000000.0)
            
            # Create a DataFrame `positions`
            self.positions = pd.DataFrame(index=self.signals.index).fillna(0.0)
            
            # Buy a 100 shares
            self.positions[self.symbol] = 100*self.signals['signal']   
              
            # Initialize the portfolio with value owned   
            self.portfolio = self.positions.multiply(self.symbol_data['close'], axis=0)
            
            # Store the difference in shares owned 
            pos_diff = self.positions.diff()
            
            # Add `holdings` to portfolio
            self.portfolio['holdings'] = (self.positions.multiply(self.symbol_data['close'], axis=0)).sum(axis=1)
            
            # Add `cash` to portfolio
            self.portfolio['cash'] = initial_capital - (pos_diff.multiply(self.symbol_data['close'], axis=0)).sum(axis=1).cumsum()   
            
            # Add `total` to portfolio
            self.portfolio['total'] = self.portfolio['cash'] + self.portfolio['holdings']
            
            # Add `returns` to portfolio
            self.portfolio['returns'] = self.portfolio['total'].pct_change()
            print("Final Portfolio Value is %s"%self.portfolio['total'][-1])
            
            investment_period = (self.signals.index[-1] - (self.signals['positions'] == 1).idxmax()).days
            
            self.cagr = (self.symbol_data.loc[self.signals.index[-1]]['close']/self.symbol_data.loc[(self.signals['positions'] == 1).idxmax()]['close'])**(365/investment_period) -1 
            print("CAGR is %s" %'{0:.2%}'.format(self.cagr)) 
            
            self.sharpe_ratio = np.sqrt(252)*(self.portfolio['returns'].mean()/self.portfolio['returns'].std())
            print("Sharpe Ratio is %s" %'{0:.2}'.format(self.sharpe_ratio))
            
            # Create a figure
            fig = plt.figure()
            
            ax1 = fig.add_subplot(111, ylabel='Portfolio value in Rs')
            ax2 = ax1.twinx()
            ax2.set_ylabel('Price')
            
            # Plot the equity curve in dollars
            self.portfolio['total'].plot(ax=ax1,grid=True,color='g', lw=2.)
            self.signals[['short_mavg','long_mavg']].plot(ax=ax2,grid=True,lw=2.)
            
            ax1.plot(self.portfolio.loc[self.signals.positions == 1.0].index, 
                     self.portfolio.total[self.signals.positions == 1.0],
                     '^', markersize=10, color='m')
            ax1.plot(self.portfolio.loc[self.signals.positions == -1.0].index, 
                     self.portfolio.total[self.signals.positions == -1.0],
                     'v', markersize=10, color='k')
            
            # Show the plot
            plt.show()        
                    
            #pnl = np.sum(self.signals['close'][1:]*self.signals['positions'][1:])
            #capital = self.signals.loc[(self.signals['positions'] == 1).idxmax()]['close']
            #return self.portfolio
            return True
        else:
            print("No Data for "+ self.symbol)
            return False
    
    def backtest(self,start_date,end_date):
        self.start_date = start_date
        self.end_date = end_date
        if self.implement():
            print(self.signals.loc[(self.signals['positions'] != 0)]['positions'])
        #   self.signals[['positions','close','short_mavg','long_mavg']].plot(grid=True)
            self.pnl()


        
if __name__ == '__main__':
    sd = datetime.date(2017,5,31)
    ed = datetime.date(2018,11,18)
    # trades1 = MovingCrossover('HDFCBANK',60,90)
    # trades1.backtest(sd,ed)
    # trades2 = MovingCrossover('MARUTI',60,90)
    # #trades2.backtest(sd,ed)
    #
    # rm.isNormal(np.array(list(trades2.portfolio['returns'])))
    #rm.linreg(trades1.portfolio['returns'][1:519].values,trades2.portfolio['returns'][1:519].values)


    