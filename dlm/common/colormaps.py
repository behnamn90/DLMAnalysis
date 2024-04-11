import math
import numpy as np
import matplotlib as mpl


def get_norm(all_times):
    for_norm = [x for x in all_times if str(x) != 'nan']
    norm = mpl.colors.Normalize(vmin=np.min(for_norm), vmax=np.max(for_norm))
    return norm

def get_colors(times, norm, cmap = mpl.pyplot.cm.rainbow):
    mymap = ['white'] * len(times)
    nans = [math.isnan(e) for e in times]
    non_nan_idxs = [i for i, x in enumerate(nans) if x == False]
    reverse = {b: a for a, b in enumerate(non_nan_idxs)}
    for_map = [x for x in times if str(x) != 'nan']
    colors = cmap(norm(for_map))
    for idx in non_nan_idxs:
        mymap[idx] = colors[reverse[idx]]
    return mymap


def get_norm_no_extreme(all_times,cmin,cmax):
    for_norm = [x for x in all_times if str(x) != 'nan']
    norm = mpl.colors.Normalize(vmin=cmin, vmax=cmax)
    return norm

def get_colors_no_extreme(times, cmin, cmax, cmap = mpl.pyplot.cm.rainbow):
    norm = mpl.colors.Normalize(vmin=cmin, vmax=cmax)
    mymap = ['white'] * len(times)
    non_nan_idxs = np.where(~np.isnan(times))[0]
    reverse = {b: a for a, b in enumerate(non_nan_idxs)}
    for_map = times[~np.isnan(times)]
    colors = cmap(norm(for_map))
    for idx in non_nan_idxs:
        mymap[idx] = colors[reverse[idx]]
    return mymap