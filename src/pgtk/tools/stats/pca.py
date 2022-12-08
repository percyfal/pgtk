"""Calculate principal components from input.

WIP: Currently fails on chunking

Calculate principal components from INPUT, which can be in a number of
different formats. Currently sgkit (zarr) is supported.

"""
import logging

import click
from pgtk.cli import pass_environment
from pgtk.stats.pca import run_pca

logger = logging.getLogger(__name__)


@click.command(help=__doc__)
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
def main(
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
