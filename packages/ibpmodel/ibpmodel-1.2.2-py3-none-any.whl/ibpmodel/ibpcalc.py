#!/usr/bin/python3 -q
"""This module contains the main functions and the auxiliary/control functions needed to calculate the IBP index.
"""

from   scipy import special
import numpy as np
import cdflib
import os
from datetime import datetime

#=== UTILS =====================================================================

def tiler(*args):
    """Provides mixed combinations of arguments.

    Creates copies of the arguments that have length equal to the product of the length of the arguments.
    This results in an ordered set of all combinations of the individual values from each of the arguements.

    Parameters
    ----------

    *args : array-likes
        Each argument is an array-like of possibly different length.

    Returns
    -------

    list of array-likes
        A list of ordered combination of the input arguments.

    Examples
    --------

    >>> from ibpmodel import ibpcalc
    >>> ibpcalc.tiler([1, 2, 3],['A', 'B'])
    [array([1, 1, 2, 2, 3, 3]), array(['A', 'B', 'A', 'B', 'A', 'B'], dtype='<U1')]

    >>> ibpcalc.tiler([17,13],[1, 2, 3],['A', 'B'])
    [array([17, 17, 17, 17, 17, 17, 13, 13, 13, 13, 13, 13]), \
array([1, 1, 2, 2, 3, 3, 1, 1, 2, 2, 3, 3]), \
array(['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'],
          dtype='<U1')]

    """

    arg_number = len(args)
    if arg_number < 1:
        return None
    elif arg_number == 1:
        return np.array(args[0])
        
    lengths    = list(map(len,args))
    maybe_tile = lambda arg,i: np.tile(arg,np.product(lengths[:i])) if i > 0 else arg

    return [
        maybe_tile(
            np.repeat(args[i], np.product(lengths[(i + 1):]))
            if i < arg_number - 1 else args[i], i)
        for i in range(len(args))
    ]
    
def tile_aggregate(result,*args,aggregator=np.mean):
    """Compresses tiles and aggregate results on the last axis of tiled ranges

    Parameters
    ----------
    result : numpy.array
        Array that is aggregated.
    *args : list or numpy.array
        Along the last element is crompressed.
    aggregator :  function, optional
        Specifies how to aggregate. the defaults is `np.mean`.

    Returns
    -------
    list of numpy.array
        last element is the compressed result

    Example
    -------

    >>> from ibpmodel import ibpcalc
    >>> ibpcalc.tile_aggregate(np.array([3,2,3,3,2,1,2,1]), [10,12], [20,21,22,24])
    (10, 12, array([2.75, 1.5 ]))
    
    >>> ibpcalc.tile_aggregate(np.array([3,2]), np.array([12]), np.array([20,21]))
    (12, array([2.5]))
    
    >>> ibpcalc.tile_aggregate(\
np.array([3,2,2,1,4,2,3,3,1,4,8,5,9,6,7,4,5,2,1,6,7,9,5,7]), \
[9,10,11], [20,21], [7,8,5,6])
    (array([ 9,  9, 10, 10, 11, 11]), array([20, 21, 20, 21, 20, 21]), \
array([2. , 3. , 4.5, 6.5, 3.5, 7. ]))

    """
    if len(args) <= 1:
        return aggregator(result)
    *preserved, collapesed = args
    reshaped= result.reshape(np.product(list(map(len,preserved))),len(collapesed))
    return (*tiler(*preserved), aggregator(reshaped, axis=1))

def doyFromMonth(month):
    '''Calculate day of year from the 15th of the month

    Parameters
    ----------
    month : int
        Value as the month in the year, with january being month 1, ``1 <= month <= 12`` 

    Returns
    -------
    int
        Day of year.

    Example
    -------

    >>> from ibpmodel import ibpcalc
    >>> ibpcalc.doyFromMonth(7)
    196

    '''
    doy_month = [15, 46, 74, 105, 135, 166, 196, 227, 258, 288, 319, 349]
    if isinstance(month, (int,np.integer)) and month in range(1,13):
        return doy_month[month-1]
    else:
        raise ValueError("Value " + str(month) + " out of range or wrong type!")

def monthFromDoy(doy):
    '''Calculate month from day of the year

    Parameters
    ----------
    doy : int
        Day of the year, ``1 <= doy <= 365``.

    Returns
    -------
    int
        Value as the month in the year, with january being month 1.

    Example
    -------

    >>> from ibpmodel import ibpcalc
    >>> ibpcalc.monthFromDoy(275)
    10
    '''
    if isinstance(doy, (int,np.integer)) and doy in range(1,366):
        return int(datetime.strptime(str(doy), '%j').month) 
    else:
        raise ValueError("Value " + str(doy) + " out of range or wrong type!")

