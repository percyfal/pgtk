#!/usr/bin/env python3
# Recall: we *cannot* subclass bokeh Figure objects since these are
# tightly linked to Javascript code. One has to build figures from
# available functions. The question is whether to package data with
# custom figure class (as in seaborn?) or just write functions that
# treat input data. Best would be to follow bokeh conventions as
# closely as possibly. Also would want generic plotting for e.g.
# matplotlib output. So: should one package data with plotting
# functions?
# Seaborn: heatmap function creates _HeatMapper class that is an axes
# object and that stores data
# Bokeh: figure function creates Figure class which is a Plot,
# GlyphAPI object. When a glyph is added (e.g. circle) a GlyphRenderer
# or list thereof is created
