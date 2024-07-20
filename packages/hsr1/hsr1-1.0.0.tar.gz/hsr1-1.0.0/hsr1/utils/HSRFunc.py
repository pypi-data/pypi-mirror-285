# -*- coding: utf-8 -*-
"""
copyright 2024 Peak Design
this file is part of hsr1, which is distributed under the GNU Lesser General Public License v3 (LGPL)
"""
import os
import datetime as dt
import time
import importlib_resources

import numpy as np
import pandas as pd
import matplotlib.pyplot as pl
import matplotlib.dates as mdates
import ephem
import scipy.interpolate as interpolate
import zipfile

# Program to load hsr1 Raw text datafiles. Caches them to HDF


def calc_direct_normal_spectrum(global_spectrum, diffuse_spectrum, sza):
    """calculates the direct normal spectrum from the diffuse, global and zenith angle
    params:
        global_spectrum, diffuse_spectrum: pandas Series of numpy arrays, each array representing one spectral reading
        sza: pandas Series one float(radians) per reading
    """
    direct_horizontal_spectrum = global_spectrum-diffuse_spectrum
    direct_normal_spectrum = direct_horizontal_spectrum/np.cos(sza)
    
    return direct_normal_spectrum
    

def calc_sun_zenith(ts, lat, lon):
    """calculates the solar zenith angle at a specific time and location
    quite slow as this has to be run in a for loop, sg2's calculation is much faster
    """
    obs = ephem.Observer()
    sun = ephem.Sun()

    obs.date = ts
    obs.lat, obs.lon = str(lat), str(lon)

    sun.compute(obs)

    return 90 - (sun.alt * 180. / np.pi), sun.az * 180. / np.pi

def calc_rayleigh(wl, pressure = 1013.25):
    """calculates the rayleigh scattering for one reading
    params:
        wl: the wavelength(s) to calculate the scattering over.
            this can be a scalar, numpy array or pandas series
        pressure: the pressure in hPa
    return is in the same datatype as the wl parameter
    """
    a1 = 117.25942 # model Rayleigh scattering 
    a2 = -1.3215
    a3 = 0.00032073
    a4 = -0.000076842
    p0 = 1013.25 
    wl  = wl*1e-3 # convert wl from nano to micrometres (for Rayleigh formula)    
    tau_r = (pressure/p0)*(1/(a1*wl**4 + a2*wl**2 + a3 + a4/wl**2))
    return tau_r

def calc_air_mass(Sza, pressure = 1013.25):
    """calculates the airmass
    params:
        Sza: the solar zenith angle in radians.
            this can be a scalar, numpy array or pandas series.
        pressure: the pressure in hPa
    return is in the same datatype as the wl parameter
    """
    a = 0.50572 
    b = 96.07995
    c = 1.6364
    C = np.cos(Sza)
    
    mu = C + a*(b - np.degrees(Sza))**(-c) # atm. air mass (note 1/m in Wood et. al 2019)
    return pressure / 1013.25 / mu

