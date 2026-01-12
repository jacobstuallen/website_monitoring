import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point
import xarray as xr
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import matplotlib.font_manager as font_manager
font_dir = '/home/js4562/project/conda_envs/earth/fonts/Avenir-Medium.otf'
font_manager.fontManager.addfont(font_dir)
prop = font_manager.FontProperties(fname=font_dir)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = prop.get_name()

# Swift logo
# ----------
im = plt.imread('images/swift.logo.1.png') # insert local path of the image.

def plot(ax):
  ax.add_feature(cfeature.LAND, facecolor='white', zorder=5)
  ax.add_feature(cfeature.COASTLINE, linewidths=0.6, zorder=6)
  return(ax)

# Load SST
# --------
fname= 'data/ice-cover.cfs.test.nc'
cds = xr.open_dataset(fname)['ICEC_P8_L1_GLL0_avg'].load().sel(
        lat_0=slice(90,70))

fname= 'data/ice-thick.cfs.test.nc'
tds = xr.open_dataset(fname)['ICETK_P8_L1_GLL0_avg'].load().sel(
        lat_0=slice(90,70))

lat = tds.lat_0
lon = tds.lon_0

#lon_idx = tds.dims.index('lon_0')
#tds, lon = add_cyclic_point(tds.values, coord=lon, axis=lon_idx)
#cds, lon = add_cyclic_point(cds.values, coord=lon, axis=lon_idx)

X, Y = np.meshgrid(lon,lat)
# TOP ONE LWC
#color_hex_codes = [
#        "001219","005f73","0a9396","94d2bd",             # BLUES
#        "d8f3dc","40916c","1b4332","52b788","e9d8a6",    # GREENS
#        "ee9b00","ca6702","9b2226","f4acb7"]    # REDS

hex1 = ["05668d","028090","00a896","02c39a","f0f3bd"][::-1]
hex2 = ["6d597a", "6930c3"]

color_hex_codes = hex1+hex2

rgb_values = [mcolors.hex2color('#'+code) for code in color_hex_codes]
cmap = mcolors.LinearSegmentedColormap.from_list('cmap1', rgb_values)

pcrs = ccrs.NorthPolarStereo(central_longitude=210)
tcrs = ccrs.PlateCarree()

fig = plt.figure(figsize=(7,4))
ax = fig.add_subplot(111, 
        projection=pcrs)

plt.contour(X, Y, cds,
        levels=[0.05],
        colors='k',
        transform=tcrs)

cf = plt.contourf(X, Y, tds,
        levels=np.arange(0.05,1.6,0.10),
        cmap=cmap,
        transform=tcrs)

cbar_ax = fig.add_axes([0.30,0.09,0.60,0.02])
cbar = fig.colorbar(cf, orientation='horizontal', cax=cbar_ax)

plot(ax)

newax = fig.add_axes([0.02,0.05,0.09,0.09], anchor='SW', zorder=10)
newax.imshow(im)
newax.axis('off')

ax.annotate('CFSv2 Ocean Heat Content',
        (0.50,0.94),
        ha='center', va='bottom', 
        xycoords='figure fraction',
        fontsize=12, fontweight='bold')

ax.annotate('28 August, 2023',
        (0.50,0.905),
        ha='center', va='bottom', 
        xycoords='figure fraction',
        fontsize=10)

ax.annotate('Swift\nClimate and Weather', (0.08,0.090), 
        ha='left', va='center',
        xycoords='figure fraction')

ax.annotate('$1*10^{11}       J/m^{2}$', (0.90,0.14), 
        xycoords='figure fraction',
        ha='right', va='center', fontsize=10)

fig.subplots_adjust(
        left=0.05, right=0.95,
        bottom=0.15, top=0.90)

#plt.savefig('ohc.test.png',  dpi=400)
plt.show()

