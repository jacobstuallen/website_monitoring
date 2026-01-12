# Jacob Stuivenvolt-Allen
# For Swift Climate and Weather
# 01/26/2024
# -----------

# Purpose: 
# -----------
# This script reads native grib files 
# from CFS pgrbanl.grib2 files into 
# netcdf for easy plotting. 
# -----------

# List of variables
# -----------------
# temp, U500, V500, psi500, hgt500, mslp
# qTOT, 

import os
import numpy as np
import re
import sys
import xarray as xr
import matplotlib.pyplot as plt
from datetime import date
from datetime import timedelta

# Grab current date
# -----------------
if(len(sys.argv) == 2):
    date = sys.argv[1]
    x = re.search("\d{8}",date)
    while not x:
        print("please type a valid date YYYYDDMM")
        date = input()
        x = re.search("\d{8}",date)
else:
    date = date.today()
    yda = str(date - timedelta(days=1)).replace('-','')
    sst_day = str(date - timedelta(days=2)).replace('-','')
    date = str(date).replace('-','')
    # also need yesterday to clean data

YYYYMMDD = date
YYYYMM = date[:-2]
YYYY = date[:-4]

#hours = ['00','06','12','18']

proj_dir = '/glade/u/home/jsallen/projects/swift/'
data_dir = '/glade/u/home/jsallen/projects/swift/data/'+ date

# Open datasets with backend_kwargs to handle multiple levels
# Different typeOfLevel values need to be opened separately
ds_isobaric = xr.open_mfdataset('../data/'+YYYYMMDD+'/cdas1.t*z.pgrbanl.grib2', 
                                 engine='cfgrib',
                                 backend_kwargs={'filter_by_keys': {'typeOfLevel': 'isobaricInhPa'}},
                                 concat_dim='time', 
                                 combine='nested')

ds_surface = xr.open_mfdataset('../data/'+YYYYMMDD+'/cdas1.t*z.pgrbanl.grib2', 
                                engine='cfgrib',
                                backend_kwargs={'filter_by_keys': {'typeOfLevel': 'surface'}},
                                concat_dim='time', 
                                combine='nested')

ds_heightAboveGround = xr.open_mfdataset('../data/'+YYYYMMDD+'/cdas1.t*z.pgrbanl.grib2', 
                                          engine='cfgrib',
                                          backend_kwargs={'filter_by_keys': {'typeOfLevel': 'heightAboveGround'}},
                                          concat_dim='time', 
                                          combine='nested')

# Print available variables to see what cfgrib has named them
print("Isobaric variables:", list(ds_isobaric.data_vars))
print("Surface variables:", list(ds_surface.data_vars))
print("Height above ground variables:", list(ds_heightAboveGround.data_vars))

# Extract variables using CF-compliant names
# cfgrib translates GRIB parameter names to standard names:
# UGRD -> u (eastward wind)
# VGRD -> v (northward wind)  
# HGT -> gh (geopotential height)
# TMP -> t (temperature)
# PRMSL -> msl (mean sea level pressure)
# DPT -> d (dewpoint)

uwnd = ds_isobaric['u'].sel(isobaricInhPa=500).mean(dim='time')
vwnd = ds_isobaric['v'].sel(isobaricInhPa=500).mean(dim='time')
hgt  = ds_isobaric['gh'].sel(isobaricInhPa=500).mean(dim='time')

# Temperature at 2m height above ground (not isobaric level)
temp = ds_heightAboveGround['t2m'].mean(dim='time')  # or just 't' depending on what's available

# Mean sea level pressure
mslp = ds_surface['msl'].mean(dim='time')

# Dewpoint at 2m
dewt = ds_heightAboveGround['d2m'].mean(dim='time')  # or 'd' depending on what's available

# If you need streamfunction, check if it's available
if 'strm' in ds_isobaric:
    strf = ds_isobaric['strm']


exit()

"""
#cdas1.t00z.ocngrbl01.grib2
ds1 = xr.open_mfdataset('../data/'+YYYYMMDD+'/cdas1.t*z.pgrbanl.grib2', engine='cfgrib', 
                       filter_by_keys={'typeOfLevel': 'isobaricInhPa'}, 
                       concat_dim='time', combine='nested')

var = ds.variables

ds = xr.open_mfdataset('../data/'+YYYYMMDD+'/cdas1.t*z.pgrbanl.grib2', engine='cfgrib',
                       concat_dim='time', combine='nested')

uwnd = ds['UGRD_P0_L100_GLL0'].sel(lv_ISBL0=50000).mean(dim='time')
vwnd = ds['VGRD_P0_L100_GLL0'].sel(lv_ISBL0=50000).mean(dim='time')
hgt  = ds['HGT_P0_L100_GLL0'].sel(lv_ISBL0=50000).mean(dim='time')

temp = ds['TMP_P0_L104_GLL0'].mean(dim='time')
strf = ds['STRM_P0_L100_GLL0']
mslp = ds['PRMSL_P0_L101_GLL0'].mean(dim='time')
dewt = ds['DPT_P0_2L108_GLL0'].mean(dim='time')
"""

exit()

# IVT CALCULATION
# ---------------
q  = ds['SPFH_P0_L100_GLL0']

qq = q.sel(lv_ISBL0=slice(300*100,1000*100))
p = q.sel(lv_ISBL0=slice(250*100,1000*100))['lv_ISBL0']

qu  = ds['UGRD_P0_L100_GLL0'].sel(lv_ISBL0=slice(300*100,1000*100)) * qq 
qv  = ds['VGRD_P0_L100_GLL0'].sel(lv_ISBL0=slice(300*100,1000*100)) * qq 

qu_int = qu.integrate(coord='lv_ISBL0')
qv_int = qv.integrate(coord='lv_ISBL0')

g = 1/9.807
ivt = np.sqrt ( (g*qu_int)**2 + (g*qv_int)**2 ).mean(dim='time')
# ---------------

# Add other calculations : WAF/(?)

# OUTPUT NETCDF
ivt.to_netcdf(data_dir+'/ivt.cfs.nc')     # integrated vapor transport
uwnd.to_netcdf(data_dir+'/u500.cfs.nc')   # u500
vwnd.to_netcdf(data_dir+'/v500.cfs.nc')   # v500
hgt.to_netcdf(data_dir+'/z500.cfs.nc')    # z500
mslp.to_netcdf(data_dir+'/mslp.cfs.nc')   # mslp
temp.to_netcdf(data_dir+'/temp.cfs.nc')   # temp
dewt.to_netcdf(data_dir+'/dewt.cfs.nc')   # dewt

# end