def calc_aot_direct(ed, eds, sza, e_solar, sed=None, aod_type=["total_od", "aod_microtops", "aod_wood_2017"]):
    """calculates the atmospheric optical depth in several different ways
    
    params:
        ed: the global spectral irradiance. columns=wavelength, index=time, timestamp in utc
        eds: the diffuse spectral irradiance. columns=wavelength, index=time, timestamp in utc
        sza: the solar zenith angle in radians. column = "sza", index=time, timestamp in utc
        e_solar: the extraterrestrial solar spectrum. columns=wavelength, index=time, timestamp in utc
        sed: sun earth distance in AU. if None, calculated from time. this is quite slow so this parameter
            can speed it up if you are already loading from the database
        aod_type: the desired outputs string or list of strings
        
    
    returns:
        aod_data: dataframe containing all the requested channels
        to convert a column of numpy arrays into a dataframe of wavelengths against time:
            pd.DataFrame(np.stack(data["spectrum_column"].values), columns = np.arange(300, 1101, 1), index=data["pc_time_end_measurement"])
    
    definition of each aod type:
        tau_t/total_od: the total optical depth from all sources
        tau_a/microtops_aod: the aerosol optical depth. this is the optical depth with rayleigh scattering removed
        tau_corr/aod_wood_2017: the aerosol optical depth with an empirical correction applied to it
    """
    edd = (ed - eds)
    edni = edd.divide(np.cos(sza.values.astype(float)),axis="index")
    
    sun = ephem.Sun()
    
    tau_r = calc_rayleigh(ed.columns.astype(float))
    tau_t = np.nan*np.ones([len(edni),len(edni.T)]) # total OT 
    tau_a = np.nan*np.ones([len(edni),len(edni.T)]) # aerosol OT 
    tau_corr = np.nan*np.ones([len(edni),len(edni.T)]) # corrected OT
    
    wl_e = np.array([440, 500, 675, 870, 1020]) #  empirical correction coefficients (Wood 2017)
    offset_am = np.array([0.0097, 0.0177, -0.0033, -0.0067, -0.0117])
    offset_wl = np.array([0.0244, 0.0260, 0.0182, 0.0124, 0.0457])
    slope_wl = np.array([1.2701, 1.2893, 1.3549, 1.4522, 1.5237])
    
    wl = ed.columns.astype(float)
    offset_am = interpolate.interp1d(wl_e, offset_am, kind = 'linear', axis = 0, fill_value = "extrapolate") # interpolate to wl range of hsr (piecewise linear)
    offset_wl = interpolate.interp1d(wl_e, offset_wl, kind = 'linear', axis = 0, fill_value = "extrapolate")(wl) # linearly extrapolated outside wl range
    slope_wl = interpolate.interp1d(wl_e, slope_wl, kind = 'linear', axis = 0, fill_value = "extrapolate")(wl)
    
    daytime = sza.values < np.radians(90)
    daytime = daytime[:, 0]
    
    
    
    if sed is None:
        sed = np.full(len(edni), np.nan)
        for i in range(len(edni)):
            if sza.iloc[i].values < np.radians(90):
                sun.compute(edni.index[i])
                sed[i] = sun.earth_distance
        sed = pd.Series(sed)
    
    ##### vectorised calculations
    airmasses = calc_air_mass(sza).values[:, 0]
    
    e_toa = pd.DataFrame((e_solar.values/np.array([sed.values]).T**2), columns=e_solar.columns, index=ed.index)
    
    airmasses = airmasses.T[:, np.newaxis]
    offsets = offset_am(airmasses)
    
    dnitoa =edni.divide(e_toa).astype(float)
    tau_t = -1/airmasses*np.log(dnitoa)
    tau_a = tau_t-tau_r.values
    tau_corr = (tau_a - offsets - offset_wl) *slope_wl
    
    tau_t[np.logical_not(daytime)] = np.nan
    tau_a[np.logical_not(daytime)] = np.nan
    tau_corr[np.logical_not(daytime)] = np.nan
    
    aod_data = pd.DataFrame()
    aod_data["pc_time_end_measurement"] = ed.index
    
    if isinstance(aod_type, str):
        aod_type = [aod_type]
    
    if "total_od" in aod_type:
        aod_data["total_od"] = list(tau_t.values)
    if "aod_microtops" in aod_type:
        aod_data["aod_microtops"] = list(tau_a.values)
    if "aod_wood_2017" in aod_type:
        aod_data["aod_wood_2017"] = list(tau_corr.values)
    
    return aod_data


def calc_cimel_band_aot_direct(Ed, Eds, Sza, E_solar, sed, aod_type=["total_od", "aod_microtops", "aod_wood_2017"]) :
    """reduce wavelength range to the cimel measurement bands, and calculate AOTs
    
    params:
        ed: the global spectral irradiance. columns=wavelength, index=time, timestamp in utc
        eds: the diffuse spectral irradiance. columns=wavelength, index=time, timestamp in utc
        sza: the solar zenith angle in radians. column = "sza", index=time, timestamp in utc
        e_solar: the extraterrestrial solar spectrum. columns=wavelength, index=time, timestamp in utc
        sed: sun earth distance in AU. if None, calculated from time. this is quite slow so this parameter
            can speed it up if you are already loading from the database
        aod_type: the desired outputs string or list of strings
        
    
    returns:
        aod_data: dataframe containing all the requested channels
        to convert a column of numpy arrays into a dataframe of wavelengths against time:
            pd.DataFrame(np.stack(data["spectrum_column"].values), columns = np.arange(300, 1101, 1), index=data["pc_time_end_measurement"])
    
    definition of each aod type:
        tau_t/total_od: the total optical depth from all sources
        tau_a/microtops_aod: the aerosol optical depth. this is the optical depth with rayleigh scattering removed
        tau_corr/aod_wood_2017: the aerosol optical depth with an empirical correction applied to it
    """
    
    cimel_band = [380, 440, 500, 675, 870, 1020]
    #Ed_cb = Ed[list(map(str,cimel_band))]
    #Eds_cb=Eds[list(map(str,cimel_band))]
    #solar_cb=E_solar[list(map(str,cimel_band))]
    Ed_cb = Ed[cimel_band]
    Eds_cb = Eds[cimel_band]
    solar_cb = E_solar[cimel_band]
    
    Ed_cb_i = []
    Eds_cb_i = []
    solar_cb_i = []
    for i in range(len(cimel_band)):
        idxrange = list(range(cimel_band[i]-5,cimel_band[i]+6))
        Ed_cb_i.append(Ed[idxrange].mean(axis=1))
        Eds_cb_i.append(Eds[idxrange].mean(axis=1))
        solar_cb_i.append(E_solar[idxrange].mean(axis=1))
    Ed_cb = pd.concat(Ed_cb_i, axis = 1)
    Eds_cb = pd.concat(Eds_cb_i, axis = 1)
    solar_cb = pd.concat(solar_cb_i, axis = 1)
    Ed_cb.columns = cimel_band
    Eds_cb.columns = cimel_band
    solar_cb.columns = cimel_band
         
    return calc_aot_direct(Ed_cb, Eds_cb, Sza, solar_cb, sed, aod_type)
    

