"""Stats utilities

"""
import logging

import click
from pgtk.cli import pass_environment
from pgtk.stats.linkage import run_ld_prune
from pgtk.stats.pca import run_pca

__shortname__ = __name__.split(".")[-1]

logger = logging.getLogger(__name__)


@click.group(help=__doc__, name=__shortname__)
@click.pass_context
def main(ctx):
    logger.debug(f"Running command {__shortname__}")


@main.command()
@click.argument("zarr", type=click.Path())
@click.argument("output_file", type=click.Path())
@click.option(
    "--components",
    help="number of pca components",
    default=10,
    type=click.IntRange(
        1,
    ),
)
@click.option(
    "--scaler",
    help="scaling algorithm",
    default="standard",
    type=click.Choice(("patterson", "standard")),
)
@click.option(
    "--subsample",
    "-s",
    help="subsample raw input to this number of sites",
    type=click.IntRange(
        1,
    ),
)
@click.option(
    "--subsample-fraction",
    "-f",
    help="subsample raw input to this fraction of sites",
    type=click.FloatRange(min=0.0, max=1.0),
)
@click.option(
    "--exclude", "-e", help="list of samples to exclude", multiple=True, type=str
)
@click.option(
    "--threads",
    "-t",
    help="number of threads",
    default=1,
    type=click.IntRange(
        1,
    ),
)
@click.option(
    "--workers",
    "-w",
    help="number of workers",
    default=1,
    type=click.IntRange(
        1,
    ),
)
@pass_environment
def pca(
    env,
    zarr,
    output_file,
    components,
    scaler,
    subsample,
    subsample_fraction,
    exclude,
    threads,
    workers,
):
    """Calculate pca coordinates

    Calculate pca coordinates using sgkit. The example is based on
    https://github.com/pystatgen/sgkit/issues/752. The input consists
    of a zarr data structure.
    """
    run_pca(zarr, subsample, subsample_fraction, exclude, components, output_file)


@main.command()
@click.argument("vcf", nargs=-1)
@click.option(
    "--window-size",
    help="the window size, measured in number of snps, to use for identifying ld blocks",
    default=500,
    type=click.IntRange(
        1,
    ),
)
@click.option(
    "--window-step",
    help="the window size, measured in number of snps, to use for identifying ld blocks",
    default=250,
    type=click.IntRange(
        1,
    ),
)
@click.option(
    "--threshold",
    help="maximum value of r^2 to include variants",
    default=0.1,
    type=click.FloatRange(min=0.0, max=1.0),
)
@click.option(
    "--n-iter",
    help="number of pruning iterations",
    default=5,
    type=click.IntRange(
        1,
    ),
)
@click.option("--plot-ld", help="Make ld plots before and after pruning", is_flag=True)
@click.option(
    "--plot-ld-variants",
    help="Number of variants to plot",
    default=1000,
    type=click.IntRange(
        1,
    ),
)
@click.option(
    "--subsample",
    "-s",
    help="subsample raw input to this number of sites",
    type=click.IntRange(
        1,
    ),
)
@click.option(
    "--subsample-fraction",
    "-f",
    help="subsample raw input to this fraction of sites",
    type=click.FloatRange(min=0.0, max=1.0),
)
@click.option(
    "--exclude", "-e", help="list of samples to exclude", multiple=True, type=str
)
@click.option(
    "--threads",
    "-t",
    help="number of threads",
    default=1,
    type=click.IntRange(
        1,
    ),
)
@click.option(
    "--workers",
    "-w",
    help="number of workers",
    default=1,
    type=click.IntRange(
        1,
    ),
)
@click.option("--as-bed", help="save output as bed", is_flag=True)
@click.option("--output-file", "-o", help="Output file name", type=click.Path())
@click.option(
    "--output-suffix", help="Output file suffix", default=".ld_prune", type=str
)
@pass_environment
# def ld_prune(env, vcf, window_size, window_step, threshold, n_iter,
#              plot_ld, plot_ld_variants, subsample, subsample_fraction, exclude,
#              threads, workers, as_bed, output_file, output_suffix):
def ld_prune(env, vcf, threads, workers, **kwargs):
    """Prune variants based on LD."""
    run_ld_prune(vcf, threads, workers, **kwargs)
