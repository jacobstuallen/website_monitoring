# Jacob Stuivenvolt-Allen
# For Swift Climate and Weather
# 01/26/2024
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

file_pattern = '../data/'+YYYYMMDD+'/cdas1.t*z.pgrbanl.grib2'

# Open specific variables - specify BOTH shortName AND typeOfLevel

print("Loading wind components...")
ds_u = xr.open_mfdataset(file_pattern, engine='cfgrib',
                         backend_kwargs={'filter_by_keys': 
                                         {'shortName': 'u', 'typeOfLevel': 'isobaricInhPa'},
                                        'decode_timedelta': False},
                         concat_dim='time', combine='nested')

ds_v = xr.open_mfdataset(file_pattern, engine='cfgrib',
                         backend_kwargs={'filter_by_keys': 
                                         {'shortName': 'v', 'typeOfLevel': 'isobaricInhPa'},
                                        'decode_timedelta': False},
                         concat_dim='time', combine='nested')

print("Loading geopotential height...")
ds_gh = xr.open_mfdataset(file_pattern, engine='cfgrib',
                          backend_kwargs={'filter_by_keys': 
                                          {'shortName': 'gh', 'typeOfLevel': 'isobaricInhPa'},
                                         'decode_timedelta': False},
                          concat_dim='time', combine='nested')

print("Loading streamfunction...")
ds_strf = xr.open_mfdataset(file_pattern, engine='cfgrib',
                            backend_kwargs={'filter_by_keys': 
                                            {'shortName': 'strf', 'typeOfLevel': 'isobaricInhPa'},
                                           'decode_timedelta': False},
                            concat_dim='time', combine='nested')

print("Loading temperature...")
ds_t = xr.open_mfdataset(file_pattern, engine='cfgrib',
                         backend_kwargs={'filter_by_keys': 
                                         {'shortName': 't', 'typeOfLevel': 'isobaricInhPa'},
                                        'decode_timedelta': False},
                         concat_dim='time', combine='nested')

print("Loading surface pressure...")
ds_sp = xr.open_mfdataset(file_pattern, engine='cfgrib',
                          backend_kwargs={'filter_by_keys': 
                                          {'shortName': 'sp', 'typeOfLevel': 'surface'},
                                         'decode_timedelta': False},
                          concat_dim='time', combine='nested')


# Extract 500 hPa level and compute time means
print("Extracting variables at 500 hPa...")
uwnd = ds_u['u'].sel(isobaricInhPa=500).mean(dim='time')
vwnd = ds_v['v'].sel(isobaricInhPa=500).mean(dim='time')
hgt  = ds_gh['gh'].sel(isobaricInhPa=500).mean(dim='time')
strf = ds_strf['strf'].sel(isobaricInhPa=500).mean(dim='time')
temp = ds_t['t'].sel(isobaricInhPa=500).mean(dim='time')  # 500 hPa temperature

mslp = ds_sp['sp'].mean(dim='time')

print("\nDone! Variables extracted:")
print(f"  uwnd: {uwnd.shape}")
print(f"  vwnd: {vwnd.shape}")
print(f"  hgt: {hgt.shape}")
print(f"  strf: {strf.shape}")
print(f"  temp: {temp.shape}")
print(f"  mslp: {mslp.shape}")


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

# IVT CALCULATION
# ---------------
print("Loading specific humidity for IVT calculation...")
ds_q = xr.open_mfdataset(file_pattern, engine='cfgrib',
                         backend_kwargs={'filter_by_keys': {'shortName': 'q', 'typeOfLevel': 'isobaricInhPa'},
                                        'decode_timedelta': False},
                         concat_dim='time', combine='nested')

# Select pressure levels from 300 to 1000 hPa
# Note: cfgrib uses hPa directly, not Pa like the old code (no *100)
qq = ds_q['q'].sel(isobaricInhPa=slice(1000, 300))  # slice goes high to low in hPa

# Get pressure coordinate in Pa for integration
p = qq['isobaricInhPa'] * 100  # Convert hPa to Pa

# Multiply specific humidity by wind components (already loaded as ds_u, ds_v)
# Select same pressure range
qu = ds_u['u'].sel(isobaricInhPa=slice(1000, 300)) * qq
qv = ds_v['v'].sel(isobaricInhPa=slice(1000, 300)) * qq

# Integrate over pressure (in Pa)
# Need to convert coordinate to Pa for proper integration
qu_int = qu.integrate(coord='isobaricInhPa') * 100  # *100 to convert hPa to Pa in integration
qv_int = qv.integrate(coord='isobaricInhPa') * 100

# Calculate IVT
g = 1/9.807
ivt = np.sqrt((g*qu_int)**2 + (g*qv_int)**2).mean(dim='time')

print(f"  IVT: {ivt.shape}")

# ---------------

# Add other calculations : WAF/(?)

# OUTPUT NETCDF
ivt.to_netcdf(data_dir+'/ivt.cfs.nc')     # integrated vapor transport
uwnd.to_netcdf(data_dir+'/u500.cfs.nc')   # u500
vwnd.to_netcdf(data_dir+'/v500.cfs.nc')   # v500
hgt.to_netcdf(data_dir+'/z500.cfs.nc')    # z500
mslp.to_netcdf(data_dir+'/mslp.cfs.nc')   # mslp
temp.to_netcdf(data_dir+'/temp.cfs.nc')   # temp
#dewt.to_netcdf(data_dir+'/dewt.cfs.nc')   # dewt

# end
