# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 15:53:34 2018

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import xlwings as xw
import pandas as pd
import datetime
import QuantLib as ql
import mrigutilities as mu
import instruments.termstructure as ts
import instruments.bonds as bonds
import instruments.options as options
import instruments.index as index
import instruments.qlMaps as qlMaps
from pywintypes import Time

objectmap = {}

@xw.func
@xw.arg('x', ndim=2, transpose=True)
@xw.ret(expand='table', index= True, transpose=False)
def argcheck(x):

    return str(x[0])
@xw.func
@xw.arg('x', pd.DataFrame, index=True, header=True)
@xw.ret(index=True, header=True,expand='table')
def CORREL2(x):
    """Like CORREL, but as array formula for more than 2 data sets"""
    return x.corr()

@xw.func
#@xw.arg('yielddata', dict)
@xw.ret(expand='table', transpose=True)
def objectcheck():
    keys=[]
    for obj in objectmap.keys():
        keys.append(str(obj))
    return keys

@xw.func
@xw.arg('shiftparameter', ndim=2, transpose=True)
def mrigxl_FlatForwardYieldCurve(reference_date,
                                 day_count='30-360',
                                 calendar='India',
                                 flat_rate=0,
                                 compounding='Compounded',
                                 compounding_frequency='Annual',
                                 shiftparameter=None):
    objid = 'FFYC'
    args = {'day_count':day_count.strip(),
            'calendar': calendar.strip(),
            'flat_rate' : flat_rate,
            'compounding' : compounding.strip(),
            'compounding_frequency' :compounding_frequency.strip()}
    if mu.args_inspector(args)[0]:
        for key in args:
            objid = objid + "|" + str(args[key]) 

        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
        ffyc = ts.FlatForwardYieldCurve(reference_date,flat_rate)
        args.update({'shiftparameter' : shiftparameter})
        ffyc.setupCurve(args)
        objectmap[objid] = ffyc
    else:
        objid = "Error in arguments -->"+mu.args_inspector(args)[1]
    return objid

@xw.func
@xw.arg('shiftparameter', ndim=2, transpose=True)
def mrigxl_SpotZeroYieldCurve(reference_date,
                             curve_currency='INR',
                             day_count='30-360',
                             calendar='India',
                             compounding='Compounded',
                             compounding_frequency='Annual',
                             interpolation='Linear',
                             shiftparameter=None):
    objid = 'SZYC'
    args = {'day_count':day_count.strip(),
            'calendar': calendar.strip(),
            'compounding' : compounding.strip(),
            'compounding_frequency' :compounding_frequency.strip(),
            'interpolation' : interpolation.strip()}
            
    if mu.args_inspector(args)[0]:
        for key in args:
            objid = objid + "|" + str(args[key]) 
        
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
        szyc = ts.SpotZeroYieldCurve(curve_currency,reference_date)
        args.update({'shiftparameter' : shiftparameter})
        szyc.setupCurve(args)
        objectmap[objid] = szyc
    else:
        objid = "Error in arguments -->"+mu.args_inspector(args)[1]
    return objid

@xw.func
#@xw.arg('yielddata', dict)
def mrigxl_FlatDividendYieldCurve(reference_date,
                                 day_count='30-360',
                                 calendar='India',
                                 flat_rate=0,
                                 compounding='Compounded',
                                 compounding_frequency='Annual'):
    objid = 'FDYC'
    args = {'day_count':day_count.strip(),
            'calendar': calendar.strip(),
            'flat_rate' : flat_rate,
            'compounding' : compounding.strip(),
            'compounding_frequency' :compounding_frequency.strip()}
    if mu.args_inspector(args)[0]:
        for key in args:
            objid = objid + "|" + str(args[key]) 

        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
        fdyc = ts.FlatDividendYieldCurve(reference_date,flat_rate)
        fdyc.setupCurve(args)
        objectmap[objid] = fdyc
    else:
        objid = "Error in arguments -->"+mu.args_inspector(args)[1]
    return objid

@xw.func
#@xw.arg('yielddata', dict)
def mrigxl_FlatVolatilityCurve(reference_date,
                                 day_count='30-360',
                                 calendar='India',
                                 spot_vols=0,
                                 compounding='Compounded',
                                 compounding_frequency='Annual'):
    objid = 'FVYC'
    args = {'day_count':day_count.strip(),
            'calendar': calendar.strip(),
            'spot_vols' : spot_vols,
            'compounding' : compounding.strip(),
            'compounding_frequency' :compounding_frequency.strip()}
    if mu.args_inspector(args)[0]:
        for key in args:
            objid = objid + "|" + str(args[key]) 

        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
        fvyc = ts.FlatVolatilityCurve(reference_date,spot_vols)
        fvyc.setupCurve(args)
        objectmap[objid] = fvyc
    else:
        objid = "Error in arguments -->"+mu.args_inspector(args)[1]
    return objid