def calc_aod_from_df(data, cimel=False, aod_type=["total_od", "aod_microtops", "aod_wood_2017"], wavelengths=None):
    """coerces data from the format returned from the database to the format for the calculation, and back,
    also loads the reference solar spectrum
    params:
        data: dataframe of all the relevant data, columns = ["pc_time_end_measurement", 
                                                             "global_spectrum", "diffuse_spectrum",
                                                             "sza", "sed"]
        cimel: if True, calculates the aod only at certain wavelengths that cimel instruments measure at
        aod_type
    """
    utctime = pd.to_datetime(data["pc_time_end_measurement"]).dt.tz_localize(None)
    
    ed = pd.DataFrame(np.stack(data["global_spectrum"].values), columns = np.arange(300, 1101, 1), index=utctime)
    eds = pd.DataFrame(np.stack(data["diffuse_spectrum"].values), columns = np.arange(300, 1101, 1), index=utctime)
    sza = pd.DataFrame(data["sza"])
    
    if wavelengths is None:
        wavelengths = np.arange(300, 1101, 1)
    else:
        ed = ed[wavelengths]
        eds = eds[wavelengths]
    
    res = importlib_resources.files("hsr1.data").joinpath("SolarSpectrum.txt")
    file = importlib_resources.as_file(res)
    with file as f:
        reference_filepath = f
    e_solar = pd.read_csv(reference_filepath, skiprows=1, delimiter='\t', index_col=0)
    smoothed_e_solar = e_solar.rolling(3).mean().T
    smoothed_e_solar = smoothed_e_solar.fillna(e_solar.T)
    
    e_solar_df = pd.DataFrame(columns = wavelengths)
    e_solar_df.loc[0, :] = smoothed_e_solar[wavelengths].values
    
    aod_data = None
    if cimel:
        aod_data = calc_cimel_band_aot_direct(ed, eds, sza, e_solar_df, data["sed"], aod_type)
    else:
        aod_data = calc_aot_direct(ed, eds, sza, e_solar_df, data["sed"], aod_type)
    
    return aod_data


def calculate_clearsky_wood(data, column="total_od", 
                            absolute_filter:float=2, 
                            relative_filter:float=0.05,
                            relative_time_period:str="10min"):
    """calculates which readings are cloudfree
    
    params:
        data: dataframe with at least columns 
            ["pc_time_end_measurement", "global_spectrum", "diffuse_spectrum", "sza", "sed"]
        column: which aod column to use, one of "total_od", "aod_microtops", "aod_wood_2017"
        absolute_filter: any readings higher than this will be filtered out
        relative_filter: any readings that are more than this value more or less than any
            other within the time window will be filtered out
        relative_time_period: the time period over which the relative filtering is done.
            this is the total time period that the filtering is done by, so if you want
            5 mins either side, pass 10min
            format is a string that will be passed to pd.Timedelta. documentation:
            https://pandas.pydata.org/docs/reference/api/pandas.Timedelta.html
    
    returns a numpy array the same length as input dataframe with ones and zeros, 1=clearsky 0=cloud
    """
    aod_data = calc_aod_from_df(data, aod_type=column, wavelengths=[500])
    nm500 = np.stack(aod_data[column].values)[:, 0]
    nm500df = pd.DataFrame(index=pd.DatetimeIndex(data["pc_time_end_measurement"]))
    nm500df["base"] = nm500
    nm500df["max"] = nm500df.rolling(pd.Timedelta(relative_time_period), center=True)["base"].max()-nm500df["base"]
    nm500df["min"] = nm500df.rolling(pd.Timedelta(relative_time_period), center=True)["base"].min()-nm500df["base"]
    nm500df["max"] = np.abs(nm500df["max"])
    nm500df["min"] = np.abs(nm500df["min"])
    nm500df["abs"] = np.logical_and(nm500df["max"] < relative_filter, nm500df["min"] < relative_filter)
    nm500df_abs = np.logical_and(nm500df["max"] < relative_filter, nm500df["min"] < relative_filter)
    
    clearsky_filter = np.logical_and(nm500df_abs.values, nm500 < absolute_filter)
    return clearsky_filter

# def calculate_clearsky_wood(data:pd.DataFrame, reading_index:int=200, 
#                             column="total_od",
#                             absolute_filter:float=2, relative_filter:float=0.05,
#                             relative_time_period:str="10min"):
#     """calculates which readings are cloudfree
    
