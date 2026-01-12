# Jacob Stuivenvolt-Allen
# For Swift Climate and Weather
# 01/26/2024
# -----------

# Purpose: 
# -----------
# This script reads native grib files 
# from CFS pgrbf01.grib2 files into 
# netcdf for easy plotting. 
# -----------

import os
import numpy as np
import re
import sys
import xarray as xr
import matplotlib.pyplot as plt
from datetime import date
from datetime import timedelta
from glob import glob

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

YYYYMMDD = date
YYYYMM = date[:-2]
YYYY = date[:-4]

proj_dir = '/glade/u/home/jsallen/projects/swift/'
data_dir = '/glade/u/home/jsallen/projects/swift/data/'+ date

file_pattern = '../data/'+YYYYMMDD+'/cdas1.t*z.pgrbf01.grib2'

print("Loading forecast variables...")

# Precipitation rate (Dataset 36)
ds_prect = xr.open_mfdataset(file_pattern, engine='cfgrib',
                             backend_kwargs={'filter_by_keys': {'shortName': 'prate'},
                                            'decode_timedelta': False},
                             concat_dim='time', combine='nested')
prect = ds_prect['prate'].sum(dim='time')
print("✓ Loaded precipitation rate")

# 2-meter relative humidity (Dataset 8)
# The shortName is '2r' but the variable name in xarray will be 'r2'
ds_rhum = xr.open_mfdataset(file_pattern, engine='cfgrib',
                            backend_kwargs={'filter_by_keys': {'shortName': '2r'},
                                           'decode_timedelta': False},
                            concat_dim='time', combine='nested')
rhum = ds_rhum['r2'].mean(dim='time')
print("✓ Loaded 2-meter relative humidity")

# OUTPUT NETCDF
print("\nWriting NetCDF files...")
prect.to_netcdf(data_dir+'/prec.cfs.nc')
print("Wrote prec.cfs.nc")
rhum.to_netcdf(data_dir+'/rhum.cfs.nc')
print("Wrote rhum.cfs.nc")

print("\nDone!")
