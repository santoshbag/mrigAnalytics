# -*- coding: utf-8 -*-
"""
Created on Wed May 23 16:19:22 2018

@author: Santosh Bag
"""

"""
Total Return Indices List from NSE
"""
TR_INDICES = {'Broad_Market' : ['NIFTY 50',
                               'NIFTY NEXT 50',
                               'NIFTY 100',
                               'NIFTY 200',
                               'NIFTY 500',
                               'NIFTY MIDCAP 150',
                               'NIFTY MIDCAP 50',
                               'NIFTY FULL MIDCAP 100',
                               'NIFTY MIDCAP 100',
                               'NIFTY SMALLCAP 250',
                               'NIFTY SMALLCAP 50',
                               'NIFTY FULL SMALLCAP 100',
                               'NIFTY SMALLCAP 100',
                               'NIFTY LARGEMIDCAP 250',
                               'NIFTY MIDSMALLCAP 400'],
               'Sectoral': ['NIFTY AUTO',
                          'NIFTY BANK',
                          'NIFTY FINANCIAL SERVICES',
                          'NIFTY FMCG',
                          'NIFTY IT',
                          'NIFTY MEDIA',
                          'NIFTY METAL',
                          'NIFTY PHARMA',
                          'NIFTY PRIVATE BANK',
                          'NIFTY PSU BANK',
                          'NIFTY REALTY'],
               'Thematic': ['NIFTY COMMODITIES',
                          'NIFTY CPSE',
                          'NIFTY ENERGY',
                          'NIFTY100 ESG',
                          'NIFTY100 ENHANCED ESG',
                          'NIFTY INDIA CONSUMPTION',
                          'NIFTY INFRASTRUCTURE',
                          'NIFTY MIDCAP LIQUID 15',
                          'NIFTY MNC',
                          'NIFTY PSE',
                          'NIFTY SME EMERGE',
                          'NIFTY SERVICES SECTOR',
                          'NIFTY SHARIAH 25',
                          'NIFTY100 LIQUID 15',
                          'NIFTY50 SHARIAH',
                          'NIFTY500 SHARIAH',
                          'NIFTY ADITYA BIRLA GROUP',
                          'NIFTY MAHINDRA GROUP',
                          'NIFTY TATA GROUP',
                          'NIFTY TATA GROUP 25% CAP'],
               'Strategy': ['NIFTY ALPHA LOW-VOLATILITY 30',
                          'NIFTY QUALITY LOW-VOLATILITY 30',
                          'NIFTY ALPHA QUALITY LOW-VOLATILITY 30',
                          'NIFTY ALPHA QUALITY VALUE LOW-VOLATILITY 30',
                          'NIFTY50 EQUAL WEIGHT',
                          'NIFTY100 EQUAL WEIGHT',
                          'NIFTY100 LOW VOLATILITY 30',
                          'NIFTY DIVIDEND OPPORTUNITIES 50',
                          'NIFTY ALPHA 50',
                          'NIFTY HIGH BETA 50',
                          'NIFTY LOW VOLATILITY 50',
                          'NIFTY200 QUALITY 30 INDEX',
                          'NIFTY QUALITY 30',
                          'NIFTY50 VALUE 20',
                          'NIFTY GROWTH SECTORS 15']}

"""
YIELD CURVE DATA FROM www.worldgovernmentbonds.com
"""

WGB_YIELD_URL = {'INR': 'http://www.worldgovernmentbonds.com/country/india/',
                 'USD': 'http://www.worldgovernmentbonds.com/country/united-states/',
                 'GBP': 'http://www.worldgovernmentbonds.com/country/united-kingdom//'}

CURVE_LIST = ['INR','USD','GBP']

COLUMN_MAPPINGS = {'ResidualMaturity':'tenor',
                   'Yield':'yield',
                   'Change1M (Value 1M ago)':'Change1M_Value_1M_ago',
                   'Change6M (Value 6M ago)':'Change6M_Value_6M_ago',
                   }



"""
 Value Research Online Mutual Fund codes
"""
VR_MF_CODE = {}

VR_LOGIN = {'VR_URL':'https://www.valueresearchonline.com/registration/loginprocess.asp',
            'CRED': {'username': 'santosh.bag@gmail.com','password': 'Xanto123!'}}

"""
 Money Control Stock codes
"""
MC_STOCK_CODE = {}

MC_URLS = {'MC_CODES_URL':'https://www.moneycontrol.com/india/stockpricequote/',
           'MC_RATIOS_URL':'https://www.moneycontrol.com/financials/',
           'MC_QTRLY_RESULTS_URL':'https://www.moneycontrol.com/financials/',
           'MC_BALANCE_SHEET_URL':'https://www.moneycontrol.com/financials/',
           'MC_PROFIT_LOSS_URL':'https://www.moneycontrol.com/financials/',
           'MC_CASHFLOW_STATEMENT_URL':'https://www.moneycontrol.com/financials/',
           'MC_CORP_ACTION_URL':'https://www.moneycontrol.com/company-facts/'}


"""
 OECD Data
"""
MC_STOCK_CODE = {}

OECD_DATABASE_CODES = {'BALANCE_OF_PAYMENTS' : 'MEI_BOP6',
             'BUSINESS_TENDENCY':'MEI_BTS_COS',
             'COMPOSITE_LEADING_INDICATORS':'MEI_CLI',
             'FINANCIAL_STATISTICS':'MEI_FIN',
             'INDUSTRY':'MEI_REAL',
             'INTERNATIONAL_TRADE':'MEI_TRD',
             'LABOUR_MARKET':'STLABOUR',
             'CONSUMER_PRICES':'MEI_PRICES',
             'PRODUCER_PRICE_INDICES':'MEI_PRICES_PPI',
             'PPP':'PPPGDP',
             'COMPARATIVE_PRICES':'CPL',
             'GDP':'QNA'}

OECD_URLS = {'BALANCE_OF_PAYMENTS' : 'https://stats.oecd.org/SDMX-JSON/data/MEI_BOP6/.IND../all?startPeriod=1947',
             'BUSINESS_TENDENCY':'https://stats.oecd.org/SDMX-JSON/data/MEI_BTS_COS/.IND../all?startPeriod=1947',
             'COMPOSITE_LEADING_INDICATORS':'https://stats.oecd.org/SDMX-JSON/data/MEI_CLI/.IND./all?startPeriod=1947',
             'FINANCIAL_STATISTICS':'https://stats.oecd.org/SDMX-JSON/data/MEI_FIN/.IND./all?startPeriod=1947',
             'INDUSTRY':'https://stats.oecd.org/SDMX-JSON/data/MEI_REAL/.IND./all?startPeriod=1947',
             'INTERNATIONAL_TRADE':'https://stats.oecd.org/SDMX-JSON/data/MEI_TRD/.IND../all?startPeriod=1947',
             'LABOUR_MARKET':'STLABOUR',
             'CONSUMER_PRICES':'MEI_PRICES',
             'PRODUCER_PRICE_INDICES':'https://stats.oecd.org/SDMX-JSON/data/MEI_PRICES_PPI/.IND../all?startPeriod=1947',
             'PPP':'https://stats.oecd.org/SDMX-JSON/data/PPPGDP/.IND/all?startPeriod=1947',
             'COMPARATIVE_PRICES':'CPL',
             'GDP':'https://stats.oecd.org/SDMX-JSON/data/QNA/IND.../all?startPeriod=1947'}



"""
ZERODHA CHARGES
"""

TR_CHARGES ={'BROK':0,
             'STT/CTT':0.001,
             'EXCH':0.0000325,
             'GST':0.18,
             'SEBI':15}