def monthfromString(month_str):
    '''Convert abbreviated month name to *int*

    Parameters
    ----------
    month_str : str
        Abbreviated month name. *['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',	'Oct', 'Nov', 'Dec']*

    Returns
    -------
    int
        Value as the month in the year, with january being month 1.

    Example
    -------

    >>> from ibpmodel import ibpcalc
    >>> ibpcalc.monthfromString('Mar')
    3
    '''
    months = [ datetime(2000,m,1).strftime("%b") for m in range(1,13) ]
    if isinstance(month_str, str) and month_str in months:
        return months.index(month_str)+1
    else:
        raise ValueError("Wrong month string: " + str(month_str)) 
    
def checkDoyMonth(day_month):
    '''Control if input is day of the year (*int*) or abbreviated month name (*str*).  

    Parameters
    ----------
    day_month : int or str or list
        Value to be checked

    Returns
    -------
    doy_out : list of int(s)
        list of days of the year

    Example
    -------

    >>> from ibpmodel import ibpcalc
    >>> ibpcalc.checkDoyMonth(['Mar',200,1])
    [74, 200, 1]

    >>> ibpcalc.checkDoyMonth('Dec')
    [349]
    '''
    if not isinstance(day_month, list):
        day_month = [day_month]
    
    doy_out = []
    for e in day_month:
        if isinstance(e, str):
            doy_out.append(doyFromMonth(monthfromString(e)))
        elif isinstance(e, int) and e in range(1,366):
            doy_out.append(e)
        else:
            raise ValueError("Wrong day_month value: " + str(e)) 
    
    return doy_out
     
def checkParameter(para, para_range):
    '''Check if *para* or element of *para* in *para_range*.

    Parameters
    ----------
    para : int or float or list
        Value to be checked
    para_range : range
        searching range

    Returns
    -------
    numpy.array
        Numpy.array contains *para*.

    Example
    -------

    >>> from ibpmodel import ibpcalc
    >>> ibpcalc.checkParameter(3,range(0,5))
    array([3])
    
    >>> ibpcalc.checkParameter([0,1,2,3,4],range(0,5))
    array([0, 1, 2, 3, 4])
    '''
    if isinstance(para, (list,np.ndarray)) and not False in list(map(lambda i: True if para_range[0] <= i <= para_range[-1] else False, para)):
        return np.array(para)
    elif isinstance(para, (float, int)) and para_range[0] <= para <= para_range[-1]:
        return np.array([para])
    else:
        raise ValueError("Value " + str(para) + " out of range or wrong type!")
    
#=== IBP ROUTINES =============================================================

def read_model_file(file=None):
    """Load CDF content into a dictionary. If no file is declared, the CDF file included in the package will be used. 
    (SW_OPER_IBP_CLI_2__00000000T000000_99999999T999999_0002.cdf)
    
    Parameters
    ----------
    file : file path, optional
        Path to cdf file containing parametors for the model. The default is None.
        
    Returns
    -------
    dict
        Contains the content of the CDF file.

    """

    if file == None:
        basepath = os.path.dirname(__file__)
        file = os.path.abspath(os.path.join(basepath,'SW_OPER_IBP_CLI_2__00000000T000000_99999999T999999_0002.cdf'))
    
    data = {}
    cdf = cdflib.CDF(file)

    for key in [
            'Parameters',
            'Intensity',
            'Monthly_LT_Shift',
            'Density_Estimators',
            'Density_Estimator_Lons'
        ]:
        data[key] = cdf.varget(key)

    cdf.close()
    return data
 

