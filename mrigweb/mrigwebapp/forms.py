# -*- coding: utf-8 -*-
"""
Created on Wed Jan 16 15:21:06 2019

@author: Santosh Bag
"""

from django import forms
import nsepy


class StockForm(forms.Form):
    stocklist = nsepy.constants.symbol_list
#    slist = [] #"<select name=\"stock\"><option value="">""</option>"
#    for stk in stocklist:
#        slist = slist.append((str(stk),str(stk)))#+"</option>"

    symbol = forms.CharField()#ChoiceField(widget = forms.Select(),choices=slist)

class StrategyForm(forms.Form):
    strategy = forms.CharField()#ChoiceField(widget = forms.Select(),choices=slist)

class StockStrategyForm(forms.Form):
#    stockstrategy = forms.CharField()#ChoiceField(widget = forms.Select(),choices=slist)
    
# Market/Technical Parameters
#    marketcap_aggf = forms.CharField()
    marketcap_aggp = forms.CharField()
    marketcap_aggpnum = forms.CharField()
    marketcap_op = forms.CharField()
    marketcap_abs_filter = forms.CharField()
#    marketcap_bm_f = forms.CharField()
    price_aggf =  forms.CharField()
    price_aggp =  forms.CharField()
    price_aggpnum =  forms.CharField()
    price_op =  forms.CharField()
    price_abs_filter =  forms.CharField()
#    price_bm_f =  forms.CharField()
    volume_aggf =  forms.CharField()
    volume_aggp =  forms.CharField()
    volume_aggpnum =  forms.CharField()
    volume_op =  forms.CharField()
    volume_abs_filter =  forms.CharField()
#    volume_bm_f =  forms.CharField()
    pricevolume_aggf =  forms.CharField()
    pricevolume_aggp =  forms.CharField()
    pricevolume_aggpnum =  forms.CharField()
    pricevolume_op =  forms.CharField()
    pricevolume_abs_filter =  forms.CharField()
#    pricevolume_bm_f =  forms.CharField()
    pricereturn_aggf =  forms.CharField()
    pricereturn_aggp =  forms.CharField()
    pricereturn_aggpnum =  forms.CharField()
    pricereturn_op =  forms.CharField()
    pricereturn_abs_filter =  forms.CharField()
    pricereturn_bm_f =  forms.CharField()

# Market/Valuation Ratios
    basiceps_aggf =  forms.CharField()
    basiceps_aggp =  forms.CharField()
    basiceps_aggpnum =  forms.CharField()
    basiceps_op =  forms.CharField()
    basiceps_abs_filter =  forms.CharField()
    basiceps_bm_f =  forms.CharField()
    dividendyield_aggf =  forms.CharField()
    dividendyield_aggp =  forms.CharField()
    dividendyield_aggpnum =  forms.CharField()
    dividendyield_op =  forms.CharField()
    dividendyield_abs_filter =  forms.CharField()
    dividendyield_bm_f =  forms.CharField()
    pe_aggf =  forms.CharField()
    pe_aggp =  forms.CharField()
    pe_aggpnum =  forms.CharField()
    pe_op =  forms.CharField()
    pe_abs_filter =  forms.CharField()
    pe_bm_f =  forms.CharField()
    ps_aggf =  forms.CharField()
    ps_aggp =  forms.CharField()
    ps_aggpnum =  forms.CharField()
    ps_op =  forms.CharField()
    ps_abs_filter =  forms.CharField()
    ps_bm_f =  forms.CharField()
    pb_aggf =  forms.CharField()
    pb_aggp =  forms.CharField()
    pb_aggpnum =  forms.CharField()
    pb_op =  forms.CharField()
    pb_abs_filter =  forms.CharField()
    pb_bm_f =  forms.CharField()
    peg_aggf =  forms.CharField()
    peg_aggp =  forms.CharField()
    peg_aggpnum =  forms.CharField()
    peg_op =  forms.CharField()
    peg_abs_filter =  forms.CharField()
    peg_bm_f =  forms.CharField()
    