#     params:
#         data: dataframe with at least columns ["total_od", "pc_time_end_measurement"]
#         reading_index: the wavelength that is used for the clearsky calculations
#             if on a full 300-1100nm spectra, make sure to subtract 300 from the wavelength you want to use
#         absolute_filter: any readings higher than this will be filtered out
#         relative_filter: any readings that are more than this value more or less than any
#             other within the time window will be filtered out
#         relative_time_period: the time period over which the relative filtering is done.
#             this is the total time period that the filtering is done by, so if you want
#             5 mins either side, pass 10min
#             format is a string that will be passed to pd.Timedelta. documentation:
#             https://pandas.pydata.org/docs/reference/api/pandas.Timedelta.html
    
#     returns a numpy array the same length as input dataframe with ones and zeros, 1=clearsky 0=cloud
#     """
#     nm500 = np.stack(data[column].values)[:, reading_index]
#     nm500df = pd.DataFrame(index=pd.DatetimeIndex(data["pc_time_end_measurement"]))
#     nm500df["base"] = nm500
#     nm500df["max"] = nm500df.rolling(pd.Timedelta(relative_time_period), center=True)["base"].max()-nm500df["base"]
#     nm500df["min"] = nm500df.rolling(pd.Timedelta(relative_time_period), center=True)["base"].min()-nm500df["base"]
#     nm500df["max"] = np.abs(nm500df["max"])
#     nm500df["min"] = np.abs(nm500df["min"])
#     nm500df["abs"] = np.logical_and(nm500df["max"] < relative_filter, nm500df["min"] < relative_filter)
#     nm500df_abs = np.logical_and(nm500df["max"] < relative_filter, nm500df["min"] < relative_filter)
    
#     clearsky_filter = np.logical_and(nm500df_abs.values, nm500 < absolute_filter)
#     return clearsky_filter

def calculate_clearsky_filter(data:pd.DataFrame, method:str="wood", kwargs:dict={}):
    """method that calls the appropriate clearsky function
    
    params:
        data: the data that is used for the clearsky calculation
        method: the method that iwll be used to calculate which readings are clearsky readings
        kwargs: the keyword arguments to pass to clearsky_filter
    """
    if method is None:
        return np.ones(len(data)).astype(bool)
    if method == "wood":
        return calculate_clearsky_wood(data, **kwargs)
    
    print("filtering method not recognised, not filtering")
    return np.ones(len(data)).astype(bool)


def AOT_plot(dfTau, title, limits=[0,1], Y_label='Optical thickness'):
    datestamp=dfTau.index[0].date() # date
    pl.figure(figsize=(18,14))

    pl.title(title + ':  {}'.format(datestamp.strftime('%Y-%m-%d')),size=18)

    pl.plot(dfTau.columns.astype(float), dfTau.values.T)
    pl.gca().xaxis.set_major_locator(pl.MultipleLocator(100) )
    #pl.gca().yaxis.set_major_locator(pl.MultipleLocator(0.1) )
    pl.tight_layout()
    pl.xlabel("Wavelength nm")
    pl.ylabel(Y_label)
    #pl.legend(loc = 'upper right')
    pl.ylim(limits)
    fig = pl.gcf()
    pl.show()
    return fig
    
def time_summary_plot(dfSummary, title, limits=[], Y_label='Irradiance W.m-2'):
    # inputs: dfSummary is a Pandas dataframe containing time v hsr summary values
    # title is some text to go in the title
    # Plot on a single Y-axis

    #  timestamp plot limits - strip out night values
    try:
        dfSummary = dfSummary[dfSummary['SZA'] < 90.0]
    except:
        print("No SZA - " + title)
        
    if len(dfSummary) == 0:
        return None
    timestamp = dfSummary.index   
    time_day_ar = np.array(timestamp) # convert to np array format

    datestamp=timestamp[0].date() # date
    pl.figure(figsize=(18,14))

    pl.title(title + ':  {}'.format(datestamp.strftime('%Y-%m-%d')),size=18)

    pl.plot(time_day_ar, dfSummary['Total W'], label = 'Global')
    pl.plot(time_day_ar, dfSummary['Diffuse W'], label = 'Diffuse')
    pl.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    pl.gca().yaxis.set_major_locator(pl.MultipleLocator(100) )
    pl.tight_layout()
    pl.ylabel(Y_label)
    pl.xlabel("UTC time [hrs]")
    pl.legend(loc = 'upper right')
    if len(limits):
        pl.ylim(limits)
    else:
        pl.ylim(bottom = 0)
    fig = pl.gcf()
    pl.show()
    return fig 