def compute_probability(time, expected_bubbles, expected_lifetime, mu, sigma):
    """Computes the probability of Ionospheric Plasma Bubbles. 

    Parameters
    ----------
    time : float or ndarray of floats
        The local time, can be eiter as an array or not.

    expected_bubbles : float or ndarray of floats
        The expected amount of bubbles, can be eiter as an array or not.

    expected_lifetime : float or ndarray of floats
        The expected lifetime of each bubble, can be eiter as an array or not.

    mu : float or ndarray of floats
        The mean position of the probability distribution in the model, can be eiter as an array or not.

    sigma : float or ndarray of floats
        The standard deviation of the probability distribution in the model, can be eiter as an array or not.
        
    Returns
    -------
    float or ndarray of floats
        The Ionospheric Bubble Index, value(s) between 0.0 and 1.0, it has the same length as all of the inputs

    Note
    ----
    Plasma Bubbles are large-scale depletions compared to the background
    ionosphere,  occurring in  the  equatorial  F-region, in  particular
    after  sunset.   They  are   assumably  driven   by  Rayleigh-Taylor
    instability and already in the past extensively studied by different
    techniques,   showing   occurrence    probabilities   depending   on
    evironmental  parameters as  season,  location, local  time and  sun
    activity.

    For a climatologic model of these dependencies, extracted from fairly 
    long time series of distortions in the magnetic field readings of the 
    LEO satellites CHAMP (2000-2010) and Swarm (since 2013) the function
    calculates a probability density.


    Examples
    --------

    >>> import numpy as np
    >>> from ibpmodel import ibpcalc
    >>> ibpcalc.compute_probability(0.0,0.5,0.5,0.5,0.5)
    0.049701856965716384
    
    >>> a = np.arange(24)+0.5
    >>> ibpcalc.compute_probability(a,a,a,a,a)
    array([0.12259724, 0.32454412, 0.48001002, 0.5996932 , 0.69182957,
           0.76275943, 0.81736377, 0.85940013, 0.89176121, 0.91667393,
           0.93585262, 0.95061706, 0.96198326, 0.97073336, 0.9774695 ,
           0.98265522, 0.98664737, 0.98972067, 0.99208661, 0.99390799,
           0.99531015, 0.99638959, 0.99722058, 0.9978603 ])
    
    >>> ibpcalc.compute_probability(a,2*a,1.2,1.3,0.4)
    array([2.00069488e-02, 7.81272947e-01, 8.55868576e-01, 6.93670227e-01,
           4.83704476e-01, 2.96120013e-01, 1.65026216e-01, 8.64714939e-02,
           4.35684741e-02, 2.14048463e-02, 1.03395302e-02, 4.93490050e-03,
           2.33423700e-03, 1.09629097e-03, 5.11888048e-04, 2.37840684e-04,
           1.10040886e-04, 5.07234746e-05, 2.33043267e-05, 1.06755465e-05,
           4.87751438e-06, 2.22316484e-06, 1.01112283e-06, 4.58962618e-07])
    """

    expected_bubbles = np.maximum(0,np.array(expected_bubbles, dtype = 'float'))
    lambda_1         = np.array(expected_bubbles,              dtype = 'float')
    lambda_2         = np.array(1 / expected_lifetime,         dtype = 'float')
    mu               = np.array(mu,                            dtype = 'float')
    sigma            = np.array(sigma,                         dtype = 'float')
    time             = np.array(time,                          dtype = 'float')

    # Transform problem to be purely in terms of error function
    # (by Ask Neve Gamby). Based on rewriting the integrant to an
    # exponential of a quadric polynomia, and then using coordinate
    # transformation and scaling of y axis to go to a basic
    # exp(-x**2) form, which can be easily evaluated by an error function

    outer_mult            = -1. / (2 * np.pi * sigma**2)**0.5
    inner_mult            = -1. / (2*sigma**2)
    x0                    = mu - lambda_2 / (2*inner_mult)
    y0                    = lambda_2 * (mu - time - lambda_2 / (4 * inner_mult))
    inner_mult_sqrt       = (-inner_mult)**0.5
    outer_mult_corrected2 = (np.pi)**0.5 * outer_mult * np.exp(y0) / inner_mult_sqrt
    integrated            = (0.5 + special.erf(
                                 (time - x0) * inner_mult_sqrt
                             ) * 0.5) * outer_mult_corrected2

    return 1.0 - np.exp(lambda_1 * integrated)


def fourier_model(coeffients, theta, periode = 365.0):
    """Computes a value based on a model of fourier components up to 2nd degree.
    
    Parameters
    ----------
    coeffients : array-like of numbers
        The coefficients of the fourier series up to second degree,
        with even numbers representing cosinus and odd sinus.
        The shape of `coefficients` must be *(5,*theta.shape)*.
    theta : number or ndarray of numbers
        The part representing the phase in the fourier expansion.
        It is in the same units as the periode.
    periode : number, optional
        The amount of `theta` need for one periode of the 1st degree 
        of the fourier expansion. Defaults to 365 (the days in a year).
    
    Returns
    -------
    number or ndarray of numbers
        The shape of this is equivalent to the shape of `theta`.
        
    Examples
    --------

    >>> from ibpmodel import ibpcalc
    >>> import numpy as np
    >>> ibpcalc.fourier_model([0,1,-1,0,0],180)
    1.0420963481067607
    
    >>> ibpcalc.fourier_model([0,1,-1,-0.5,0.7],1,periode=10)
    -0.48044810416758793
    
    >>> ibpcalc.fourier_model([0,1,-1,-0.5,0.7],np.arange(11),10)
    array([-0.3       , -0.4804481 , -0.218165  ,  0.98765424,  2.0886424 ,
            1.7       , -0.03798462, -1.50224404, -1.53249278, -0.70496209,
           -0.3       ])

    """

    base  = theta * (np.pi * 2. / periode)
    base2 = base * 2

    return (
        coeffients[0] +
        coeffients[1] * np.sin(base)  +
        coeffients[2] * np.cos(base)  +
        coeffients[3] * np.sin(base2) +
        coeffients[4] * np.cos(base2)
    )
    
    
