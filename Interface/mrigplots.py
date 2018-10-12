# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 16:19:21 2018

Plot Library..

@author: Santosh Bag
"""

import matplotlib.pyplot as plt
import matplotlib

def singleScaleLine_plots(labels,pltname=None):
    
    MICRO_SIZE = 3
    MINI_SIZE = 6
    SMALL_SIZE = 8
    MEDIUM_SIZE = 10
    BIGGER_SIZE = 12

    bg_color = 'black'#'dimgray'
    fg_color = 'white'
    border='yellow'
    
    plt.rc('font', size=MINI_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=MINI_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MINI_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MINI_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=MINI_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=MINI_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=MINI_SIZE)  # fontsize of the figure title
    plt.rcParams['savefig.facecolor']=bg_color
    plt.rcParams['savefig.edgecolor']=border


    #basecurve = curve.getBaseCurve()
#   sht = xw.Book.caller().sheets.active
    fig = plt.figure(figsize=(5,2), facecolor=bg_color, edgecolor=border)
    fig.suptitle(pltname, fontsize=SMALL_SIZE, fontweight='bold',color=fg_color)
    #fig.patch.set_facecolor('tab:gray')
    
    primary_axis = fig.add_subplot(111)
    fig.subplots_adjust(top=0.85)

    primary_axis.set_xlabel(labels[0],color=fg_color)
    primary_axis.set_ylabel(labels[1],color=fg_color)
    primary_axis.patch.set_facecolor(bg_color)
    
    primary_axis.xaxis.set_tick_params(color=fg_color, labelcolor=fg_color)
    primary_axis.yaxis.set_tick_params(color=fg_color, labelcolor=fg_color)
    primary_axis.grid(which='major',color=fg_color)
    for spine in primary_axis.spines.values():
        spine.set_color(fg_color)
    primary_axis.legend(bbox_to_anchor=(0.40, 0.30))
    
    secondary_axis = None
    
    if len(labels) == 3:
        secondary_axis = primary_axis.twinx()
        secondary_axis.set_ylabel(labels[2],color=fg_color)
    
        secondary_axis.xaxis.set_tick_params(color=fg_color, labelcolor=fg_color)
        secondary_axis.yaxis.set_tick_params(color=fg_color, labelcolor=fg_color)
        secondary_axis.grid(which='minor',color=fg_color)
        for spine in secondary_axis.spines.values():
            spine.set_color(fg_color)
        secondary_axis.legend(bbox_to_anchor=(0.60, 0.30))
    
#    primary_axis.plot(tenors[1:],zeroes[1:],"yellow",label="Spot")
#    primary_axis.plot(tenors[1:],forwards[1:],"maroon",label="6M Forward")
#    #plt.legend(bbox_to_anchor=(0.60, 0.30))
#    secondary_axis.plot(tenors[1:],discounts[1:],'C6',label="Discount Factors")

    #start, end = ax.get_ylim()
    #stepsize = (end - start - 0.005)/5
    #ax.yaxis.set_ticks(np.arange(start-2*stepsize, end+stepsize, stepsize))

    plt.autoscale()
    plt.tight_layout()

#    primary_axis.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter('{0:.2%}'.format))

    #secondary_axis.legend(loc='lower')
    
    
    #plt.legend([primary_axis,secondary_axis])
#    sht.pictures.add(fig, 
#                     name=pltname, 
#                     update=True,
#                     left=sht.range(location).left,
#                     top=sht.range(location).top)
    #return 'Plotted with years=10'
    
    graph = [fig,primary_axis,secondary_axis]
    return graph