def time_general_plot(dfSummary, title, ColRange, limits=[], Y_label=''):
    # inputs: dfSummary is a Pandas dataframe containing time v hsr summary values
    # title is some text to go in the title
    # ColRange is the index range of columns to plot
    # Plot on a single Y-axis

    #  timestamp plot limits - strip out night values
    #  timestamp plot limits - strip out night values
    try:
        dfSummary = dfSummary[dfSummary['SZA'] < 90.0]
    except:
        print("No SZA - " + title)
        
    if len(dfSummary) == 0:
        return None

    timestamp = dfSummary.index   
    time_day_ar = np.array(timestamp) # convert to np array format

    datestamp=timestamp[0].date() # date
    pl.figure(figsize=(18,14))
    #fig, axes = pl.subplots(1,1, figsize = (18,14))
    #axes[0].set_prop_cycle('color', ['b','g','r','c','m','y','k'])
    pl.gca().set_prop_cycle(pl.cycler('color', ['b','g','r','c','m','y','k', 'tab:blue', 'tab:orange', 'tab:brown']))

    pl.title(title + ':  {}'.format(datestamp.strftime('%Y-%m-%d')),size=18)
    for idx in ColRange:
        pl.plot(time_day_ar, dfSummary.iloc[:,idx].values, label = dfSummary.columns[idx])
    
    pl.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    #pl.gca().yaxis.set_major_locator(pl.MultipleLocator(100) )
    pl.tight_layout()
    pl.ylabel(Y_label)
    pl.xlabel("UTC time [hrs]")
    pl.legend(loc = 'upper right')
    if len(limits):
        pl.ylim(limits)
    else:
        pl.ylim(bottom = 0)
    fig = pl.gcf()
    pl.show()
    return fig

def temp_RH_summary_plot(dfGPS, title ):   
    # inputs: dfGPS is a Pandas dataframe containing time v hsr GPS values
    # title is some text to go in the title

    timestamp = dfGPS.index   
    time_day_ar = np.array(timestamp) # convert to np array format

    datestamp=timestamp[0].date() # date
    #pl.figure(figsize=(18,14))

    fig, ax1 = pl.subplots(figsize=(18,14))
    fig.subplots_adjust(right=0.75)


    pl.title(title + ':  {}'.format(datestamp.strftime('%Y-%m-%d')),size=18)

    ax1.set_xlabel('UTC time [Hrs]')
    ax1.set_ylabel('Temp °C',color = 'r')
    ax1.tick_params(axis='y', labelcolor = 'r')
    P1 = ax1.plot(time_day_ar, dfGPS['RHTemp'],'r-', label = 'RH sensor temp')
    P2 = ax1.plot(time_day_ar, dfGPS['BaroTemp'],'r--', label = 'Baro sensor temp')

    ax2 = ax1.twinx()
    ax2.set_ylabel('RH %',color = 'b')
    ax2.tick_params(axis='y', labelcolor='b')
    P3 = ax2.plot(time_day_ar, dfGPS['RH'],'b-', label = 'RH %')
    ax2.set_ylim(bottom = 0)
    
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(("axes", 1.05))

    ax3.set_ylabel('Pressure hPa',color = 'g')
    ax3.tick_params(axis='y', labelcolor = 'g')
    P4 = ax3.plot(time_day_ar, dfGPS['Pressure'],'g-', label = 'Pressure')

    if (max(timestamp) - min(timestamp)).days > 2:
        pl.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    else:
        pl.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    #pl.gca().yaxis.set_major_locator(pl.MultipleLocator(100) )
    pl.tight_layout()
    #pl.ylabel("Temp °C")
    #pl.xlabel("UTC time [hrs]")
    #pl.legend(loc = 'upper right', handles = [P1, P2, P3, P4])
    fig.legend(loc = 'upper right')
    #pl.xlim(llim,ulim)
   # pl.ylim(bottom = 0)
    pl.show()
    return pl 

def correct_wavelength(dfE, hsr_series):
    # dfE is an uncorrected HSR spectrum dataframe. Apply corrections for HSR1-004
    wl = dfE.columns.astype(float)
    if hsr_series == 'HSR1-004':
        wl_corr = wl*0.995 + 9.7
    else:
        return dfE
    
    for i in range(len(dfE)):
        f_wl = interpolate.interp1d(wl_corr, dfE.iloc[i], bounds_error=False, fill_value=0)
        dfE.iloc[i] = f_wl(wl)
    return dfE
 
