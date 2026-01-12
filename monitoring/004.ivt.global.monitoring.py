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

def plot(ax):
  ax.add_feature(cfeature.LAND, facecolor='gainsboro', alpha=0.5)
  ax.add_feature(cfeature.COASTLINE, linewidths=0.6)
  return(ax)

# Swift logo
# ----------
im = plt.imread(f'{path}images/website.logo.png') # insert local path of the image.

# Load z500
# ---------
fname= data_dir+'/ivt.cfs.nc'
ivt = xr.open_dataset(fname)['__xarray_dataarray_variable__']

print(ivt)

fname= data_dir+'/mslp.cfs.nc'
mslp = xr.open_dataset(fname)['sp'] / 100

lat = ivt.latitude
lon = ivt.longitude
lon = np.linspace(0,360,len(lon))
X, Y = np.meshgrid(lon,lat)

#color_hex_codes = ["f94144","f3722c","f8961e","f9844a","f9c74f","90be6d","43aa8b","4d908e","edf6f9","FFFFFF"][::-1]

hx_1 = ["edeec9","dde7c7","bfd8bd","98c9a3","77bfa3"] # ARR START
hx_2 = ["b7094c","a01a58","892b64","723c70","5c4d7d","455e89","2e6f95","1780a1","0091ad"][::-1]

color_hex_codes = hx_1+hx_2
print(color_hex_codes)

rgb_values = [mcolors.hex2color('#'+code) for code in color_hex_codes]
cmap = mcolors.LinearSegmentedColormap.from_list('cmap1', rgb_values)

pcrs = ccrs.Robinson(
        central_longitude=210)
tcrs = ccrs.PlateCarree()

fig = plt.figure(figsize=(7,4))
ax = fig.add_subplot(111, 
        projection=pcrs)

cf = ax.contourf(X, Y, ivt,
        levels=np.arange(250,1201,50),
        extend='max',
        cmap=cmap,
        transform=tcrs)

ax.contour(X, Y, ivt,
        levels=np.arange(250,1201,50),
        colors='white',
        linewidths=0.06,
        transform=tcrs)

cs = ax.contour(X, Y, mslp,
        levels=np.arange(1000,1022,7),
        linewidths=0.3,
        colors='k',
        transform=tcrs)

ax.clabel(cs, cs.levels, inline=True, fontsize=5)

plot(ax)

ax.annotate('CFSv2.1 Integrated Vapor Transport',
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
ax.annotate('$Kg*(m/s)^{-1}$', (0.76,0.09), 
        xycoords='figure fraction',
        ha='left', va='center', fontsize=14)
# ------------------------


fig.subplots_adjust(
        left=0.05, right=0.95,
        bottom=0.15, top=0.90)

plt.savefig(f'{path}global/004.ivt.png', bbox_inches='tight', dpi=400)
plt.show()