@xw.func
#@xw.arg('yielddata', dict)
def mrigxl_Libor(index_name,
                 curve_currency='INR',
                 tenor='3M',
                 day_count='30-360',
                 calendar='India',
                 settlement_days=3,
                 yieldcurvehandle=None):
    objid = "Index"
    
    args = {'index_name':index_name.strip(),
            'curve_currency' : curve_currency.strip(),
            'tenor' : tenor.strip(),
            'day_count':day_count.strip(),                                     
            'calendar': calendar.strip(),
            'settlement_days' : int(settlement_days)}
    
    if mu.args_inspector(args)[0]:
        for key in args:
            objid = objid + "|" + str(args[key]) 
            
        if yieldcurvehandle.strip() in objectmap.keys():
            ych = objectmap[yieldcurvehandle.strip()].getCurveHandle()
            libor = index.Libor(args['index_name'],
                                args['tenor'],
                                args['settlement_days'],
                                args['curve_currency'],
                                args['calendar'],
                                args['day_count'],
                                ych)
            objectmap[objid] = libor
    else:
        objid = "Error in arguments -->"+mu.args_inspector(args)[1]
    return objid

@xw.func
@xw.arg('call_schedule', ndim=2, transpose=True)
@xw.arg('put_schedule', ndim=2, transpose=True)
@xw.arg('dividend_schedule', ndim=2, transpose=True)
def mrigxl_Bond(issue_name,
                 issue_date,
                 maturity_date,
                 face_value=100,
                 day_count='30-360',
                 calendar='India',
                 business_convention='Following',
                 month_end='True',
                 settlement_days=3,
                 date_generation='Backward',
                 coupon_frequency='Semiannual',
                 fixed_coupon_rate=None,
                 floating_coupon_index=None,
                 floating_coupon_spread=0,
                 inArrears=True,
                 cap=None,
                 floor=None,
                 fixing=None,
                 conversionRatio=None,
                 conversionPrice=None,
                 credit_spread=None,
                 call_schedule=None,
                 put_schedule=None,
                 dividend_schedule=None):
    
    
    bondType = None
    # Check for fixed rate bond
    if floating_coupon_index != None:
        if floating_coupon_index.strip() in objectmap.keys():
            bondType = 'floatingratebond'
    if fixed_coupon_rate != None:
        bondType = 'fixedratebond'
    if conversionRatio != None:
        bondType = 'convertiblebond'

    
    if bondType != None:    
    
        args = {'issue_name':issue_name.strip(),
                'issue_date':issue_date,
                'maturity_date':maturity_date,
                'facevalue':face_value,                      
                'day_count':day_count.strip(),
                'calendar': calendar.strip(),
                'business_convention' : business_convention.strip(),
                'month_end': month_end,
                'settlement_days':int(settlement_days),
                'date_generation' :date_generation.strip(),
                'coupon_frequency' :coupon_frequency.strip(),
                'inArrears' : inArrears}
        
        objid = ''
        if mu.args_inspector(args)[0]:
            for key in args:
                objid = objid + "|" + str(args[key]) 
            
            for arg_name in args:
                try:
                    args[arg_name] = qlMaps.QL[args[arg_name]]
                except:
                    pass
                
            if bondType == 'fixedratebond':
                args['coupon_rates'] = fixed_coupon_rate
                bond = bonds.FixedRateBond(args)
                objid = "Fixed Rate Bond | "+str(fixed_coupon_rate) + objid
    
            if bondType == 'floatingratebond':
                args['coupon_index'] = objectmap[floating_coupon_index.strip()].getIndex()
                args['coupon_spread'] = floating_coupon_spread
                if cap != None :
                    args['cap'] = [cap]
                else:
                    args['cap'] = []
                if floor != None :
                    args['floor'] = [floor]
                else:
                    args['floor'] = []
                args['fixing'] = fixing
                bond = bonds.FloatingRateBond(args)
                bond.setBlackPricer()
                objid = "Floating Rate Bond|" \
                        + objectmap[floating_coupon_index.strip()].getName()+"+" \
                        + str(floating_coupon_spread) \
                        + "|" + str(args['cap']) \
                        + "|" + str(args['floor']) \
                        + "|" + str(args['fixing']) + objid
            
            if bondType == 'convertiblebond':
                args['coupon_rates'] = fixed_coupon_rate
                args['conversion_ratio'] = conversionRatio
                args['conversion_price'] = conversionPrice
                args['credit_spread'] = credit_spread
                args['call_schedule'] = call_schedule
                args['put_schedule'] = put_schedule
                args['dividend_schedule'] = dividend_schedule
                bond = bonds.FixedRateConvertibleBond(args)
                #bond = "tst"
                objid = "Convertible Bond "\
                        + "|" +str(fixed_coupon_rate)\
                        + "|" +str(conversionRatio)\
                        + "|" +str(conversionPrice) \
                        + "|" +str(credit_spread) \
                        + "|"  +objid
    
            
            objectmap[objid] = bond
        else:
            objid = "Error in arguments -->"+mu.args_inspector(args)[1]
    else:
        objid = 'Bond Type not assigned'
    return objid