def compute_lambda(longitude, params, f107, gosc_val, density, month = 0):
    """Computes the 'lambda' parameter.
    Lambda is the intensity, one of the parameters describing
    the final probability and modeled as a Poisson process.

    Parameters
    ----------
    longitude : float or ndarray of floats
        The longitude(s) of the point(s) we calculate lambda for.
    params : array-like
        Parameter values from the model (CDF-file).
    f107 : float or ndarray of floats
        The Solar Radio Flux (F10.7 index).
    gosc_val : float or ndarray of floats
        result of method `fourier_model()`
    density : ndarray of floats
        Density values from the model (CDF-file).
    month : int or ndarray of ints, optional
        The number of months since the year started, meaning January would 
        be 0. The default is 0.

    Returns
    -------
    float or ndarray of floats

    Examples
    --------

    >>> from ibpmodel import ibpcalc
    >>> import numpy as np
    >>> ibpcalc.compute_lambda(1,[-232.54229262, 4.67324294], 123.4, 17.3, \
np.array([2.1,3.0]))
    1084.307658528

    >>> params = np.array([-232.54229262, 4.67324294, 1.34695254, -1.31448553, 1.09712955])
    >>> densi_once = np.sin(np.arange(360)*np.pi/180) * 3 + 5
    >>> ibpcalc.compute_lambda(1,[-232.54229262, 4.67324294], 123.4, 17.3, densi_once)
    1788.2556529203105
    
    >>> densi_year = np.array([ (densi_once -3)* np.cos(month*np.pi/6) \
+ 8 for month in range(12)])
    >>> ibpcalc.compute_lambda(1,[-232.54229262, 4.67324294], 123.4, 17.3, densi_year, \
month=5)
    1851.5944384882494
    
    >>> months = np.array((np.sin(np.arange(20))+1) % 12, dtype='int')
    >>> ibpcalc.compute_lambda(1,[-232.54229262, 4.67324294], 123.4, 17.3, \
densi_year[:,months], month=months)
    array([2149.6915391, 2149.6915391, 2149.6915391, 2149.6915391,
           2149.6915391, 2149.6915391, 2149.6915391, 2149.6915391,
           2149.6915391, 2149.6915391, 2149.6915391, 2149.6915391,
           2149.6915391, 2149.6915391, 2149.6915391, 2149.6915391,
           2149.6915391, 2149.6915391, 2149.6915391, 2149.6915391])

    """

    number_of_density = np.prod(density.shape)
    selection         = np.array(
        (longitude + 180.) *
        (number_of_density / 360) + month,
        dtype = 'int'
    )
    selected_density = density.reshape(number_of_density)[selection]
    return np.maximum(
        0,
        selected_density * (params[0] + f107 * params[1] + gosc_val)
    )

