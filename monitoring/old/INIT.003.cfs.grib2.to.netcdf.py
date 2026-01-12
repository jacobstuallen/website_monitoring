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

proj_dir = '/home/js4562/project/swift/'
data_dir = '/home/js4562/project/swift/data/'+date

# Just need to point to day relevant path
ds = xr.open_mfdataset('../data/'+YYYYMMDD+'/cdas1.t*z.ocngrbl01.grib2', engine='pynio',
        concat_dim='time', combine='nested')

var = ds.variables

# 01 variables of interest
ohc = ds['OHC_P8_2L236_GLL0_avg'].mean(dim='time')
sal = ds['SALTY_P8_L160_GLL0_avg'].mean(dim='time')
tauu = ds['UFLX_P8_L1_GLL0_avg'].mean(dim='time')
tauv = ds['VFLX_P8_L1_GLL0_avg'].mean(dim='time')
cover = ds['ICEC_P8_L1_GLL0_avg'].mean(dim='time')
thick = ds['ICETK_P8_L1_GLL0_avg'].mean(dim='time')

# OUTPUT NETCDF
ohc.to_netcdf(data_dir+'/ohc.cfs.nc')
sal.to_netcdf(data_dir+'/sal.cfs.nc')
tauu.to_netcdf(data_dir+'/tauu.cfs.nc')
tauv.to_netcdf(data_dir+'/tauv.cfs.nc')
cover.to_netcdf(data_dir+'/ice-cover.cfs.nc')
thick.to_netcdf(data_dir+'/ice-thick.cfs.nc')

# OUTPUT NETCDF
