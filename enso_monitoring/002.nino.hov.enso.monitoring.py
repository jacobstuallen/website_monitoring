import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
import sys
import os
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import matplotlib.font_manager as font_manager
font_dir = '/glade/work/jsallen/conda-envs/fonts/Avenir-Medium.otf'
font_manager.fontManager.addfont(font_dir)
prop = font_manager.FontProperties(fname=font_dir)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = prop.get_name()

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
    YYYYMMDD = str(date).replace('-','')

# For testing
YYYYMMDD = "20251227"
print(date)
date = "2025-12-27"

# project dirs
proj_dir = '/glade/u/home/jsallen/projects/swift/'
data_dir = '/glade/u/home/jsallen/projects/swift/data/'+YYYYMMDD

# Swift logo
# ----------
im = plt.imread('images/website.logo.png') # insert local path of the image.

def plot(ax):
  ax.add_feature(cfeature.LAND, facecolor='white', zorder=5)
  ax.add_feature(cfeature.COASTLINE, linewidths=0.6, zorder=6)
  return(ax)

# Load SST
# --------

for yy in range (1,4):

    fname = data_dir+'/sst.day.anom.*.nc'
    ds = xr.open_mfdataset(fname)['anom'][-365*yy:].sel(
            lat=slice(-5,5),
            lon=slice(120,280)).mean(dim='lat')

    lon = ds.lon
    time = ds.time

    # TOP ONE LWC
    color_hex_codes = [
            "006d77","001219","005f73",
            "0a9396","94d2bd","FFFFFF",
            "ee9b00","ca6702","ae2012",
            "9b2226","b5838d"]

    rgb_values = [mcolors.hex2color('#'+code) for code in color_hex_codes]
    cmap = mcolors.LinearSegmentedColormap.from_list('cmap1', rgb_values)

    fig = plt.figure(figsize=(8,8.0))
    ax = fig.add_subplot(111)

    cf = plt.contourf(lon, time, ds,
            levels=np.arange(-3,3.1,0.20),
            extend='both',
            cmap=cmap)

    plt.contour(lon, time, ds,
            levels=np.arange(-3,3.1,0.40),
            colors='white',
            linewidths=0.05)

    plt.contour(lon, time, ds,
            levels=[-0.5,0.5],
            colors='k',
            linewidths=0.4)

    ax.grid(color='k')
    #ax.grid(width=0.5, colors='k', ls='--')

    cbar_ax = fig.add_axes([0.40,0.09,0.55,0.02])
    plt.colorbar(cf, orientation='horizontal', cax=cbar_ax, label='°C')


    ax.annotate('OISST V2.1 Daily SST Anomaly',
            (0.52,0.97),
            ha='center', va='bottom', 
            xycoords='figure fraction',
            fontsize=12, fontweight='bold')

    if yy == 1:
        ax.annotate(r'Longitude and Time Hovm$\ddot{o}$ller: Preceding year',
            (0.52,0.942),
            ha='center', va='bottom', 
            xycoords='figure fraction',
            fontsize=10)

    if yy > 1:
        ax.annotate(r'Longitude and Time Hovm$\ddot{o}$ller: Preceding '+str(yy)+' years'.format(yy),
            (0.52,0.942),
            ha='center', va='bottom', 
            xycoords='figure fraction',
            fontsize=10)

    #ax.annotate('Swift\nClimate and Weather', (0.12,0.085), 
    #        ha='left', va='center',
    #        xycoords='figure fraction')

    newax = fig.add_axes([0.02,0.02,0.07,0.07], anchor='SW', zorder=1)
    newax.imshow(im)
    newax.axis('off')
    fig.text(0.095, 0.050, 'JSA', fontsize=18,
             ha='left', va='center', fontweight='bold')

    #ax.annotate('°C', (0.93,0.13), 
    #        xycoords='figure fraction',
    #        ha='right', va='center', fontsize=14)

    fig.subplots_adjust(
        top=0.94, bottom=0.15, left=0.15,
        right=0.92, hspace=0.2, wspace=0.2)

    plt.savefig('figures/002.enso-hov.{}.png'.format(yy),  dpi=400)
    plt.show()

