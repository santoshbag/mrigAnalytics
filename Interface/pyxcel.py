# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 16:46:14 2018

@author: Santosh Bag
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import xlwings as xw
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d import Axes3D
import datetime
import QuantLib as ql
import mrigutilities as mu
from pywintypes import Time
import matplotlib.pyplot as plt
import matplotlib



@xw.func
@xw.arg('isinlist', ndim=1, transpose=True)
@xw.ret(expand='table', transpose=False)
def mrigxl_getMFNAV(reference_date, isinlist=None):
    
    nav_df = mu.getMFNAV(reference_date,isinlist)
    nav_df.drop(['Fund House','Scheme Type'],axis=1,inplace=True)
    #nav_df.drop('Scheme Type',axis=1)
    nav_df.reset_index(level=0, inplace=True)
    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    return nav_df
    
@xw.func
@xw.ret(expand='table', transpose=False)
def mrigxl_getStockData(symbol,start_date,end_date):
    
    stock_df = mu.getStockData(symbol,start_date,end_date)
#    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    return stock_df

