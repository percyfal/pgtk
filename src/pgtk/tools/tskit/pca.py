"""Make pca from tree sequence file

Make pca plot from tree sequence file (TSFILE). By default, samples
are colored according to population obtained from tree sequence
metadata. If none is available, no coloring is added.

"""
import logging

import click
import tskit
from bokeh.io.doc import curdoc
from bokeh.themes import Theme
from pgtk.arguments import tsfile
from pgtk.cli import pass_environment
from pgtk.options import threads
from pgtk.options import workers
from pgtk.plotting.pca import _get_palette
from pgtk.plotting.pca import bokeh_plot_pca
from pgtk.stats.pca import pca
from pgtk.tskit.convert import ts_to_sgkit_dataset


logger = logging.getLogger(__name__)


def validate_populations(ctx, param, value):
    if value is None:
        return
    return value.split(",")


def validate_samples_individuals(ctx, param, value):
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
@tsfile
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
    "--tsploidy",
    help="sample output ploidy",
    type=click.IntRange(
        1,
    ),
    default=2,
)
@click.option(
    "--samples",
    type=click.UNPROCESSED,
    callback=validate_samples_individuals,
    default=None,
    help="subset to samples",
)
@click.option(
    "--individuals",
    type=click.UNPROCESSED,
    callback=validate_samples_individuals,
    default=None,
    help="subset to individuals",
)
@click.option(
    "--populations",
    type=click.UNPROCESSED,
    callback=validate_populations,
    default=None,
    help="subset to populations",
)
@pass_environment
def main(
    env,
    tsfile,
    contig_id,
    output_file,
    png,
    ncols,
    no_legend,
    bokeh_theme_file,
    ploidy,
    tsploidy,
    samples,
    individuals,
    populations,
    **kwargs,
):
    ts = tskit.load(tsfile)
    if (len(ts.samples()) % 2) != 0:
        logger.warning(
            "assuming diploids; uneven number of samples"
            " (chromosomes) in tree sequence file"
        )
    ds = ts_to_sgkit_dataset(
        ts,
        contig_id,
        ploidy=ploidy,
        samples=samples,
        individuals=individuals,
        populations=populations,
    )
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
    if tsploidy != ploidy:
        df["population"] = [ds.cohorts.data[i] for i in ds.sample_cohort[::ploidy]]
    else:
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
