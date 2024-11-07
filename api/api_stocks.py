#  Copyright (c) 2024.
import datetime
import sys,os

import dateutil
import numpy as np
import pandas_ta as ta
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from rest_framework import serializers
import mrigutilities as mu

class StockAPI1():
    def __init__(self, name,levelFlag=False,period='3m'):
        self.symbol = name
        self.get_price_vol(levelFlag,period)
    def get_price_vol(self, levelFlag=False,period='1Y'):
        today = datetime.date.today()
        years = 0
        months = 0
        weeks = 0
        days = 0

        if period[-1].upper() == 'Y':
            years = int(period[:-1])
        if period[-1].upper() == 'M':
            months = int(period[:-1])
        if period[-1].upper() == 'W':
            weeks = int(period[:-1])
        if period[-1].upper() == 'D':
            days = int(period[:-1])

        startdate = today - dateutil.relativedelta.relativedelta(years=years,
                                                                 months=months,
                                                                 weeks=weeks,
                                                                 days=days)
        #        print(startdate)
        self.pricevol_data = mu.getStockData(self.symbol,
                                             startdate,
                                             today)
        self.pricevol_data['daily_logreturns'] = np.log(
            self.pricevol_data['close_adj'] / self.pricevol_data['close_adj'].shift(1))

        sma_20 = ta.sma(self.pricevol_data['close'],length=20)
        sma_60 = ta.sma(self.pricevol_data['close'],length=60)
        sma_100 = ta.sma(self.pricevol_data['close'],length=100)

        # print(sma.columns)
        self.pricevol_data = pd.merge(self.pricevol_data, sma_20, left_index=True, right_index=True)
        self.pricevol_data = pd.merge(self.pricevol_data, sma_60, left_index=True, right_index=True)
        self.pricevol_data = pd.merge(self.pricevol_data, sma_100, left_index=True, right_index=True)

        # print(self.pricevol_data.columns)

class StockPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAPI1
        fields = '__all__'



