# FIXME: make plotting functions generic on top of different backends
# import collections
# import itertools
# import json
# import numpy as np
# import pandas as pd
from bokeh import plotting
from bokeh.layouts import gridplot
from bokeh.palettes import Set3

# from bokeh.layouts import column
# from bokeh.layouts import row
# from bokeh.models import BasicTicker
# from bokeh.models import BoxSelectTool
# from bokeh.models import CategoricalAxis
# from bokeh.models import CategoricalScale
# from bokeh.models import ColorBar
# from bokeh.models import ColumnDataSource
# from bokeh.models import GeoJSONDataSource
# from bokeh.models import HoverTool
# from bokeh.models import LinearColorMapper
# from bokeh.models.ranges import FactorRange
# from bokeh.palettes import Viridis256
# from bokeh.transform import linear_cmap
# from bokeh.transform import transform

# import scipy

# from stats import cluster_gnn_map


def _get_palette(cmap=Set3[12], n=12, start=0, end=1):
    import matplotlib
    import numpy as np

    linspace = np.linspace(start, end, n)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("customcmap", cmap)
    palette = cmap(linspace)
    hex_palette = [matplotlib.colors.rgb2hex(c) for c in palette]
    return hex_palette


def windowed_plot(df):
    plots = []
    for stat in df.columns:
        if stat == "windows":
            continue
        if len(plots) == 0:
            p = plotting.figure(width=1200, height=200, title=stat)
        else:
            p = plotting.figure(
                width=1200, height=200, x_range=plots[0].x_range, title=stat
            )
        p.line(x="windows", y=stat, source=df)
        plots.append(p)
    pp = gridplot(plots, ncols=1)
    return pp
