#!/usr/bin/env python3
"""This module contains the application functions for the calculation of the IBP index as well as the graphical visualization.
"""
from .ibpcalc import *
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings

def calculateIBPindex(day_month=0, longitude=list(range(-180,180,5)), local_time=np.arange(-6,6.1,0.1), f107=150, coeff=None):
    '''Calculates the Ionospheric Bubble propability index based on the input parameters. 
    Returns a *pandas.DataFrame* with input parameters and IBP index. 

    Parameters
    ----------
    day_month : int or str or list, optional
        Day of year (*int*) or the month of the year (*str*). 
        *int*: Day of the year, ``0 <= doy <= 365``. The value 0 means it should be calculated based on every month.
        *str*: Abbreviated month name. ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        The default is 0.
    longitude : int or list of ints, optional
        The geographical longitude(s), ``-180 <= longitude <= 180``. The default is `list(range(-180,180,5))`.
    local_time : int or float or list, optional
        The local time, ``-6.0 <= local_time <= 24``. The default is `np.arange(-6,6.1,0.1)`.
    f107 : int or float or list, optional
        The Solar Radio Flux (F10.7 index), ``80.0 <= f107``. The default is 150.
    coeff : None or str, optional
        Name of the coefficient file.
        The default is None.

    Returns
    -------
    df : pandas.DataFrame
        contains the columns: Doy (Day(s) of the year), Month (Month(s) from the day of the year), 
        Lon (Longitude(s)), LT (Local Time(s)), F10.7 (solar index(es)), IBP (Ionospheric Bubble Index, value(s) between 0.0 and 1.0).
    '''

    
    df = pd.DataFrame(columns=['Doy','Month','Lon','LT','F10.7','IBP'])
    
    if day_month == 0:
        day_of_year = np.array([ doyFromMonth(i) for i in range(1,13) ])
    else:
        day_of_year = np.array(checkDoyMonth(day_month))
       
    longitude_range = range(-180,181)
    longitude = checkParameter(longitude, longitude_range).astype(int)
    longitude[longitude == 180] = -180

    local_time_range = range(-6,25)
    local_time = checkParameter(local_time, local_time_range) 

    f107_range = range(80,1000)
    f107 = checkParameter(f107, f107_range)
    if max(f107) > 200:
        warnings.warn('You are using values for Solar Radio Flux greater than 200sfu. \nPlease note: The model is not designed for these values.')

    data = read_model_file(coeff)

    parts = tiler(day_of_year, longitude, local_time, f107)

    for i, c in enumerate(['Doy', 'Lon', 'LT', 'F10.7']):
        df[c] = parts[i]

    df['Month'] = [ monthFromDoy(i) for i in df['Doy'] ]

    df['IBP'] = compute_probability_exp(
        df['Doy'].to_numpy(), 
        df['Month'].to_numpy(), 
        df['Lon'].to_numpy(), 
        df['LT'].to_numpy(), 
        df['F10.7'].to_numpy(),
        data=data)

    df['IBP'] = df['IBP'].round(4)

    return df

def butterflyData(f107=150, coeff=None):
    '''Calculates the Ionospheric Bubble Propability Index for all months (using the center DOY of each month) and all integer longitudes (resolution of 5 degree)
    using Local_Time of range -5 to 1 and a fixed value of F10.7. IBP index is then averaged from the Local_Times.

    Parameters
    ----------
    f107 : int, optional
        The Solar Radio Flux (F10.7 index). The default is 150.

    Returns
    -------
    out_data : numpy.array
        [[month],[longitude],[IBP index]].

    '''
    month_range       = np.arange(   1,  13,    1)
    longitude_range   = np.arange(-180, 179,  5.0)
    local_time_range  = np.arange(  -5,   1, 0.01)

    month, longitude, local_time = tiler(
        np.array(month_range,dtype='int'),longitude_range,local_time_range)

    data = read_model_file(coeff)
    
    day_of_year = np.array([ doyFromMonth(t) for t in month ])
    result = compute_probability_exp(
        day_of_year,month,longitude,local_time,f107,data)

    out_data = np.array(tile_aggregate(result,month_range,longitude_range,local_time_range)).transpose()
    
    return out_data
    
def getcolorbar(cmap, level=np.arange(0.0, 1.05, 0.05)):
    '''Applies level to colormap.
    
    Parameters
    ----------
    cmap : matplotlib.colors.Colormap

    level : array-like
    
    Returns
    -------
    matplotlib.cm.ScalarMappable
    '''

    norm = mpl.colors.BoundaryNorm(level, cmap.N)
    return mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
 
def setcolorbar(scalarmap, fig, ax, **kwargs):
    '''Sets colorbar to figure on the specified axis.

    Parameters
    ----------
    scalarmap : matplotlib.cm.ScalarMappable

    fig : matplotlib.figure.Figure

    ax : matplotlib.axes

    Returns
    -------
    colorbar
    '''
    cbar = fig.colorbar(scalarmap, ax=ax, label='Ionospheric Bubble Probability', **kwargs)
    return cbar

