# Jacob Stuivenvolt-Allen
# Ocean variables from CFS
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

#proj_dir = '/home/js4562/project/swift/'
#data_dir = '/home/js4562/project/swift/data/'+date

proj_dir = '/glade/u/home/jsallen/projects/swift/'
data_dir = '/glade/u/home/jsallen/projects/swift/data/'+ date

file_pattern = '../data/'+YYYYMMDD+'/cdas1.t*z.ocngrbl01.grib2'

print("Loading ocean variables...")

# Ocean heat content (Dataset 4)
ds_ohc = xr.open_mfdataset(file_pattern, engine='cfgrib',
                           backend_kwargs={'filter_by_keys': {'shortName': 'ohc'},
                                          'decode_timedelta': False},
                           concat_dim='time', combine='nested')
ohc = ds_ohc['ohc'].mean(dim='time')
print("✓ Loaded ocean heat content")

# Salinity (Dataset 0)
ds_sal = xr.open_mfdataset(file_pattern, engine='cfgrib',
                           backend_kwargs={'filter_by_keys': {'shortName': 's'},
                                          'decode_timedelta': False},
                           concat_dim='time', combine='nested')
sal = ds_sal['s'].mean(dim='time')
print("✓ Loaded salinity")

# U-component of atmospheric surface momentum flux (Dataset 2)
ds_tauu = xr.open_mfdataset(file_pattern, engine='cfgrib',
                            backend_kwargs={'filter_by_keys': {'shortName': 'avg_utaua'},
                                           'decode_timedelta': False},
                            concat_dim='time', combine='nested')
tauu = ds_tauu['avg_utaua'].mean(dim='time')
print("✓ Loaded u momentum flux")

# V-component of atmospheric surface momentum flux (Dataset 2)
ds_tauv = xr.open_mfdataset(file_pattern, engine='cfgrib',
                            backend_kwargs={'filter_by_keys': {'shortName': 'avg_vtaua'},
                                           'decode_timedelta': False},
                            concat_dim='time', combine='nested')
tauv = ds_tauv['avg_vtaua'].mean(dim='time')
print("✓ Loaded v momentum flux")

# Sea ice area fraction (Dataset 2)
ds_cover = xr.open_mfdataset(file_pattern, engine='cfgrib',
                             backend_kwargs={'filter_by_keys': {'shortName': 'avg_ci'},
                                            'decode_timedelta': False},
                             concat_dim='time', combine='nested')
cover = ds_cover['avg_ci'].mean(dim='time')
print("✓ Loaded ice cover")

# Sea ice thickness (Dataset 2)
ds_thick = xr.open_mfdataset(file_pattern, engine='cfgrib',
                             backend_kwargs={'filter_by_keys': {'shortName': 'avg_sithick'},
                                            'decode_timedelta': False},
                             concat_dim='time', combine='nested')
thick = ds_thick['avg_sithick'].mean(dim='time')
print("✓ Loaded ice thickness")

# OUTPUT NETCDF
print("\nWriting NetCDF files...")
ohc.to_netcdf(data_dir+'/ohc.cfs.nc')
sal.to_netcdf(data_dir+'/sal.cfs.nc')
tauu.to_netcdf(data_dir+'/tauu.cfs.nc')
tauv.to_netcdf(data_dir+'/tauv.cfs.nc')
cover.to_netcdf(data_dir+'/ice-cover.cfs.nc')
thick.to_netcdf(data_dir+'/ice-thick.cfs.nc')

print("✓ Wrote all NetCDF files")
print("\nDone!")
