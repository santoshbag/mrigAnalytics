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

    bg_color = 'white'#'dimgray'
    fg_color = 'black'
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



"""
HELP

Version 3.0.2matplotlib Fork me on GitHub
indexmodules |next |previous |home| examples| tutorials| API| docs »The Matplotlib API »axes »
Quick search

Table of Contents
matplotlib.axes.Axes.plot
Examples using matplotlib.axes.Axes.plot
Related Topics
Documentation overview
The Matplotlib API
axes
Previous: matplotlib.axes.subplot_class_factory
Next: matplotlib.axes.Axes.errorbar
Show Page Source
matplotlib.axes.Axes.plot
Axes.plot(*args, scalex=True, scaley=True, data=None, **kwargs)[source]
Plot y versus x as lines and/or markers.

Call signatures:

plot([x], y, [fmt], data=None, **kwargs)
plot([x], y, [fmt], [x2], y2, [fmt2], ..., **kwargs)
The coordinates of the points or line nodes are given by x, y.

The optional parameter fmt is a convenient way for defining basic formatting like color, marker and linestyle. It's a shortcut string notation described in the Notes section below.

>>> plot(x, y)        # plot x and y using default line style and color
>>> plot(x, y, 'bo')  # plot x and y using blue circle markers
>>> plot(y)           # plot y using x as index array 0..N-1
>>> plot(y, 'r+')     # ditto, but with red plusses
You can use Line2D properties as keyword arguments for more control on the appearance. Line properties and fmt can be mixed. The following two calls yield identical results:

>>> plot(x, y, 'go--', linewidth=2, markersize=12)
>>> plot(x, y, color='green', marker='o', linestyle='dashed',
...      linewidth=2, markersize=12)
When conflicting with fmt, keyword arguments take precedence.

Plotting labelled data

There's a convenient way for plotting objects with labelled data (i.e. data that can be accessed by index obj['y']). Instead of giving the data in x and y, you can provide the object in the data parameter and just give the labels for x and y:

>>> plot('xlabel', 'ylabel', data=obj)
All indexable objects are supported. This could e.g. be a dict, a pandas.DataFame or a structured numpy array.

Plotting multiple sets of data

There are various ways to plot multiple sets of data.

The most straight forward way is just to call plot multiple times. Example:

>>> plot(x1, y1, 'bo')
>>> plot(x2, y2, 'go')
Alternatively, if your data is already a 2d array, you can pass it directly to x, y. A separate data set will be drawn for every column.

Example: an array a where the first column represents the x values and the other columns are the y columns:

>>> plot(a[0], a[1:])
The third way is to specify multiple sets of [x], y, [fmt] groups:

>>> plot(x1, y1, 'g^', x2, y2, 'g-')
In this case, any additional keyword argument applies to all datasets. Also this syntax cannot be combined with the data parameter.

By default, each line is assigned a different style specified by a 'style cycle'. The fmt and line property parameters are only necessary if you want explicit deviations from these defaults. Alternatively, you can also change the style cycle using the 'axes.prop_cycle' rcParam.

Parameters:	
x, y : array-like or scalar
The horizontal / vertical coordinates of the data points. x values are optional. If not given, they default to [0, ..., N-1].

Commonly, these parameters are arrays of length N. However, scalars are supported as well (equivalent to an array with constant value).

The parameters can also be 2-dimensional. Then, the columns represent separate data sets.

fmt : str, optional
A format string, e.g. 'ro' for red circles. See the Notes section for a full description of the format strings.

Format strings are just an abbreviation for quickly setting basic line properties. All of these and more can also be controlled by keyword arguments.

data : indexable object, optional
An object with labelled data. If given, provide the label names to plot in x and y.

Note

Technically there's a slight ambiguity in calls where the second label is a valid fmt. plot('n', 'o', data=obj) could be plt(x, y) or plt(y, fmt). In such cases, the former interpretation is chosen, but a warning is issued. You may suppress the warning by adding an empty format string plot('n', 'o', '', data=obj).

Returns:	
lines
A list of Line2D objects representing the plotted data.

Other Parameters:	
scalex, scaley : bool, optional, default: True
These parameters determined if the view limits are adapted to the data limits. The values are passed on to autoscale_view.

**kwargs : Line2D properties, optional
kwargs are used to specify properties like a line label (for auto legends), linewidth, antialiasing, marker face color. Example:

>>> plot([1,2,3], [1,2,3], 'go-', label='line 1', linewidth=2)
>>> plot([1,2,3], [1,4,9], 'rs',  label='line 2')
If you make multiple lines with one plot command, the kwargs apply to all those lines.

Here is a list of available Line2D properties:

Property	Description
agg_filter	a filter function, which takes a (m, n, 3) float array and a dpi value, and returns a (m, n, 3) array
alpha	float
animated	bool
antialiased	bool
clip_box	Bbox
clip_on	bool
clip_path	[(Path, Transform) | Patch | None]
color	color
contains	callable
dash_capstyle	{'butt', 'round', 'projecting'}
dash_joinstyle	{'miter', 'round', 'bevel'}
dashes	sequence of floats (on/off ink in points) or (None, None)
drawstyle	{'default', 'steps', 'steps-pre', 'steps-mid', 'steps-post'}
figure	Figure
fillstyle	{'full', 'left', 'right', 'bottom', 'top', 'none'}
gid	str
in_layout	bool
label	object
linestyle	{'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
linewidth	float
marker	unknown
markeredgecolor	color
markeredgewidth	float
markerfacecolor	color
markerfacecoloralt	color
markersize	float
markevery	unknown
path_effects	AbstractPathEffect
picker	float or callable[[Artist, Event], Tuple[bool, dict]]
pickradius	float
rasterized	bool or None
sketch_params	(scale: float, length: float, randomness: float)
snap	bool or None
solid_capstyle	{'butt', 'round', 'projecting'}
solid_joinstyle	{'miter', 'round', 'bevel'}
transform	matplotlib.transforms.Transform
url	str
visible	bool
xdata	1D array
ydata	1D array
zorder	float
See also

scatter
XY scatter plot with markers of varying size and/or color ( sometimes also called bubble chart).
Notes

Format Strings

A format string consists of a part for color, marker and line:

fmt = '[color][marker][line]'
Each of them is optional. If not provided, the value from the style cycle is used. Exception: If line is given, but no marker, the data will be a line without markers.

Colors

The following color abbreviations are supported:

character	color
'b'	blue
'g'	green
'r'	red
'c'	cyan
'm'	magenta
'y'	yellow
'k'	black
'w'	white
If the color is the only part of the format string, you can additionally use any matplotlib.colors spec, e.g. full names ('green') or hex strings ('#008000').

Markers

character	description
'.'	point marker
','	pixel marker
'o'	circle marker
'v'	triangle_down marker
'^'	triangle_up marker
'<'	triangle_left marker
'>'	triangle_right marker
'1'	tri_down marker
'2'	tri_up marker
'3'	tri_left marker
'4'	tri_right marker
's'	square marker
'p'	pentagon marker
'*'	star marker
'h'	hexagon1 marker
'H'	hexagon2 marker
'+'	plus marker
'x'	x marker
'D'	diamond marker
'd'	thin_diamond marker
'|'	vline marker
'_'	hline marker
Line Styles

character	description
'-'	solid line style
'--'	dashed line style
'-.'	dash-dot line style
':'	dotted line style
Example format strings:

'b'    # blue markers with default shape
'ro'   # red circles
'g-'   # green solid line
'--'   # dashed line with default color
'k^:'  # black triangle_up markers connected by a dotted line

"""