def checkcmap(cmap):
    '''Check if variable is a color map.

    Parameters
    ----------
    cmap : str or matplotlib.colors.Colormap

    Returns
    -------
    matplotlib.colors.Colormap

    '''
    try:
        if isinstance(cmap, str):
            cmap = mpl.colormaps[cmap]
        if not isinstance(cmap, (mpl.colors.LinearSegmentedColormap, mpl.colors.ListedColormap)):
            raise ValueError(f"'{cmap}' of type {type(cmap)} is not a valid for colormap")
    except Exception as err:
            print(err)
            print("Default colormap 'viridis' is used!")
            cmap = mpl.colormaps['viridis']
 
    return cmap


def plotIBPindex(doy, f107=150, ax=None, coeff=None, cmap='coolwarm', colors='b', linewidths=0.2, **kwargs):
    '''Create a contour plot of IBP index for the given day. The resolution along the longitude is 5 degree. Local time spans from 6 pm to 6 am with a resolution of 0.1 hours. Default colormap is 'coolwarm'. 

    Parameters
    ----------
    doy : int or str
        Day of year (*int*) or the month of the year (*str*). 
        *int*: Day of the year, ``0 <= doy <= 365``. The value 0 means it should be calculated based on every month.
        *str*: Abbreviated month name. ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    f107 : int or float, optional
        The Solar Radio Flux (F10.7 index). The default is 150.
    ax : matplotlib.axes, optional
        The Axes object in which the plot will be drawn. The default is None.
    coeff : str, optional
        Path of coefficient file. The default is None.
    cmap : str or Colormap, optional
        The colormap instance or registered colormap name to use. The default is 'coolwarm'.
    colors : color string or sequence of colors, optional
        The color of the contour lines. The default is 'blue'.
    linewidths : float, optional
        The line width of the contour lines. The default is 0.2.

    Returns
    -------
    matplotlib.axes, matplotlib.cm.ScalarMappable

    '''

    if isinstance(doy, (int, str)):
        doy = checkDoyMonth(doy)[0]
    else:
        raise ValueError(f"'{doy}' must be of type int or str, not  {type(doy)}")

    df = calculateIBPindex(day_month=doy, f107=f107, coeff=coeff)
    
    value_size = np.unique(df['Lon'].to_numpy(), return_counts=True)
    value_size = ( len(value_size[0]), value_size[1][0] )
    
    x = np.transpose(df['Lon'].to_numpy().reshape(value_size))
    y = np.transpose(df['LT'].to_numpy().reshape(value_size))
    z = np.transpose(df['IBP'].to_numpy().reshape(value_size))
    
    if ax == None:
        fig, ax = plt.subplots(figsize = (9, 4))
        pltshow = True
    else:
        pltshow = False
    
    cmap = checkcmap(cmap)

    levels = np.arange(0.0, 1.05, 0.05)
    scalarmap = getcolorbar(cmap, levels)
    
    ax.contourf(x, y, z, levels=levels, cmap=cmap, **kwargs)
    ax.contour(x, y, z, levels=levels, colors=colors, linewidths=linewidths, **kwargs)

    ticks_loc = ax.get_yticks().tolist()
    ax.yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
    ax.set_yticklabels([f"{int(24+i)}:00" if i < 0 else f"0{int(i)}:00" for i in ticks_loc]) 

    ax.set_title('IBP index at doy ' + str(doy)+' with F10.7 = ' + str(f107))
    ax.set_xlabel('Longitude in degree')
    ax.set_ylabel('Local Time')

    if pltshow:
        setcolorbar(scalarmap, fig, ax)
        
        plt.subplots_adjust(right=1, bottom=0.15)
        plt.show()
    else:
        return (ax, scalarmap)

def plotButterflyData(f107=150, ax=None, coeff=None, cmap='plasma_r', colors='#999900', linewidths=0.2, **kwargs):
    '''Create a contour plot of the result from function butterflyData(). Default colormap is 'plasma_r'. 

    Parameters
    ----------
    f107 : int or float, optional
        The Solar Radio Flux (F10.7 index). The default is 150.
    ax : matplotlib.axes, optional
        The Axes object in which the plot will be drawn. The default is None.
    coeff : str, optional
        Path of coefficient file. The default is None.
    cmap : str or Colormap, optional
        The colormap instance or registered colormap name to use. The default is 'plasma_r'.
    colors : color string or sequence of colors, optional
        The color of the contour lines. The default is '#999900'.
    linewidths : float, optional
        The line width of the contour lines. The default is 0.2.

    Returns
    -------
    matplotlib.axes, matplotlib.cm.ScalarMappable

    '''
    d = butterflyData(f107, coeff)
    
    y = np.transpose(np.reshape(d[:, 0], (12, 72)))
    x = np.transpose(np.reshape(d[:, 1], (12, 72)))
    z = np.transpose(np.reshape(d[:, 2], (12, 72)))

    l = np.arange(0.0, 0.85, 0.05)

    if ax == None:
        fig, ax = plt.subplots(figsize = (6.2, 5.0))
        pltshow = True
    else:
        pltshow = False
    
    cmap = checkcmap(cmap)
    
    scalarmap = getcolorbar(cmap, l)
           
    ax.contourf(x, y, z, l, cmap = cmap, **kwargs)
    ax.contour(x, y, z, levels=l, colors = colors, linewidths = linewidths, **kwargs)
    
    ax.set_title('Monthly IBP index with F10.7 = '+str(f107))
    ax.set_xlabel('Longitude in degree')
    ax.set_ylabel('Month')
    
    if pltshow:
        setcolorbar(scalarmap, fig, ax)        
        plt.show()
    else:
        return ax, scalarmap


    