def Recalc_hsr_from_Raw(Raw, hsr_cal_path, hsr_cal_file, hsr_series):
    # Recalculate hsr final values from array of raw readings         
    
    # get calibration & calibrate raw values to W.m-2
    filename = os.path.join(hsr_cal_path, hsr_cal_file)
    with open(filename) as fp:
        Lines = fp.readlines(200)
        hsr_int = int(Lines[1].split("\t")[1])
        fp.close()
        
    try:    # try the quick read, works for uninterrupted files
        hsr_cal = pd.read_csv(filename, skiprows=4, delimiter='\t', index_col=1, header=None)
        hsr_cal = hsr_cal.drop(hsr_cal.columns[0], axis  = 1)
        hsr_cal.columns = np.arange(0,len(hsr_cal.columns))
    except:     # try a line-by-line read
        print ("Error reading calibration file  " + filename)
        
    dfLight = []
    m_IndCh = []
    if hsr_series == 'HSR1-003':
        hsr_int = 30
    elif hsr_series == 'HSR1-004':
        hsr_int = 20
        
    for ch in range(0, len(Raw)):
        if ch > 0:
            dfRaw = Raw[ch]-Raw[0]
            dfCal = hsr_cal[ch-1]
            dfLight_ch = dfRaw * dfCal / hsr_int    # Make sure this matches the integration time
        else:
            dfLight_ch = Raw[0]
        
        Ind_Ch = dfLight_ch[np.arange(400,901)].sum(axis = 1)
        m_IndCh.append(Ind_Ch)
        dfLight.append(dfLight_ch.copy())
        
    IndCh = pd.concat(m_IndCh, axis = 1)
        
    Max = IndCh.iloc[:,np.arange(1,len(IndCh.columns))].idxmax(axis = 1)
    Min = IndCh.iloc[:,np.arange(1,len(IndCh.columns))].idxmin(axis = 1)
    
    Ed = pd.DataFrame(columns = dfLight[0].columns, index = dfLight[0].index)
    Eds = pd.DataFrame(columns = dfLight[0].columns, index = dfLight[0].index)
    Summary = pd.DataFrame()
    for i in range(0, len(IndCh)):
        Ed.iloc[i,:] = dfLight[Max[i]].iloc[i,:] + dfLight[Min[i]].iloc[i,:]
        Eds.iloc[i,:] = dfLight[Min[i]].iloc[i,:] *2
    
    Summary['Total W'] = Ed[np.arange(400,901)].sum(axis = 1) 
    Summary['Diffuse W'] = Eds[np.arange(400,901)].sum(axis = 1) 
    
    Molar = Ed.columns * 0.00835935 #np.where((Ed.columns < 400) | (Ed.columns > 700), 0, Ed.columns * 0.00835935)
    Ed_mol = Ed * Molar
    Eds_mol = Eds * Molar
    Summary['Total Molar'] = Ed_mol[np.arange(400,700)].sum(axis = 1) # multiply by Quantum scaling
    Summary['Diffuse Molar'] = Eds_mol[np.arange(400,700)].sum(axis = 1) 
    
    # Now check for scale jumps if it's HSR1-003
    # Work on IndCh
    if hsr_series == 'HSR1-003':
        Scale = np.ones(len(IndCh))*0.298
        Mult = 0.298
        for i in range(0, len(IndCh)-1):
            if IndCh.iloc[i,1:7].max() > 136:
                Mult = 1
            elif IndCh.iloc[i,1:7].max() < 20:
                Mult = 0.298
            Scale[i] = Mult  
            
            if abs((IndCh.index[i+1]-IndCh.index[i]).seconds) < 80:
                Ratio = IndCh.iloc[i+1,1:7]/ IndCh.iloc[i,1:7]    
                if all(R > 1.8 for R in Ratio):
                    Mult = 0.298
                elif all(R < 0.6 for R in Ratio):
                    Mult = 1
        
        IndCh = IndCh.mul( Scale, axis = 0)
        Summary = Summary.mul( Scale, axis = 0)
        Ed = Ed.mul( Scale, axis = 0)
        Eds = Eds.mul( Scale, axis = 0)
            
            
    # - reduce to 1-min averages
    Ed_1m = Ed.astype(float).resample('1T',label = 'right', closed = 'right').mean().dropna(how='all')
    Eds_1m = Eds.astype(float).resample('1T',label = 'right', closed = 'right').mean().dropna(how='all')
    Summary_1m = Summary.astype(float).resample('1T',label = 'right', closed = 'right').mean().dropna(how='all')
    #IndCh.columns = ['Ch' + str(i) for i in IndCh.columns]
    IndCh.columns = [ str(i) for i in IndCh.columns]

#    for idx, row in Summary_1m.iterrows():
#        Summary_1m.at[idx,'SZA'] = calc_sun_zenith(idx, lat, lon)
    return Ed_1m, Eds_1m, Summary_1m, IndCh         

def CalibratehsrRaw(Raw, hsr_cal_path, hsr_cal_file):
    # get calibration & calibrate raw values to W.m-2
    filename = os.path.join(hsr_cal_path, hsr_cal_file)
    try:    # try the quick read, works for uninterrupted files
        with open(filename) as f:
            print(f.readline())
            items = f.readline().split()
            if items[0] == 'IntegrationTime':       # read integration time
                hsr_int = int(items[1])
                
        hsr_cal = pd.read_csv(filename, skiprows=4, delimiter='\t', index_col=1, header=None)
        hsr_cal = hsr_cal.drop(hsr_cal.columns[0], axis  = 1)
        hsr_cal.columns = np.arange(0,len(hsr_cal.columns))
    except:     # try a line-by-line read
        print ("Error reading calibration file  " + filename)
        
    
    m_Light = []
    m_IndCh = []
        
    for ch in range(0, len(Raw)):
        if ch > 0:
            m_Raw = Raw[ch]-Raw[0]
            m_Cal = hsr_cal[ch-1]
            m_Light_ch = m_Raw * m_Cal / hsr_int    # Make sure this matches the integration time
        else:
            m_Light_ch = Raw[0]
        
        Ind_Ch = m_Light_ch[np.arange(400,901)].sum(axis = 1)
        m_IndCh.append(Ind_Ch)
        m_Light.append(m_Light_ch.copy())

    IndCh = pd.concat(m_IndCh, axis = 1)
    return m_Light, IndCh