def align_time_of_year(day_of_year, month):
    """Guess day of year and month from each other.
    
    Parameters
    ----------
    day_of_year : int or ndarray of ints
        Time as the day of year, restricted to ``0 < day_of_year <= 365``,
        with the value 0 meaning it should be calculated based on `month`
        (which gives the median day of the `month`).
    month : int or ndarray of ints
        Time as the month in the year, with january being month 1,
        so ``0 < month <= 12``.
    
    Returns
    -------
    day_of_year : int or ndarray of ints
        A recalculated possible copy of the `day_of_year` parameter.
    month : int or ndarray of ints
        A recalculated copy of the `month` parameter.
        
    Examples
    --------

    >>> from ibpmodel import ibpcalc
    >>> import numpy as np
    >>> ibpcalc.align_time_of_year(0,6)
    (166, 6)
    >>> ibpcalc.align_time_of_year(162,3)
    (162, 6)
    >>> ibpcalc.align_time_of_year(0,np.arange(12)+1)
    (array([ 16,  45,  75, 105, 136, 166, 197, 228, 258, 289, 319, 350]), array([ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12]))

    >>> ibpcalc.align_time_of_year(np.array([0,33,21,17,267,0,115,96,315,0,172,256]),np.arange(12)+1)
    (array([ 16,  33,  21,  17, 267, 166, 115,  96, 315, 289, 172, 256]), array([ 1,  2,  1,  1,  9,  6,  4,  4, 11, 10,  6,  9]))
    
    """

    # This is a side-effect free version by Ask Neve Gamby.
    #
    # 2019-03-05: Now always recalculating 'month' (clumsy type handling?),
    #             Martin Rother (rother@gfz-potsdam.de).

    is_array = isinstance(day_of_year,np.ndarray)
    if is_array != isinstance(month,np.ndarray):
        #ensure that both now are arrays
        if is_array:
            month = np.array([month] * len(day_of_year))
        else:
            day_of_year = np.array([day_of_year] * len(month))
            is_array = True
    
    days_in_month     = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    days_at_month     = np.cumsum([0, *days_in_month])

    if (    
            not is_array and day_of_year     == 0
            or  is_array and any(day_of_year == 0) 
        ):
        
        day_of_year_guess = days_at_month[:-1] + days_in_month // 2 + (days_in_month % 2 > 0 )
        guesses           = day_of_year_guess[month - 1]

        if is_array:
            day_of_year                   = np.array(day_of_year)
            day_of_year[day_of_year == 0] = guesses[day_of_year == 0]
        else:
            day_of_year = guesses

    month = sum(day_of_year > dat for dat in days_at_month)
    return (day_of_year, month)


def compute_probability_exp(day_of_year, month, longitude, local_time, f107, data):
    """Compute the Ionospheric Bubble index.
    Core routine to return a probability of the occurence of a bubble.

    Parameters
    ----------
    day_of_year : int or ndarray of ints
        Time as the day of year, restricted to ``0 < day_of_year <= 356``,
        with the value 0 meaning it should be calculated based on month
        (which gives the median day of the month).

    month : int or ndarray of ints
        Time as the month in the year, with january being month 1, ``0 < month <= 12``.

    longitude : float or ndarray of floats
        The geographical longitude(s), ``-180 <= longitude <= 180``.

    local_time : float or ndarray of floats
        The local time, can be eiter as an array or not, ``-6.0 <= local_time <= 24``.

    f107 : float or ndarray of floats
        The Solar Radio Flux (F10.7 index), ``0.0 <= f107 <= 200.0``.

    data : dict
        Containing the parameters of the model (CDF-file).
        
    Returns
    -------

    float or ndarray of floats
        The Ionospheric Bubble Index, value(s) between 0.0 and 1.0,
        it has the same length as all of the inputs
        
    Examples
    --------

    >>> from ibpmodel import ibpcalc
    >>> import numpy as np
    >>> data = ibpcalc.read_model_file()
    >>> ibpcalc.compute_probability_exp(0, 3, 12, 2, 150, data)
    0.04537450559812162
    
    >>> ibpcalc.compute_probability_exp(0, 2, 12, 2, 150, data)
    0.03213949936284399
    
    Note
    ----
    Rearranged/rewritten and optimized by 
    Ask Neve Gamby <aknvg@space.dtu.dk>.

    The resolution of the function `gosc` is higher than monthly.
    If a `day_of_year` is known, the results can be more precise.

    It is now possible to calculate with either ndarrays or single values,
    for all parameters except data (which has a special structure).
    Note that this version is, compared with the initial version
    more closely resembling the original 'R' code, much more efficient
    due to vectorization.

    """

    # CHECKS:

    if np.any( (local_time < -6.0) | (local_time >  24.0) ):
        raise ValueError("Local time(s) or hour to midnight out of range!")
        
    #if np.any( (f107       <  0.0) | (f107       > 200.0) ):
    #    raise ValueError("F10.7 parameter(s) out of valid range!")

    # Normalize time selected
    
    (day_of_year, month) = align_time_of_year(day_of_year, month)
    
    # Extraction

    density     = np.array(data['Density_Estimators'])
    shifts      = np.array(data['Monthly_LT_Shift'  ])
    params      = np.array(data['Parameters'        ])
    gosc        = np.array(data['Intensity'         ])
    gosc_val    = fourier_model(gosc, day_of_year, 365.0)
       
    # Force LT to be between -6 and 6 (needed by model)

    local_time  = ((local_time + 12) % 24) - 12

    lambda0     = compute_lambda(
        longitude,
        params,
        f107,
        gosc_val,
        density,
        month - 1
    )

    shifttime   = fourier_model(shifts[:, month - 1], longitude, 360.0)
    
    return compute_probability(

        local_time,
        lambda0,
        params[2],
        params[3] + shifttime,
        params[4]

    )
#===============================================================================

if __name__ == "__main__": 
    import doctest
    doctest.testmod()