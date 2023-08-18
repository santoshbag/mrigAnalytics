# -*- coding: utf-8 -*-
"""
Created on Fri May  5 10:45:34 2023

@author: Santosh Bag
"""

from distutils.core import setup
from setuptools import  find_packages

import py2exe


setup(console = ['tradingDB_GUI.py'],
      options = {"py2exe" : { "excludes" : ['old', 'data', 'media', 'mrigweb', 'research', 'interface', 'strategies', 'instruments', 'maintenance', 'sql_queries'],
                  "includes"  :['mrigutilities']}},
      packages=find_packages() + find_packages(where='', 
                                exclude=['old', 'data', 'media', 'mrigweb', 'research', 'interface', 'strategies', 'instruments', 'maintenance', 'sql_queries']),
      )