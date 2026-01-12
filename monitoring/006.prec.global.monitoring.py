import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import colormaps as cmaps
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import sys 
import os

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

# project dirs
proj_dir = '/glade/u/home/jsallen/projects/swift/'
data_dir = '/glade/u/home/jsallen/projects/swift/data/'+YYYYMMDD
path     = '/glade/u/home/jsallen/projects/swift/monitoring/'

# Swift logo
# ----------
im = plt.imread(f'{path}images/website.logo.png') # insert local path of the image.

def plot(ax):
  ax.add_feature(cfeature.LAND, facecolor='none', zorder=4)
  ax.add_feature(cfeature.COASTLINE, linewidths=0.6, zorder=5)
  return(ax)

# Load SST
# --------
fname = data_dir+'/prec.cfs.nc'
ds = xr.open_dataset(fname)['prate'].load() * 3600

fname2 = data_dir+'/mslp.cfs.nc'
ds2 = xr.open_dataset(fname2)['sp'].load()

lat = ds.latitude
lon = ds.longitude
lon = np.linspace(0,360,len(lon))
X, Y = np.meshgrid(lon,lat)

# TOP ONE LWC
color_hex_codes = ["006d77","001219","005f73",
                   "0a9396","94d2bd","FFFFFF",
                   "ee9b00","ca6702","ae2012",
                   "9b2226","b5838d"]

rgb_values = [mcolors.hex2color('#'+code) for code in color_hex_codes]
#cmap = mcolors.LinearSegmentedColormap.from_list('cmap1', rgb_values)
cmap='YlGnBu'
cmap = cmaps.nice_gfdl

pcrs = ccrs.Robinson(
        central_longitude=210)
tcrs = ccrs.PlateCarree()

fig = plt.figure(figsize=(7,4))
ax = fig.add_subplot(111, 
        projection=pcrs)

cf = plt.contourf(X, Y, ds,
        levels=np.arange(0.20,7.1,0.20),
        extend='max',
        cmap=cmap,
        transform=tcrs)

plt.contour(X, Y, ds,
        levels=np.arange(0.20,7.1,0.20),
        extend='max',
        colors='white',
        linewidths=0.04,
        transform=tcrs)

#cs = plt.contour(X, Y, ds2/100,
#        levels=np.arange(970,1020,10),
#        extend='max',
#        colors='k',
#        linewidths=0.4,
#        transform=tcrs)

#ax.clabel(cs, [970,990,1010], inline=True, fontsize=7) 

plot(ax)

ax.annotate('CFSV2 Daily Precipitation Rate',
        (0.50,0.94),
        ha='center', va='bottom', 
        xycoords='figure fraction',
        fontsize=12, fontweight='bold')

ax.annotate(date,
        (0.50,0.905),
        ha='center', va='bottom', 
        xycoords='figure fraction',
        fontsize=10)

# ------------------------
cbar_ax = fig.add_axes([0.25,0.09,0.50,0.03])
plt.colorbar(cf, orientation='horizontal', cax=cbar_ax)#, label='°C')
newax = fig.add_axes([0.03,0.03,0.09,0.09], anchor='SW', zorder=1)
newax.imshow(im)
newax.axis('off')
fig.text(0.085, 0.060, 'JSA', fontsize=16,
             ha='left', va='center', fontweight='bold')
ax.annotate('mm', (0.76,0.09),
        xycoords='figure fraction',
        ha='left', va='center', fontsize=14)
# ------------------------

fig.subplots_adjust(
        left=0.05, right=0.95,
        bottom=0.15, top=0.90)

plt.savefig(f'{path}global/prec.anom.png', bbox_inches='tight', dpi=400)
plt.show()

