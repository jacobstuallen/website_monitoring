import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
import pandas as pd
from scipy import signal
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


def moving_average(a, window_size):
    cumsum = np.cumsum(np.insert(a, 0, 0))
    return (cumsum[window_size:] - cumsum[:-window_size]) / float(window_size)

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

# ENSO Indices
indices  = ['ANOM', 'ANOM.1', 'ANOM.2', 'ANOM.3']
save_str = ['1+2','3','4','3.4']

# LOAD ENSO INDICES-
# ------------------
#enso = signal.detrend(pd.read_csv(data_dir+'/ersst.nino.mon.txt', 
#        delimiter=r"\s+")['ANOM.3'])

for i, index in enumerate(indices):

    enso = signal.detrend(
            pd.read_csv(
                data_dir+'/ersst.nino.mon.txt', delimiter=r"\s+")[index] )

    y_data_max = np.max(enso) + 0.2
    y_data_min = np.min(enso) - 0.2
    enso = moving_average(enso, 3)

    # PLOT A NICE LONG THIN TIME SERIES
    time_ax = pd.date_range('1950-01-01', periods=len(enso), freq='MS')

    # Split the data in half
    mid_point = len(enso) // 2
    enso_first_half = enso[:mid_point]
    enso_second_half = enso[mid_point:]
    time_first_half = time_ax[:mid_point]
    time_second_half = time_ax[mid_point:]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
    fig.subplots_adjust(
            left=0.10, right=0.95,
            bottom=0.11, top=0.95, hspace=0.18)

    # Function to plot each subplot
    def plot_enso(ax, time, data, title_suffix, add_marker=False):
        ax.plot(time, data, color='k', lw=1.5, zorder=10)
        ax.grid(lw=0.2, ls='--')
        
        ax.fill_between(time, 0.5, data, np.where(data>0.5, True, False), color='indianred')
        ax.fill_between(time, -0.5, data, np.where(data<-0.5, True, False), color='cadetblue')
        
        ax.set_ylim(y_data_min, y_data_max)
        ax.set_ylabel('°C')
        ax.set_title(f'Monthly Niño {save_str[i]} Index : ERSST {title_suffix}', loc='left')
        ax.minorticks_on()
        ax.tick_params(axis='both', which='minor', color='black', length=3)
        
        # Only add marker, line, and annotation if requested
        if add_marker:
            ax.plot(time[-1], data[-1], marker='o',
                    markeredgecolor='darkslategray',
                    color='none', markersize=10, markeredgewidth=2)
            
            # Get the current y-axis limits
            ymin, ymax = ax.get_ylim()

            # Calculate the ratio for where the data point is within the y-axis range
            yax_ratio = (data[-1] - ymin) / (ymax - ymin)
            
            # Draw vertical line from the last data point to the top of the y-axis
            ax.axvline(time[-1], ymin=yax_ratio, ymax=0.985,
                    color='darkslategray', ls='-',
                    lw=2.0, clip_on=False, zorder=10)
            
            box = dict(boxstyle='round', facecolor='white', edgecolor='darkslategray', linewidth=2)
            
            # Position annotation just above the y-axis maximum
            y_position = ymax
            ax.annotate(str(time[-1].date())+ ': {}°C'.format(round(data[-1], 2)), 
                        (time[-1], y_position),
                    xycoords='data', ha='center',
                    annotation_clip=False, va='bottom',
                    bbox=box)


    # Plot first half (without marker)
    plot_enso(ax1, time_first_half, enso_first_half, '(1950-1987)', add_marker=False)

    # Plot second half (with marker)
    plot_enso(ax2, time_second_half, enso_second_half, '(1987-Present)', add_marker=True)
    ax2.set_xlabel('Year')

    newax = fig.add_axes([0.02,0.02,0.07,0.07], anchor='SW', zorder=1)
    newax.imshow(im)
    newax.axis('off')
    fig.text(0.095, 0.050, 'JSA', fontsize=18, 
             ha='left', va='center', fontweight='bold')

    plt.savefig(f'figures/nino{save_str[i]}.png', dpi=500)
    plt.show()
