# -*- coding: utf-8 -*-
"""
Created on Wed May 23 16:19:22 2018

@author: Santosh Bag
"""

import json
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

file = open(os.path.join(os.path.dirname(__file__), "settings.json"))
settings = json.load(file)

trade_display_analytics = settings['trade_display_analytics']

fred_api = '2b698cadeffb4967c40cca3a3afb0509'

# RAZORPAY DETAILS
RAZORPAY_KEY_ID = 'rzp_test_eR8UOYsnBFwq49'
RAZORPAY_KEY_SECRET = 'ttfyVQSOHoP1ZyBFsjK4ZG6a'

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
                 'GBP': 'http://www.worldgovernmentbonds.com/country/united-kingdom/'}

US_TREASURY_URL = 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value='
US_TREASURY_XML_URL = 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value='

CCIL_INR_ZCYC_URL = {'INR' : 'https://www.ccilindia.com/RiskManagement/SecuritiesSegment/Lists/Tenor%20Wise%20Zero%20Coupon%20Yield/Attachments/2419/Tenor-wise%20Zero%20Coupon%20Yields%20Sheet%2019072019.xls'}

CURVE_LIST = ['INR','USD','GBP']

COLUMN_MAPPINGS = {'ResidualMaturity':'tenor',
                   'Yield':'yield',
#                   'Change1M (Value 1M ago)':'Change1M_Value_1M_ago',
#                   'Change6M (Value 6M ago)':'Change6M_Value_6M_ago',
                   'Chg 1M':'Change1M_Value_1M_ago',
                   'Chg 6M':'Change6M_Value_6M_ago'
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


MC_MEDIA_URLS = {'MC_BROKERRECOS_URL':'http://www.moneycontrol.com/rss/brokeragerecos.xml',
                 'MC_BUZZSTOCKS_URL':'http://www.moneycontrol.com/rss/buzzingstocks.xml',
                 'MC_LATESTNEWS_URL':'http://www.moneycontrol.com/rss/latestnews.xml',
                 'MC_POPULAR_URL':'http://www.moneycontrol.com/rss/mostpopular.xml',
                 'MC_BUSINESS_URL':'http://www.moneycontrol.com/rss/business.xml',
                 'MC_ECONOMY_URL':'http://www.moneycontrol.com/rss/economy.xml',
                 'MC_MARKETREPORT_URL':'http://www.moneycontrol.com/rss/marketreports.xml',
                 'MC_GLOBAL_URL':'http://www.moneycontrol.com/rss/internationalmarkets.xml',
                 'MC_MARKETOUTLOOK_URL':'http://www.moneycontrol.com/rss/marketoutlook.xml',
                 'MC_TECHNICALS_URL':'http://www.moneycontrol.com/rss/technicals.xml',
                 'MC_IPONEWS_URL':'http://www.moneycontrol.com/rss/iponews.xml',
                 'MC_COMMODITIES_URL':'http://www.moneycontrol.com/rss/commodities.xml',
                 'MC_RESULTS_URL':'http://www.moneycontrol.com/rss/results.xml',
                 'MC_TECHNICALS_URL':'http://www.moneycontrol.com/rss/technicals.xml',
                 'MC_INSURANCE_URL':'http://www.moneycontrol.com/rss/insurancenews.xml',
                 }

ET_MEDIA_URLS = {'MC_BROKERRECOS_URL':'http://www.moneycontrol.com/rss/brokeragerecos.xml',
                 'MC_BUZZSTOCKS_URL':'http://www.moneycontrol.com/rss/buzzingstocks.xml',
                 'MC_LATESTNEWS_URL':'http://www.moneycontrol.com/rss/latestnews.xml',
                 'MC_POPULAR_URL':'http://www.moneycontrol.com/rss/mostpopular.xml',
                 'MC_BUSINESS_URL':'http://www.moneycontrol.com/rss/business.xml',
                 'MC_ECONOMY_URL':'http://www.moneycontrol.com/rss/economy.xml',
                 'MC_MARKETREPORT_URL':'http://www.moneycontrol.com/rss/marketreports.xml',
                 'MC_GLOBAL_URL':'http://www.moneycontrol.com/rss/internationalmarkets.xml',
                 'MC_MARKETOUTLOOK_URL':'http://www.moneycontrol.com/rss/marketoutlook.xml',
                 'MC_TECHNICALS_URL':'http://www.moneycontrol.com/rss/technicals.xml',
                 'MC_IPONEWS_URL':'http://www.moneycontrol.com/rss/iponews.xml',
                 'MC_COMMODITIES_URL':'http://www.moneycontrol.com/rss/commodities.xml',
                 'MC_RESULTS_URL':'http://www.moneycontrol.com/rss/results.xml',
                 }

'''
Mutual Fund URLS
'''

MF = {
    'AUM':'https://www.amfiindia.com/research-information/aum-data/average-aum',
    'NAV_ONEMF_HIST':'https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf={}&frmdt={}&todt={}',
    'SCHEME_INFO' : 'https://portal.amfiindia.com/DownloadSchemeData_Po.aspx?mf=0',
    'NAV_ALL_HIST':'https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt={}&todt={}'
}




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
ZERODHA_CHARGES = {
'EQ_D' : {'BROK_FLAT':0,
               'BROK_PER':0,
             'STT/CTT':0.001,
             'EXCH':0.0000325,
             'GST':0.18,
             'SEBI':10},
'EQ_I' : {'BROK_FLAT':20,
            'BROK_PER':0.0003,
             'STT/CTT':0.00025,
             'EXCH':0.0000325,
             'GST':0.18,
             'SEBI':10},
'EQ_F' : {'BROK_FLAT':20,
             'BROK_PER':0.0003,
             'STT/CTT':0.0001,
             'EXCH':0.000019,
             'GST':0.18,
             'SEBI':10},
'EQ_O' : {'BROK_FLAT':20,
            'BROK_PER':0,
             'STT/CTT':0.0005,
             'EXCH':0.0005,
             'GST':0.18,
             'SEBI':10}

}

NIFTY_50 = {
            'INFY',
            'ASIANPAINT',
            'HCLTECH',
            'RELIANCE',
            'HEROMOTOCO',
            'TATACONSUM',
            'ICICIBANK',
            'TECHM',
            'BAJAJ-AUTO',
            'WIPRO',
            'LT',
            'NTPC',
            'BAJAJFINSV',
            'ONGC',
            'ADANIENT',
            'SBILIFE',
            'POWERGRID',
            'EICHERMOT',
            'ITC',
            'TCS',
            'M&M',
            'HDFCBANK',
            'HINDUNILVR',
            'AXISBANK',
            'INDUSINDBK',
            'CIPLA',
            'BHARTIARTL',
            'MARUTI',
            'KOTAKBANK',
            'ADANIPORTS',
            'NESTLEIND',
            'HINDALCO',
            'UPL',
            'BPCL',
            'JSWSTEEL',
            'DRREDDY',
            'GRASIM',
            'COALINDIA',
            'DIVISLAB',
            'TATASTEEL',
            'ULTRACEMCO',
            'APOLLOHOSP',
            'SUNPHARMA',
            'TATAMOTORS',
            'BAJFINANCE',
            'TITAN',
            'BRITANNIA',
            'SBIN',
            'HDFCLIFE',
            'LTIM'       
            }

NIFTY_100 = {'ABB',
            'ACC',
            'ADANIENT',
            'ADANIGREEN',
            'ADANIPORTS',
            'ATGL',
            'ADANITRANS',
            'AWL',
            'AMBUJACEM',
            'APOLLOHOSP',
            'ASIANPAINT',
            'DMART',
            'AXISBANK',
            'BAJAJ-AUTO',
            'BAJFINANCE',
            'BAJAJFINSV',
            'BAJAJHLDNG',
            'BANKBARODA',
            'BERGEPAINT',
            'BEL',
            'BPCL',
            'BHARTIARTL',
            'BOSCHLTD',
            'BRITANNIA',
            'CANBK',
            'CHOLAFIN',
            'CIPLA',
            'COALINDIA',
            'COLPAL',
            'DLF',
            'DABUR',
            'DIVISLAB',
            'DRREDDY',
            'EICHERMOT',
            'NYKAA',
            'GAIL',
            'GODREJCP',
            'GRASIM',
            'HCLTECH',
            'HDFCAMC',
            'HDFCBANK',
            'HDFCLIFE',
            'HAVELLS',
            'HEROMOTOCO',
            'HINDALCO',
            'HAL',
            'HINDUNILVR',
            'ICICIBANK',
            'ICICIGI',
            'ICICIPRULI',
            'ITC',
            'IOC',
            'IRCTC',
            'INDUSTOWER',
            'INDUSINDBK',
            'NAUKRI',
            'INFY',
            'INDIGO',
            'JSWSTEEL',
            'JINDALSTEL',
            'KOTAKBANK',
            'LTIM',
            'LT',
            'LICI',
            'M&M',
            'MARICO',
            'MARUTI',
            'MUTHOOTFIN',
            'NTPC',
            'NESTLEIND',
            'ONGC',
            'PIIND',
            'PAGEIND',
            'PIDILITIND',
            'POWERGRID',
            'PGHH',
            'RELIANCE',
            'SBICARD',
            'SBILIFE',
            'SRF',
            'MOTHERSON',
            'SHREECEM',
            'SIEMENS',
            'SBIN',
            'SUNPHARMA',
            'TCS',
            'TATACONSUM',
            'TATAMOTORS',
            'TATAPOWER',
            'TATASTEEL',
            'TECHM',
            'TITAN',
            'TORNTPHARM',
            'UPL',
            'ULTRACEMCO',
            'MCDOWELL-N',
            'VBL',
            'VEDL',
            'WIPRO',
            'ZOMATO'}


INDEX_MAP_FOR_OC = {'NIFTY 50':'NIFTY',
                    'NIFTY IT':'NIFTYIT',
                    'NIFTY BANK':'BANKNIFTY',
                    'NIFTY MIDCAP 50':'NIFTYMID50'}

MRIGWEB = {'development' : 'mrigweb',
           'production' : 'mrigweb'}

RB_WAREHOUSE = {'development' : 'rb_warehouse',
                'production' : 'rb_warehouse'}

DBHOST = {'SIRIUS' : '192.168.29.208',
          'localhost' : 'localhost'}

ENVIRONMENT = 'development'
#ENVIRONMENT = 'production'

NSE_HOLIDAYS = {
	'22-Jan-2024' :'Special Holiday',
'26-Jan-2024' : 'Republic Day',
'08-Mar-2024':	'Mahashivratri',
'25-Mar-2024'	:'Holi',
'29-Mar-2024' :	'Good Friday',
'11-Apr-2024'	:'Id-Ul-Fitr',
'17-Apr-2024' :	'Shri Ram Navmi',
'01-May-2024' : 'Maharashtra Day',
'17-Jun-2024' :	'Monday	Bakri Id',
'17-Jul-2024':	'Moharram',
'15-Aug-2024'	: 'Independence Day',
'02-Oct-2024' : 'Mahatma Gandhi Jayanti',
'01-Nov-2024':	'Diwali Laxmi Pujan',
'15-Nov-2024' : 'Gurunanak Jayanti',
'25-Dec-2024' :	'Christmas'}


if __name__ == '__main__':
    print(trade_display_analytics)