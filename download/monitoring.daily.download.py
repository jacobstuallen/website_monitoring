# Jacob Stuivenvolt-Allen
# Swift Climate and Weather
# 01/06/2024

# Purpose:
# -----------
# This script downloads daily data
# used on the monitoring page
# -----------

# List of datas sources
# ---------------------

# ---------------------
from datetime import date
from datetime import timedelta
import os
import numpy as np
import re
import sys
import xarray as xr

# DOWNLOAD OPTIONS
# ----------------
do_sst_download = True 
do_cfs_download = True
do_enso_index_download = True

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

# sst days
sst_YYYYMMDD = sst_day
sst_YYYYMM   = sst_day[:-2]
sst_YYYY     = sst_day[:-4]

# cfs days
cfs_YYYYMMDD = yda
cfs_YYYYMM   = yda[:-2]
cfs_YYYY     = yda[:-4]

# Make directory for current day
# ------------------------------
#data_path = '/home/js4562/project/swift/data/'+date+'/'
data_path = '/glade/work/jsallen/projects/swift/data/'+date+'/'
dir_cmd = 'mkdir -p '+data_path
os.system(dir_cmd)


# SST ~ DAILY: OISSTv2 - 2 day lag
# --------------------------------
sst_http = 'https://downloads.psl.noaa.gov/Datasets/noaa.oisst.v2.highres/'
def sst_download():

    if do_sst_download == True:
        sst_file  = sst_http+'sst.day.mean.'+sst_YYYY+'.nc'
        ssta_file = sst_http+'sst.day.anom.'+sst_YYYY+'.nc'
        sst_wget = 'wget -nc '+sst_file+ ' -O '+ data_path + 'sst.day.mean.'+sst_YYYY+'.nc'
        ssta_wget = 'wget -nc '+ssta_file+ ' -O '+ data_path + 'sst.day.anom.'+sst_YYYY+'.nc'

        os.system(sst_wget)
        os.system(ssta_wget)

        # slice last day from SST
        ds1 = xr.open_dataset(
            data_path + 'sst.day.mean.'+sst_YYYY+'.nc',
            ).isel(time=-1).to_netcdf(
                    data_path+'sst.recent.day.mean.nc')

        ds2 = xr.open_dataset(
            data_path + 'sst.day.anom.'+sst_YYYY+'.nc',
            ).isel(time=-1).to_netcdf(
                data_path+'sst.recent.day.anom.nc')

        return( print('OISST DOWNLOADED --------------- '))

# GLOBAL TEMP ANOM
# ----------------
tanom_file = 'https://downloads.psl.noaa.gov/Datasets/ghcncams/air.mon.mean.nc'

# GDEX PATH 
# ---------
gdex = f'https://osdf-director.osg-htc.org/ncar/gdex/d094000/{cfs_YYYY}/'

# CFS : pgrbanl and ocngrbl
# -------------------------
atm_1_http = f'{gdex}cdas1.'+cfs_YYYYMMDD+'.pgrbanl.tar'
atm_2_http = f'{gdex}cdas1.'+cfs_YYYYMMDD+'.pgrbf.tar'
ocn_http   = f'{gdex}cdas1.'+cfs_YYYYMMDD+'.ocngrbl.tar'
#atm_1_http = 'https://data.rda.ucar.edu/ds094.0/'+cfs_YYYY+'/cdas1.'+cfs_YYYYMMDD+'.pgrbanl.tar'
#atm_2_http = 'https://data.rda.ucar.edu/ds094.0/'+cfs_YYYY+'/cdas1.'+cfs_YYYYMMDD+'.pgrbf.tar'
#ocn_http   = 'https://data.rda.ucar.edu/ds094.0/'+cfs_YYYY+'/cdas1.'+cfs_YYYYMMDD+'.ocngrbl.tar'

def cfs_download():

    if do_cfs_download == True:

        atm_1_wget = 'wget -nc '+atm_1_http+ ' -P '+ data_path
        atm_2_wget = 'wget -nc '+atm_2_http+ ' -P '+ data_path
        ocn_wget = 'wget -nc '+ocn_http+ ' -P '+ data_path 

        os.system(atm_1_wget)
        os.system(atm_2_wget)
        os.system(ocn_wget)

        os.system('tar -xvf '+data_path+'cdas1.'+cfs_YYYYMMDD+'.pgrbanl.tar -C '+data_path)
        os.system('tar -xvf '+data_path+'cdas1.'+cfs_YYYYMMDD+'.pgrbf.tar -C '+data_path)
        os.system('tar -xvf '+data_path+'cdas1.'+cfs_YYYYMMDD+'.ocngrbl.tar -C '+data_path)

    return( print('CFS DOWNLOADED --------------- '))


# ENSO MONITORING AND INDICES
# ---------------------------

def enso_index_download():
    if do_enso_index_download == True:

        # ENSO INDEX
        # ----------
        index_http = 'https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.91-20.ascii'
        index_wget = 'wget -nc '+index_http+' -O '+data_path+ 'ersst.nino.mon.txt'
        os.system(index_wget)

        # DAILY SST FROM LAST THREE YEARS
        # -------------------------------
        y4 = int(YYYY)
        y3 = y4 - 1
        y2 = y4 - 2
        y1 = y4 - 3
        years = [y1,y2,y3,y4]

        sst_http = 'https://downloads.psl.noaa.gov/Datasets/noaa.oisst.v2.highres/'
        for year in years:
            sst_file  = sst_http+'sst.day.mean.'+str(year)+'.nc'
            ssta_file = sst_http+'sst.day.anom.'+str(year)+'.nc'
            sst_wget = 'wget -nc '+sst_file+ ' -O '+ data_path + 'sst.day.mean.'+str(year)+'.nc'
            ssta_wget = 'wget -nc '+ssta_file+ ' -O '+ data_path + 'sst.day.anom.'+str(year)+'.nc'

            os.system(sst_wget)
            os.system(ssta_wget)


        # DAILY SST FROM LAST THREE YEARS
        # -------------------------------
        olr_http = 'https://downloads.psl.noaa.gov/Datasets/cpc_blended_olr-2.5deg/olr.day.anom.nc'
        olr_wget = 'wget -nc '+olr_http+ ' -O '+data_path+'olr.day.anom.nc'
        os.system(olr_wget)

    return( print('ENSO INDICES DOWNLOADED ------------- ') )



# Call Functions
# --------------
sst_download()
cfs_download()
enso_index_download()

