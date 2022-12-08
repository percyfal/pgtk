"""Make pca from vcf

Make pca plot from vcf (VCF).

"""
import logging
import os
import re
import sys

import click
import cyvcf2
import pandas as pd
import sgkit as sg
from bokeh.io.doc import curdoc
from bokeh.themes import Theme
from pgtk.cli import pass_environment
from pgtk.options import threads
from pgtk.options import workers
from pgtk.plotting.pca import _get_palette
from pgtk.plotting.pca import bokeh_plot_pca
from pgtk.stats.pca import pca
from sgkit.io.vcf import vcf_to_zarr

logger = logging.getLogger(__name__)


def validate_populations(ctx, param, value):
    if value is None:
        return
    return value.split(",")


def validate_samples(ctx, param, value):
    if value is None:
        return
    data = []
    try:
        indices = value.split(",")
        for i in indices:
            v = i.split("-")
            if len(v) == 1:
                data.append(int(v[0]))
            elif len(v) == 2:
                if int(v[0]) > int(v[1]):
                    raise
                data.extend(range(int(v[0]), int(v[1]) + 1))
            else:
                raise
    except ValueError as e:
        print(e)
    except Exception as e:
        print(e)
    return data


@click.command(help=__doc__)
@click.argument("vcf", type=click.Path(exists=True))
@click.argument("metadata", type=click.Path(exists=True))
@click.option("--components", type=int, default=3, help="number of pca components")
@click.option(
    "--scaler",
    type=click.Choice(["patterson", "standard"]),
    default=None,
    help="scaling algorithm",
)
@click.option("--exclude", help="list of samples to exclude", type=str, multiple=True)
@click.option(
    "--subsample",
    "-s",
    default=None,
    type=click.IntRange(
        1,
    ),
    help="subsample raw input to this number of sites",
)
@click.option(
    "--subsample-fraction",
    "-f",
    default=None,
    type=click.FloatRange(0.0, 1.0),
    help="subsample raw input to this number of sites",
)
@threads
@workers
@click.option("--contig-id", type=str, default="1")
@click.option("--output-file", "-o", type=click.Path(), default="bokeh.html")
@click.option("--png", help="Make png plots for each pc combination", is_flag=True)
@click.option("--ncols", help="Number of columns in gridplot", default=None, type=int)
@click.option("--no-legend", help="Don't draw legend", is_flag=True)
@click.option("--bokeh-theme-file", help="bokeh theme file", type=click.Path())
@click.option(
    "--ploidy",
    help="sample output ploidy",
    type=click.IntRange(
        1,
    ),
    default=2,
)
@click.option(
    "--samples",
    type=click.UNPROCESSED,
    callback=validate_samples,
    default=None,
    help="subset to samples. NB: in vcf files samples and individuals are assumed equal",
)
@click.option(
    "--populations",
    type=click.UNPROCESSED,
    callback=validate_populations,
    default=None,
    help="subset to populations",
)
@click.option(
    "--force",
    is_flag=True,
    help="force regeneration of zarr output",
)
@pass_environment
def main(
    env,
    vcf,
    metadata,
    contig_id,
    output_file,
    png,
    ncols,
    no_legend,
    bokeh_theme_file,
    ploidy,
    samples,
    populations,
    force,
    **kwargs,
):
    md = pd.read_table(metadata)
    if md.columns.values.tolist() != ["sample", "population"]:
        logger.error(
            "metadata table must consist of two columns with "
            "headings 'sample' and 'population'"
        )
        sys.exit()
    md.set_index("sample", inplace=True)

    vcffh = cyvcf2.VCF(vcf)
    if samples is None:
        samples = vcffh.samples
    if populations is None:
        populations = md["population"].values.tolist()

    md = md.loc[
        samples,
    ][md["population"].isin(populations)]
    samples = md.index.values
    popid = dict(map(reversed, dict(enumerate(md.population.unique())).items()))
    md["popid"] = md.population.map(popid)
    zarr = re.sub(".vcf.gz|.vcf|.bcf", ".zarr", vcf)
    if not os.path.exists(zarr) or force:
        logger.info(f"Converting from {vcf} to {zarr}")
        vcf_to_zarr(vcf, zarr)
    ds = sg.load_dataset(zarr)
    if len(samples) != len(ds.samples):
        ds = ds.sel(samples=ds.sample_id.isin(samples.tolist()))

    ids = ds.sample_id.values.tolist()
    ds["sample_cohort"] = md.loc[ids, "popid"].values.flatten().tolist()
    ds = ds.assign({"cohorts": list(popid.keys())})
    ds = pca(ds, **kwargs)

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
    df["population"] = [ds.cohorts.data[i] for i in ds.sample_cohort]
    groups = sorted(list(set(df["population"])))
    color = {x: y for x, y in zip(groups, _get_palette(n=len(groups)))}
    df["color"] = [color[x] for x in df["population"]]
    if bokeh_theme_file is not None:
        curdoc().theme = Theme(filename=bokeh_theme_file)
    bokeh_plot_pca(
        df,
        explained,
        filename=output_file,
        png=png,
        legend=(not no_legend),
        ncomp=kwargs["components"],
        ncols=ncols,
    )
