import itertools
import math
import re

import pandas as pd
import sgkit as sg
from bokeh.io import curdoc
from bokeh.io import export_png
from bokeh.io import output_file
from bokeh.io import show
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource
from bokeh.palettes import Set3
from bokeh.plotting import figure
from bokeh.themes import Theme


def _get_palette(cmap=Set3[12], n=12, start=0, end=1):
    import matplotlib
    import numpy as np

    linspace = np.linspace(start, end, n)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("customcmap", cmap)
    palette = cmap(linspace)
    hex_palette = [matplotlib.colors.rgb2hex(c) for c in palette]
    return hex_palette


# NB: https://speciationgenomics.github.io/pca/ calculates explained
# variance from sums of plink eigenvals, although not all components
# have been calculated
def bokeh_plot_pca_coords(df, explained, *, pc1=1, pc2=2, legend=True, **kw):
    source = ColumnDataSource(df)
    x = explained[pc1 - 1]
    y = explained[pc2 - 1]
    xlab = f"PC{pc1} ({x:.1f}%)"
    ylab = f"PC{pc2} ({y:.1f}%)"

    metadata_columns = [x for x in df.columns if not re.match("^(PC[0-9]+|color)$", x)]
    tooltips = [(x, f"@{x}") for x in metadata_columns]
    p = figure(
        x_axis_label=xlab,
        y_axis_label=ylab,
        tooltips=tooltips,
        title=f"PC{pc1} vs PC{pc2}",
        **kw,
    )
    kw = {}
    if legend:
        kw.update(**{"legend_group": "population"})
    p.circle(
        x=f"PC{pc1}",
        y=f"PC{pc2}",
        source=source,
        color="color",
        alpha=0.8,
        line_color="black",
        **kw,
    )
    if legend:
        p.add_layout(p.legend[0], "right")
    return p


def bokeh_plot_pca(
    df, eigenvals, ncomp=6, filename=None, png=False, legend=True, ncols=None, **kw
):
    pairs = list(itertools.combinations(range(ncomp), 2))
    n = len(pairs)
    if ncols is None:
        if n <= 3:
            ncols = 2
        else:
            ncols = math.floor(math.sqrt(n))
    plots = []
    for (i, j) in pairs:
        p = bokeh_plot_pca_coords(
            df, eigenvals, pc1=i + 1, pc2=j + 1, legend=legend, **kw
        )
        plots.append(p)
        # if png:
        #     if filename:
        #         pngout = f"{filename}.PC{i+1}-PC{j+1}.png"
        #     else:
        #         pngout = f"PC{i+1}-PC{j+1}.png"
        #     export_png(p, filename=pngout)
    plots.append
    gp = gridplot(plots, ncols=ncols)

    if filename is not None:
        output_file(filename)
        if png:
            export_png(gp, filename=f"{filename}.png")
        show(gp)
    else:
        return gp


def run_plot_pca(input_file, metadata, components, output_file, bokeh_theme, **kwargs):
    if input_file.endswith("eigenvec"):
        header = 0
        sep = " "
        colnames = ["FID", "IID"]
        # Check header
        with open(input_file) as fh:
            line = fh.readline()
            if not line.startswith("FID"):
                header = None
            if len(line.split(sep)) == 1:
                sep = "\t"
        df = pd.read_table(input_file, header=header, sep=sep)
        if header is None:
            colnames += [f"PC{i+1}" for i in range(df.shape[1] - 2)]
            df.columns = colnames
        df.set_index(["FID"], inplace=True)
        df.index.names = ["sample"]
        df = df.drop(["IID"], axis=1)
        df.reset_index(inplace=True)
        eigenval_file = input_file.replace("eigenvec", "eigenval")
        eigenvals = pd.read_table(eigenval_file, header=None)
        explained = eigenvals[0].values / sum(eigenvals[0].values) * 100
    elif input_file.endswith("zarr"):
        # Assume from sgkit
        ds = sg.load_dataset(input_file)
        explained = ds.sample_pca_explained_variance_ratio.values * 100
        df = (
            ds.sample_pca_projection.to_dataframe()
            .reset_index()
            .pivot(index="samples", columns="components")
        )
        df.index.names = ["sample"]
        df.columns = [f"PC{i+1}" for _, i in df.columns]
        df.reset_index(inplace=True)
        df["sample"] = ds.sample_id[df["sample"].values].values
    else:
        raise (Exception(f"No support for file type {input_file}"))
    if metadata is not None:
        md = pd.read_table(metadata)
        try:
            df = df.merge(md, on="sample")
        except Exception as e:
            print(e)
    if "population" not in df.columns:
        df["population"] = df["sample"]
    groups = sorted(list(set(df["population"])))
    color = {x: y for x, y in zip(groups, _get_palette(n=len(groups)))}
    df["color"] = [color[x] for x in df["population"]]
    if bokeh_theme is not None:
        curdoc().theme = Theme(filename=bokeh_theme)
    bokeh_plot_pca(
        df,
        explained,
        filename=output_file,
        png=kwargs["png"],
        legend=(not kwargs["no_legend"]),
        ncomp=components,
        ncols=kwargs["ncols"],
    )
