'''
This code is to determine
those points in a given 2D spatial data at a particular time
which are surrounded by data on all sides
but does not have data at that point.

Such points are referred as isolated nan points here.
'''
__author__ = "Surya Datta Sudhakar"
__copyright__ = "Copyright 2023, INCOIS"

import xarray as xr, numpy as np

def finding_isolated_nans(data_set1: xr.Dataset, TAXS, ZAXS):
    '''
    Each point is surrounded by 8 points
    °   °   °
    °   .   °
    °   °   °
    '''
    data_set = data_set1['UCMP']
    data_slice = data_set.isel(TAXS=TAXS, ZAXS=ZAXS)
    lat = data_slice['YAXS']
    long = data_slice['XAXS']

    long_lat_values = []

    for i in range(len(lat)):
        for j in range(len(long)):
            if np.isnan(data_slice.isel(YAXS=i, XAXS=j)):
                neighbor_sum = 0
                for m in range(-1, 2):
                    for n in range(-1, 2):
                        if (i+m >= 0 and i+m < len(lat) and j+n >= 0 and j+n < len(long)):
                            if not np.isnan(data_slice.isel(YAXS=i+m, XAXS=j+n)):
                                neighbor_sum += 1
                if neighbor_sum == 8:
                    long_lat_values.append(data_set1.isel(TAXS=TAXS, ZAXS=ZAXS,YAXS=i, XAXS=j))

    # long_lat_values = np.array(long_lat_values)

    return long_lat_values



