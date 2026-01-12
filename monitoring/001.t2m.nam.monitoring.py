import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import xarray as xr
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import cartopy.feature as cfeature
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

def plot(ax):
  ax.add_feature(cfeature.OCEAN.with_scale('50m'), facecolor='gainsboro', zorder=5)
  ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidths=0.6, zorder=6)
  ax.add_feature(cfeature.STATES.with_scale('50m'), linewidths=0.3, zorder=6)
  ax.add_feature(cfeature.LAKES.with_scale('50m'),
          edgecolor='k', facecolor='white', linewidths=0.3, zorder=6)
  return(ax)

# Swift logo
# ----------
im = plt.imread('images/swift.logo.1.png') # insert local path of the image.

# Load z500
# ---------
fname= data_dir+'/temp.cfs.nc'
tds = xr.open_dataset(fname)['TMP_P0_L104_GLL0'].sel(
        lat_0=slice(72,15),
        lon_0=slice(190,315))

hds = tds.sel(
        lat_0=slice(23,18),
        lon_0=slice(360-161,360-154))

hlat = hds.lat_0
hlon = hds.lon_0
hX, hY = np.meshgrid(hlon,hlat)

lat = tds.lat_0
lon = tds.lon_0
X, Y = np.meshgrid(lon,lat)

color_hex_codes = [
        "e0c3fc","dab6fc","9fa0ff","757bc8",                      # PURPLES
        "001219","005f73","0a9396","94d2bd",                      # BLUES
        "d8f3dc","40916c","1b4332","52b788","e9d8a6",             # GREENS
        "ffcb69","ee9b00","ca6702","ae2012","941b0c","621708",             # REDS
        "370617","b5838d","e5989b","ffb4a2","ffcdb2"]             # PINKS

rgb_values = [mcolors.hex2color('#'+code) for code in color_hex_codes]
cmap = mcolors.LinearSegmentedColormap.from_list('cmap1', rgb_values)

pcrs = ccrs.Miller(central_longitude=180)
tcrs = ccrs.PlateCarree()

fig = plt.figure(figsize=(7,4))
ax = fig.add_subplot(111, 
        projection=pcrs)

cf = ax.contourf(X, Y, tds - 273.15,
        levels=np.arange(-30,51,1),
        extend='both',
        cmap=cmap,
        transform=tcrs)

ax.contour(X, Y, tds - 273.15,
        levels=np.arange(-30,51,1),
        colors='white',
        linewidths=0.03,
        transform=tcrs)

#ax.clabel(cs, [560,575,590], inline=True, fontsize=7)
plot(ax)

ax2 = fig.add_axes([0.07,0.17,0.35,0.22], projection=ccrs.PlateCarree())
ax2.contourf(hX, hY, hds-273.15,
        levels=np.arange(-30,51,1),
        extend='both',
        cmap=cmap,
        transform=tcrs)

plot(ax2)

cbar_ax = fig.add_axes([0.30,0.09,0.60,0.02])
plt.colorbar(cf, orientation='horizontal', cax=cbar_ax)

newax = fig.add_axes([0.02,0.05,0.09,0.09], anchor='SW', zorder=1)
newax.imshow(im, zorder=10)
newax.axis('off')

ax.annotate('CFSv2.1 Surface Temperature',
        (0.50,0.94),
        ha='center', va='bottom', 
        xycoords='figure fraction',
        fontsize=12, fontweight='bold')

ax.annotate(date,
        (0.50,0.905),
        ha='center', va='bottom', 
        xycoords='figure fraction',
        fontsize=10)

ax.annotate('Swift\nClimate and Weather', (0.08,0.090), 
        ha='left', va='center',
        xycoords='figure fraction')

ax.annotate('°C', (0.90,0.14), 
        xycoords='figure fraction',
        ha='right', va='center', fontsize=14)

fig.subplots_adjust(
        left=0.05, right=0.95,
        bottom=0.15, top=0.90)

#plt.savefig('temp.test.png', bbox_inches='tight', dpi=400)
plt.savefig('nam/001.temp.png',  dpi=400)
plt.show()

