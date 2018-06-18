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
import instruments.swaps as swaps
import instruments.options as options
import instruments.index as index
import instruments.qlMaps as qlMaps
from pywintypes import Time

objectmap = {}

@xw.func
#@xw.arg('x', ndim=2, transpose=True)
@xw.ret(expand='table', index= True, transpose=False)
def argcheck(x):
    re = ql.Settings.instance().evaluationDate
    re = mu.python_dates(re)
    if x == None:
        x= True
    return Time(re)
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
    if ((conversionRatio == None) and not(None in [call_schedule,put_schedule])):
        bondType = 'callablebond'
    
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

            if bondType == 'callablebond':
                args['coupon_rates'] = fixed_coupon_rate
                args['call_schedule'] = call_schedule
                args['put_schedule'] = put_schedule
                bond = bonds.FixedRateCallableBond(args)
                #bond = "tst"
                objid = "Callable Bond "\
                        + "|" + str(fixed_coupon_rate)\
                        + "|" + objid
            
            objectmap[objid] = bond

        else:
            objid = "Error in arguments -->"+mu.args_inspector(args)[1]
    else:
        objid = 'Bond Type not assigned'
    return objid

@xw.func
def mrigxl_Swap(fixed_pay,
                 maturity_date,
                 face_value,
                 fixedleg_day_count='30-360',
                 fixedleg_calendar='India',
                 fixedleg_business_convention='Following',
                 fixedleg_month_end='True',
                 fixedleg_date_generation='Backward',
                 fixedleg_coupon_frequency='Semiannual',
                 fixedleg_coupon_rate=None,
                 floatleg_day_count='30-360',
                 floatleg_calendar='India',
                 floatleg_business_convention='Following',
                 floatleg_month_end='True',
                 floatleg_date_generation='Backward',
                 floatleg_coupon_frequency='Semiannual',
                 floatleg_index=None,
                 floatleg_coupon_spread=0,
                 floatleg_fixing=None):
    
    
    swapType = None
    # Check for fixed rate bond
    if fixedleg_coupon_rate != None:
        swapType = 'fixedfloatswap'
    
    if swapType != None:    
    
        fixedleg_args = {'pay_recieve_flag':fixed_pay.strip(),
                'maturity_date':maturity_date,
                'facevalue':face_value,                      
                'day_count':fixedleg_day_count.strip(),
                'calendar': fixedleg_calendar.strip(),
                'business_convention' : fixedleg_business_convention.strip(),
                'month_end': fixedleg_month_end,
                'date_generation' :fixedleg_date_generation.strip(),
                'coupon_frequency' :fixedleg_coupon_frequency.strip()}

        floatleg_args = {'day_count':floatleg_day_count.strip(),
                'calendar': floatleg_calendar.strip(),
                'business_convention' : floatleg_business_convention.strip(),
                'month_end': floatleg_month_end,
                'date_generation' :floatleg_date_generation.strip(),
                'coupon_frequency' :floatleg_coupon_frequency.strip()}  
        
        objid = ''
        if (mu.args_inspector(fixedleg_args)[0] and mu.args_inspector(floatleg_args)[0]):
            for key in fixedleg_args:
                objid = objid + "|" + str(fixedleg_args[key]) 
            for key in floatleg_args:
                objid = objid + "|" + str(floatleg_args[key]) 
            
            
            for arg_name in fixedleg_args:
                try:
                    fixedleg_args[arg_name] = qlMaps.QL[fixedleg_args[arg_name]]
                except:
                    pass

            for arg_name in floatleg_args:
                try:
                    floatleg_args[arg_name] = qlMaps.QL[floatleg_args[arg_name]]
                except:
                    pass
                
                
            if swapType == 'fixedfloatswap':
                fixedleg_args['coupon_rates'] = fixedleg_coupon_rate
                floatleg_args['coupon_index'] = objectmap[floatleg_index.strip()].getIndex()
                floatleg_args['coupon_spread'] = floatleg_coupon_spread
                floatleg_args['fixing'] = floatleg_fixing             
                swap = swaps.VanillaFixedFLoatSwap(fixedleg_args,floatleg_args)
                objid = "Fixed Float Swap | " \
                        + '{0:.2%}'.format(fixedleg_coupon_rate) \
                        + "|" + objectmap[floatleg_index.strip()].getName()+"+" \
                        + str(floatleg_coupon_spread) \
                        + "|" + str(floatleg_args['fixing']) + objid
            
            objectmap[objid] = swap

        else:
            objid = "Error in arguments -->" \
                    + mu.args_inspector(fixedleg_args)[1] \
                    + mu.args_inspector(floatleg_args)[1]
    else:
        objid = 'Swap Type not assigned'
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

        if exercise_type == 'American':
            option = options.VanillaAmericanOption(args)
            objid = "Vanilla American | "+ objid

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
        resultset.update(bond.getAnalytics())
        
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

        resultset.update(bond.getAnalytics())
    
    if assettype in ["FixedRateCallableBond"]:
        discount_curve_id = args['Discount Curve']
        mean_reversion = args['Mean Reversion']
        rate_vol = args['Short Rate Vol']
        grid_points = args['Hull White Grid Pts']
        #print(underlying_spot)
#        discount_curve_handle = objectmap[discount_curve_id].getCurveHandle()
        bond = objectmap[assetobjectid]
        bond.valuation(objectmap[discount_curve_id],
                       mean_reversion,
                       rate_vol,
                       int(grid_points))

        resultset.update(bond.getAnalytics())

    if assettype in ["VanillaFixedFLoatSwap"]:
        discount_curve_id = args['Discount Curve']
        #print(underlying_spot)
#        discount_curve_handle = objectmap[discount_curve_id].getCurveHandle()
        swap = objectmap[assetobjectid]
        swap.valuation(objectmap[discount_curve_id])

        resultset.update(swap.getAnalytics())

#Cashflow Formatting for Display
    if 'cashflows' in resultset.keys():
        offset=1
        for tup in resultset['cashflows']:
            cashflow[tup[0].strftime('%m/%d/%Y')+' '*offset] = tup[1]
        resultset['-----------------'] = '-----------------'
        resultset['Cashflow Date'] = 'Cashflow Amount'
        resultset.update(cashflow)
        resultset.pop('cashflows')

    if 'Fixed Leg Cashflows' in resultset.keys():
        offset=2
        for tup in resultset['Fixed Leg Cashflows']:
            cashflow[tup[0].strftime('%m/%d/%Y')+' '*offset] = tup[1]
        resultset['-----------------'] = '-----------------'
        resultset['Fixed Leg Cashflow Date'] = 'Fixed Leg Cashflow Amount'
        resultset.update(cashflow)
        resultset.pop('Fixed Leg Cashflows')
    if 'Floating Leg Cashflows' in resultset.keys():
        offset=3
        for tup in resultset['Floating Leg Cashflows']:
            cashflow[tup[0].strftime('%m/%d/%Y')+' '*offset] = tup[1]
        resultset['-----------------'] = '-----------------'
        resultset['Floating Leg Cashflow Date'] = 'Floating Leg Cashflow Amount'
        resultset.update(cashflow)
        resultset.pop('Floating Leg Cashflows')
    
    
    
    #Asset is Option
    if assettype in ["Option", "VanillaEuropeanOption", "VanillaAmericanOption"]:
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
    
    