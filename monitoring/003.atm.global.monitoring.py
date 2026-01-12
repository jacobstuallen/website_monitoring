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
path     = '/glade/u/home/jsallen/projects/swift/monitoring/'

# ----------
def plot(ax):
  ax.add_feature(cfeature.LAND, facecolor='gainsboro', alpha=0.5)
  ax.add_feature(cfeature.COASTLINE, linewidths=0.6)
  return(ax)

# Swift logo
# ----------
im = plt.imread(f'{path}images/website.logo.png') # insert local path of the image.

# Load z500
# ---------
fname= data_dir+'/z500.cfs.nc'
hds = xr.open_dataset(fname, decode_timedelta=False)['gh']

fname= data_dir+'/u500.cfs.nc'
uds = xr.open_dataset(fname, decode_timedelta=False)['u']

fname= data_dir+'/v500.cfs.nc'
vds = xr.open_dataset(fname, decode_timedelta=False)['v']

lat = hds.latitude
lon = hds.longitude
lon = np.linspace(0,360,len(lon))
X, Y = np.meshgrid(lon,lat)

color_hex_codes = ["f94144","f3722c","f8961e","f9c74f","90be6d","43aa8b","4d908e","edf6f9","FFFFFF"][::-1]

rgb_values = [mcolors.hex2color('#'+code) for code in color_hex_codes]
cmap = mcolors.LinearSegmentedColormap.from_list('cmap1', rgb_values)

pcrs = ccrs.Robinson(
        central_longitude=210)
tcrs = ccrs.PlateCarree()

fig = plt.figure(figsize=(7,4))
ax = fig.add_subplot(111, 
        projection=pcrs)

cs = ax.contour(X, Y, hds/10,
        levels=np.arange(560,591,7.5),
        linewidths=0.9,
        colors='k',
        transform=tcrs)

ax.clabel(cs, [560,575,590], inline=True, fontsize=7)

cf = ax.contourf(X, Y, np.sqrt( uds.values**2 + vds.values**2) ,
        levels=np.arange(10,56,2),
        extend='max',
        cmap=cmap,
        transform=tcrs)


ax.contour(X, Y, np.sqrt( uds.values**2 + vds.values**2) ,
        levels=np.arange(10,56,2),
        colors='white',
        linewidths=0.08,
        transform=tcrs)

plot(ax)

ax.annotate('CFSv2.1 500hPa Wind and Geopotential Height (m)',
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
ax.annotate('m/s', (0.76,0.09), 
        xycoords='figure fraction',
        ha='left', va='center', fontsize=14)
# ------------------------

fig.subplots_adjust(
        left=0.05, right=0.95,
        bottom=0.15, top=0.90)

plt.savefig(f'{path}global/003.atm500.png', bbox_inches='tight', dpi=500)
#plt.show()