def SPN1_DomeLensing(TPIndex, vZen, vAz, Rotation):
    # SPN1_DOMELENSING returns a float giving the additional sensitivity
    # due to dome lensing
    # TPIndex is an integer between 1 and 7, matching the SPN1 Thermopile number
    # Az & Zen are solar position, in degrees
    # Rotation is the SPN1 orientation relative to North, in degrees
    # return value is normalised to the horizontal incoming beam, so corrected measurement
    # DNImeas = DNI * (Cos(zen) + DomeLensing)
    # If inputs are arrays, then must all be the same size

    TP1Err = vZen  ** 3 * np.cos(np.radians(vZen)) / -30000000.0
    if TPIndex == 1:
        r = TP1Err
    elif TPIndex > 1 and TPIndex <= 7:
        A = ((TPIndex-2) * -60) 
        r = 0.012 * np.sin(np.radians(2 * vZen)) * np.cos(np.radians(A - vAz + Rotation)) + TP1Err
    
    Idx = (vZen > 90) | (vZen < 0)     # check for out of range zenith angles
    r[Idx] = 0
    
    return r

def SPN1_FTAngle(vZen, vAz, Rotation):
    #SPN1_FTAngle returns a matrix giving the 7 Thermopile First Touch angle values, 7
    #columns for the 7 thermopiles, rows to match input vectors.
    #FTAngle values in degrees
    #Az & Zen are solar position, in degrees
    #Rotation is the SPN1 orientation relative to North, in degrees
    
    # Load the image file, find the right coordinates on the image
    FTSign = pl.imread( 'D:\DOCUMENT\MATLAB\SPN1_Correction\Data\SPN1 TPValue\FTSign.BMP')
    Sgn1 = FTSign[:,:,0]/64 - 1        # split the three colour planes
    Sgn2 = FTSign[:,:,1]/64 - 1
    Sgn3 = FTSign[:,:,2]/64 - 1
    TPCombined = pl.imread( 'D:\DOCUMENT\MATLAB\SPN1_Correction\Data\SPN1 TPValue\FTAngle.BMP')
    TP1 = TPCombined[:,:,0].astype(np.float) * Sgn1       # split the three colour planes
    TP2 = TPCombined[:,:,1].astype(np.float) * Sgn2
    TP3 = TPCombined[:,:,2].astype(np.float) * Sgn3
    # Sgn1[Sgn1==0]=-1
    # Sgn2[Sgn2==0]=-1
    # Sgn3[Sgn3==0]=-1
    [R, C] = AZtoRC(vAz - Rotation, vZen)
    
    # figure
    # image(TPCombined); hold on
    # plot(X,Y)
    # ylim([0 1000 ]); xlim([0 1000 ])
    
    #linearInd = sub2ind(np.shape(TP1),R,C)
    
    mFTAngle = np.zeros([len(vZen),8])
    mFTAngle[:,1] = TP1[R,C]          # First three image planes are direct
    mFTAngle[:,2] = TP2[R,C]
    mFTAngle[:,3] = TP3[R,C]
    #linearInd = sub2ind(np.shape(TP1),R,1000-C)    # the rest use symmetries
    mFTAngle[:,4] = TP3[R,1000-C]
    mFTAngle[:,5] = TP2[R,1000-C]
    #linearInd = sub2ind(np.shape(TP1),1000-R,1000-C)
    mFTAngle[:,6] = TP3[1000-R, 1000-C]
    #linearInd = sub2ind(np.shape(TP1),1000-R,C)
    mFTAngle[:,7] = TP3[1000-R,C]
    
    mFTAngle[:,:] = mFTAngle[:,:] / 10;        # scale to degrees


    return mFTAngle

