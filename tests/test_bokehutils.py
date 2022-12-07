#!/usr/bin/env python3
import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.models import GeoJSONDataSource
from bokeh.plotting import figure


def test_data_sources():
    x = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6], "fac": ["a", "b", "c"]})
    _ = ColumnDataSource(x)
    _ = GeoJSONDataSource()


def test_bokeh_renderer():
    plot = figure(width=300, height=300)
    _ = plot.vbar(x=[1, 2, 3], width=0.5, bottom=0, top=[1, 2, 3], color="#CAB2D6")
