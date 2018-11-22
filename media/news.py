# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 17:15:53 2018

This module deals with News from Money Control and Other websites
@author: Santosh Bag
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import requests
import datetime,pandas,time
from bs4 import BeautifulSoup
import mrigstatics,mrigutilities
import xml.etree.ElementTree as ET


def get_MCNews():
    
    for urlkey in mrigstatics.MC_MEDIA_URLS.keys():
        url = mrigstatics.MC_MEDIA_URLS[urlkey]
        s = requests.Session()
        response = s.get(url)
    
        tree = ET.fromstring(response.text)
        recos = []
        desc = []
        recodates = []
        for child in tree.iter('pubDate'):
            recodates.append(datetime.datetime.strptime((child.text[5:7]+"-"+child.text[8:11]+"-"+child.text[12:16]),'%d-%b-%Y'))
        for child in tree.iter('title'):
            recos.append(child.text)
        for child in tree.iter('description'):
            desc.append(child.text[child.text.find('/>')+3:])
        
        re = []
        for i in range(0,len(recos[2:])):
            re.append([recodates[i],recos[i+2],desc[i+2],urlkey[3:-4]])
        
        recos = pandas.DataFrame(re,columns=["date","title","description","type"])
        engine = mrigutilities.sql_engine()
        try:
            recos.to_sql('media',engine, if_exists='append', index=False)
        except:
            pass
            
        print(recos)

def get_ETNews():
    
    for urlkey in mrigstatics.ET_MEDIA_URLS.keys():
        url = mrigstatics.ET_MEDIA_URLS[urlkey]
        s = requests.Session()
        response = s.get(url)
    
        tree = ET.fromstring(response.text)
        recos = []
        desc = []
        recodates = []
        for child in tree.iter('pubDate'):
            recodates.append(datetime.datetime.strptime((child.text[5:7]+"-"+child.text[8:11]+"-"+child.text[12:16]),'%d-%b-%Y'))
        for child in tree.iter('title'):
            recos.append(child.text)
        for child in tree.iter('description'):
            desc.append(child.text[child.text.find('/>')+3:])
        
        re = []
        for i in range(0,len(recos[2:])):
            re.append([recodates[i],recos[i+2],desc[i+2],urlkey[3:-4]])
        
        recos = pandas.DataFrame(re,columns=["date","title","description","type"])
        engine = mrigutilities.sql_engine()
        try:
            recos.to_sql('media',engine, if_exists='append', index=False)
        except:
            pass
            
        print(recos)
    
if __name__ == '__main__':
    get_MCNews()        
    
 
    
    
    
