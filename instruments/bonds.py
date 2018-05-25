# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 11:20:48 2016

@author: sbag
"""

from QuantLib import Bond
from portfolio import Product

class Bond(Product):
    def __init__(self,name=Bond1):
        self.issue_name = name
        self.security_type = "Bond"
        
    def setupBond(self,setupparams):
        self.issue_date = setupparams['issue_date']
        self.maturity_date = setupparams['maturity_date']
        self.coupon_frequency = setupparams['coupon_frequency']
        self.day_count = setupparams['day_count']
        