def SPN1_TPValue(vZen, vAz, Rotation):
    #SPN1_TPValue returns a matrix giving the 7 Thermopile exposure values, 7
    #columns for the 7 thermopiles, rows to match input vectors.
    #Exposure values in range 0 - 1 for fraction of solar disk exposure
    #Az & Zen are solar position, in degrees
    #Rotation is the SPN1 orientation relative to North, in degrees
    
    # Load the image file, find the right coordinates on the image
    TPCombined = pl.imread( 'D:\DOCUMENT\MATLAB\SPN1_Correction\Data\SPN1 TPValue\TPValue.BMP')
    #TPCombined = imread( 'Data\SPN1 TPValue\TPValue.BMP');
    TP1 = TPCombined[:,:,1]        # split the three colour planes
    TP2 = TPCombined[:,:,2]
    TP3 = TPCombined[:,:,3]
    [R, C] = AZtoRC(vAz - Rotation, vZen)
    
    # figure;
    # image(TPCombined); hold on;
    # plot(X,Y);
    # ylim([0 1000 ]); xlim([0 1000 ]);
    
    linearInd = sub2ind(np.shape(TP1),len(R),len(C))
    
    mTPValue = np.zeros(np.size(vZen,1),7)
    mTPValue[:,1] = TP1(linearInd)          # First three image planes are direct
    mTPValue[:,2] = TP2(linearInd)
    mTPValue[:,3] = TP3(linearInd)
    linearInd = sub2ind(np.size(TP1),R,1000-C)    # the rest use symmetries
    mTPValue[:,4] = TP3(linearInd)
    mTPValue[:,5] = TP2(linearInd)
    linearInd = sub2ind(np.size(TP1),1000-R,1000-C)
    mTPValue[:,6] = TP3(linearInd)
    linearInd = sub2ind(np.size(TP1),1000-R,C)
    mTPValue[:,7] = TP3(linearInd)
    
    mTPValue[:,:] = mTPValue[:,:] / 255        # scale to range 0 - 1 
    return mTPValue
           
def AZtoRC(vAzimuth, vZenith):
    # Converts Azimuth & Zenith angles to R,C position on bitmap array
    # watch out - matrix Row, Col are the opposite way round to X, Y on the image
    # vAzimuth & vZenith come in degrees
    vZenith[vZenith>90]=91     #force zenith in range <90
    BMPRadius = 450
    Centre = 500           # Size information for the image
    vC = np.floor(BMPRadius * vZenith / 90 * np.cos(np.radians(vAzimuth)) + Centre + 0.5)      #X
    vR = np.floor(BMPRadius * vZenith / 90 * np.sin(np.radians(vAzimuth)) + Centre + 0.5)      #Y
    return vR.astype(int), vC.astype(int)

def sub2ind(array_shape, rows, cols):
    return rows*array_shape[1] + cols
            
def Save_hsr_Files(hsr_path, hsr_date, Savepath, fname, headerlines, df):
    # hsr_path is original file folder root, hsr_date is the daily folder or zip, Savepath is the new folder root
    # fname is the filename without extension, headerlines the number to copy in from original file, df the dataframe to save after the headerlines
    
    filepath = os.path.join(Savepath, hsr_date)
    os.makedirs(filepath, exist_ok=True)  

    originalfilename = os.path.join(hsr_path, hsr_date + '.zip')
    lines = []
    # get start of original file
    if os.path.isfile(originalfilename):    # for data in zipfiles
        try:    # try the quick read, works for uninterrupted files
            archive = zipfile.ZipFile(originalfilename, 'r')
            ### Import hsr file from daily folder
            f = archive.open(fname + '.txt')
            lines = f.readlines()        
        except:     # try a line-by-line read
            print ("Error reading zip: " + originalfilename)

    elif os.path.isdir(os.path.join(hsr_path, hsr_date)):     # for data expanded into dated folders
        originalfilename = os.path.join(hsr_path, hsr_date, fname + '.txt')
        try:    # try the quick read, works for uninterrupted files
            f = open(originalfilename,'r')
            lines = f.readlines()
        except:     # try a line-by-line read
            print ("Error reading, : " + originalfilename)
           

    filename = os.path.join(filepath, fname + '.txt')
    if len(lines):
        with  open(filename, 'wb') as newfile:
            newfile.writelines(lines[0:headerlines])
    else:
        with  open(filename, 'w') as newfile:
            newfile.write('Spectrometer Data file\n')
            newfile.write(fname + '\t' + hsr_date + '\n')
        
    df.to_csv(filename, mode='a', index_label='Time', sep='\t')  
    return

def Get_hsr_Dates(hsr_path, start_date, end_date):
# Get a list of hsr datafiles in the root folder

    folderlist = None
    if hsr_path == "":
        folderlist = os.listdir()
    else:
        folderlist = os.listdir(hsr_path)
    
    datelist = []
    for i, name in enumerate(folderlist):
        try:
            res = bool(dt.datetime.strptime(name[:10], '%Y-%m-%d'))
            datelist.append(name[:10])
        except ValueError:
            res = False
            
    date_dict = dict.fromkeys(datelist, True)     # removes any duplicate dates
    try: 
        # check dates are in range
            for i, name in enumerate(date_dict):
                if len(start_date):
                    if dt.datetime.strptime(name, '%Y-%m-%d') < dt.datetime.strptime(start_date[:10], '%Y-%m-%d'):   
                        date_dict[name] = False
                if len(end_date):
                    if dt.datetime.strptime(name, '%Y-%m-%d') > dt.datetime.strptime(end_date[:10], '%Y-%m-%d'):   
                        date_dict[name] = False
               
    except:
        print('Error checking dates')
        print("start_date: "+str(start_date))
        print("end_date: "+str(end_date))
    
    #print (date_dict)
    hsr_dates  = [k for k, v in date_dict.items() if v == True]
    return hsr_dates