@xw.func
#@xw.arg('bonddata', dict)
def mrigxl_Option(option_name,
                 underlying_name,
                 maturity_date,
                 option_type,
                 strike,
                 exercise_type,
                 day_count='30-360',
                 calendar='India'):
    
    
    args = {'option_name':option_name.strip(),
            'underlying_name':underlying_name.strip(),
            'maturity_date':maturity_date,
            'option_type':option_type.strip(),
            'strike': strike,                               
            'exercise_type':exercise_type.strip(),
            'day_count':day_count.strip(),
            'calendar':calendar.strip()}
    
    objid = ''
    if mu.args_inspector(args)[0]:
        for key in args:
            objid = objid + "|" + str(args[key]) 
        
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
            
        if exercise_type == 'European':
            option = options.VanillaEuropeanOption(args)
            objid = "Vanilla European | "+ objid

        objectmap[objid] = option
    else:
        objid = "Error in arguments -->"+mu.args_inspector(args)[1]
    return objid


@xw.func
@xw.arg('args', dict)
@xw.ret(expand='table')
def mrigxl_Analytics(assetobjectid,args):
    resultset = {'Heads' : 'Values'}
    assettype = str(type(objectmap[assetobjectid]))[8:-2].split(".")[-1]
    #resultset = assettype
    cashflow = {}
    #Asset is Bond
    if assettype in ["FixedRateBond", "FloatingRateBond", "Bond"]:
        discount_curve_id = args['Discount Curve']
#        discount_curve_handle = objectmap[discount_curve_id].getCurveHandle()
        bond = objectmap[assetobjectid]
        bond.valuation(objectmap[discount_curve_id])
        
    if assettype in ["FixedRateConvertibleBond"]:
        underlying_spot = args['Underlying Spot']
        discount_curve_id = args['Discount Curve']
        volatility_curve_id = args['Volatility Curve']
        dividend_curve_id = args['Dividend Curve']
        #print(underlying_spot)
#        discount_curve_handle = objectmap[discount_curve_id].getCurveHandle()
        bond = objectmap[assetobjectid]
        bond.valuation(underlying_spot,
                         objectmap[discount_curve_id],
                         objectmap[volatility_curve_id],
                         objectmap[dividend_curve_id])

        resultset.update(objectmap[assetobjectid].getAnalytics())
    if 'cashflows' in resultset.keys():
        for tup in resultset['cashflows']:
            cashflow[Time(tup[0])] = tup[1]
        resultset['-----------------'] = '-----------------'
        resultset['Cashflow Date'] = 'Cashflow Amount'
        resultset.update(cashflow)
        resultset.pop('cashflows')
    
    #Asset is Option
    if assettype in ["Option", "VanillaEuropeanOption"]:
        underlying_spot = args['Underlying Spot']
        discount_curve_id = args['Discount Curve']
        volatility_curve_id = args['Volatility Curve']
        dividend_curve_id = args['Dividend Curve']
        valuation_method = args['Valuation Method']
        
        option = objectmap[assetobjectid]
        option.valuation(underlying_spot,
                         objectmap[discount_curve_id],
                         objectmap[volatility_curve_id],
                         objectmap[dividend_curve_id],
                         valuation_method)
        resultset.update(objectmap[assetobjectid].getAnalytics())
    return resultset
    
    
@xw.func
def setPricing(bondHandle, curvehandle):
    bond = objectmap[bondHandle]
    curve = objectmap[curvehandle]
    
    bondengine = ql.DiscountingBondEngine(curve)
    bond.setPricingEngine(bondengine)
    return True

@xw.func
def bondAnalytics(bondHandle):
    bond = objectmap[bondHandle]
    
    return bond.NPV()



if __name__ == '__main__':
    print("santosh---")
    print(objectmap)
    xw.serve()
    
    