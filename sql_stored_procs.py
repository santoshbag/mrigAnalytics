# -*- coding: utf-8 -*-
"""
Created on Sat Sep  8 15:46:04 2018

@author: Santosh Bag
"""

import sys
import nsepy
import datetime #import date, timedelta
from pandas import DataFrame
from sqlalchemy import create_engine
import mrigutilities

engine = mrigutilities.sql_engine()
#cur = engine.connect().connection.cursor()
calculate_returns_sql = "update stock_history set symbol='PVP' where symbol='PVP'"
engine.execute(calculate_returns_sql)
#cur.callproc(calculate_returns_sql)