# Profitability Ratios
    roe_aggf =  forms.CharField()
    roe_aggp =  forms.CharField()
    roe_aggpnum =  forms.CharField()
    roe_op =  forms.CharField()
    roe_abs_filter =  forms.CharField()
    roe_bm_f =  forms.CharField()
    roa_aggf =  forms.CharField()
    roa_aggp =  forms.CharField()
    roa_aggpnum =  forms.CharField()
    roa_op =  forms.CharField()
    roa_abs_filter =  forms.CharField()
    roa_bm_f =  forms.CharField()
    netprofitmargin_aggf =  forms.CharField()
    netprofitmargin_aggp =  forms.CharField()
    netprofitmargin_aggpnum =  forms.CharField()
    netprofitmargin_op =  forms.CharField()
    netprofitmargin_abs_filter =  forms.CharField()
    netprofitmargin_bm_f =  forms.CharField()
    operatingprofitmargin_aggf =  forms.CharField()
    operatingprofitmargin_aggp =  forms.CharField()
    operatingprofitmargin_aggpnum =  forms.CharField()
    operatingprofitmargin_op =  forms.CharField()
    operatingprofitmargin_abs_filter =  forms.CharField()
    operatingprofitmargin_bm_f =  forms.CharField()
    
# Liquidity Ratios
    currentratio_aggf =  forms.CharField()
    currentratio_aggp =  forms.CharField()
    currentratio_aggpnum =  forms.CharField()
    currentratio_op =  forms.CharField()
    currentratio_abs_filter =  forms.CharField()
    currentratio_bm_f =  forms.CharField()
    quickratio_aggf =  forms.CharField()
    quickratio_aggp =  forms.CharField()
    quickratio_aggpnum =  forms.CharField()
    quickratio_op =  forms.CharField()
    quickratio_abs_filter =  forms.CharField()
    quickratio_bm_f =  forms.CharField()

# Solvency Ratios
    debtequity_aggf =  forms.CharField()
    debtequity_aggp =  forms.CharField()
    debtequity_aggpnum =  forms.CharField()
    debtequity_op =  forms.CharField()
    debtequity_abs_filter =  forms.CharField()
    debtequity_bm_f =  forms.CharField()

#Efficiency Ratios
    assetturnover_aggf =  forms.CharField()
    assetturnover_aggp =  forms.CharField()
    assetturnover_aggpnum =  forms.CharField()
    assetturnover_op =  forms.CharField()
    assetturnover_abs_filter =  forms.CharField()
    assetturnover_bm_f =  forms.CharField()
    inventoryturnover_aggf =  forms.CharField()
    inventoryturnover_aggp =  forms.CharField()
    inventoryturnover_aggpnum =  forms.CharField()
    inventoryturnover_op =  forms.CharField()
    inventoryturnover_abs_filter =  forms.CharField()
    inventoryturnover_bm_f =  forms.CharField()

# Market Risk 
    volatility_aggf =  forms.CharField()
    volatility_aggp =  forms.CharField()
    volatility_aggpnum =  forms.CharField()
    volatility_op =  forms.CharField()
    volatility_abs_filter =  forms.CharField()
    volatility_bm_f =  forms.CharField()
    beta_aggf =  forms.CharField()
    beta_aggp =  forms.CharField()
    beta_aggpnum =  forms.CharField()
    beta_op =  forms.CharField()
    beta_abs_filter =  forms.CharField()
    beta_bm_f =  forms.CharField()
    sharpe_aggf =  forms.CharField()
    sharpe_aggp =  forms.CharField()
    sharpe_aggpnum =  forms.CharField()
    sharpe_op =  forms.CharField()
    sharpe_abs_filter =  forms.CharField()
    sharpe_bm_f =  forms.CharField()

    
class OptionForm(forms.Form):
    symbol = forms.CharField()
    expiry = forms.CharField()
    strike = forms.CharField()
    callput = forms.CharField()
    
    
