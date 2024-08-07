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
import mrigstatics,mrigutilities,json
import xml.etree.ElementTree as ET

from gnews  import GNews
import pytz
import nltk

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
}


def get_MCNews():
    print("News download started\n")
    for urlkey in mrigstatics.MC_MEDIA_URLS.keys():
        url = mrigstatics.MC_MEDIA_URLS[urlkey]
        s = requests.Session()
        response = s.get(url)
        tree = ET.fromstring(response.text)
        recos = []
        desc = []
        guid = []
        body = []
        recodates = []
        for child in tree.iter('pubDate'):
            recodates.append(datetime.datetime.strptime((child.text[5:7]+"-"+child.text[8:11]+"-"+child.text[12:16]),'%d-%b-%Y'))
        for child in tree.iter('title'):
            recos.append(child.text)
        for child in tree.iter('description'):
            desc.append(child.text[child.text.find('/>')+3:])
        for child in tree.iter('guid'):
            articleurl = child.text
            articlebody = ""
            guid.append(articleurl)
            # print(articleurl)
            soup = BeautifulSoup(requests.get(articleurl, headers=headers).content, "html.parser")
            data = soup.find_all('script')
            for i in range(1,4):
                tes = data[i].string
                # print(tes[1707])
                # articlebody = ""
                try:
                    tes = json.loads(tes, strict=False)
                    # print(tes[0]['headline'])
                    # print(" "*80)
                    articlebody = tes[0]['articleBody']
                    # print(body)
                except:
                    pass
            body.append(articlebody)
            tes = None



        re = []
        for i in range(0,len(recos[2:])):
            re.append([recodates[i],recos[i+2],desc[i+2],urlkey[3:-4],guid[i],body[i]])
        # for recs in re:
            # print(recs[1],recs[5])
        
        recos = pandas.DataFrame(re,columns=["date","title","description","type","guid","body"])
        engine = mrigutilities.sql_engine()
        try:
            recos.to_sql('media',engine, if_exists='append', index=False)
        except:
            pass
        print(recos)
    return recos

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
        # try:
        #     recos.to_sql('media',engine, if_exists='append', index=False)
        # except:
        #     pass
        print(recos)
            
        print("News download finished\n")
        return recos

def get_GoogleNews():
    googlenews = GNews(language='en', country='IN', period='1d', start_date=None, end_date=None, max_results=20)
    IST = pytz.timezone('Asia/Kolkata')
    GMT = pytz.timezone('UTC')

    news_topics = {
        'Top News' : ['Top News'],
        'Broker Recos' : ['Stock Recommendations india'],
        'Buzz Stocks' : ['Buzz Stocks india'],
        'Economy' : ['Economy india','World Economy'],
        'Business': ['Business india'],
        'Markets' : ['Market Reports india','Stock Market india moneycontrol'],
        'Results' : ['Financial Results india'],
        'Technicals' : ['stock technical analysis india'],
    }

    news = {}
    for topic in news_topics.keys():
        news[topic] = []
        khabar_list = []
        for search_param in news_topics[topic]:
            # khabar = googlenews.get_news(search_param)
            for khabar in googlenews.get_news(search_param):
                try:
                    dtime = datetime.datetime.strptime(khabar['published date'], '%a, %d %b %Y %I:%M:%S %Z')
                    dtime = GMT.localize(dtime)
                    khabar_list.append([dtime.astimezone(IST).strftime('%a, %d %b %Y %I:%M:%S'),khabar['title'],khabar['description'],topic,khabar['url'],khabar['description']])
                    # khabar_list.append("<a style=\"color:#f7ed4a;text-decoration:underline;\" target=\"_blank\" rel=\"noopener noreferrer\" href=\"" + khabar['url'] + "\">" +khabar['title']+ "</a>")
                except:
                    pass
        news[topic] = khabar_list
    df = pandas.DataFrame()
    for k in news.keys():
        df = pandas.concat([df, pandas.DataFrame(news[k], columns=["date", "title", "description", "type", "guid", "body"])])
    news = df
    engine = mrigutilities.sql_engine()
    try:
        news.to_sql('media', engine, if_exists='append', index=False)
    except:
        pass
    print(news)
    return(news)


if __name__ == '__main__':
    # get_MCNews()
    # get_ETNews()
    get_GoogleNews()
 
    
    
    
