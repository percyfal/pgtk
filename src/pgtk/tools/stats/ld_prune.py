"""Run LD pruning on input vcf files.

Run LD pruning on input vcf files (VCF).

"""
import logging

import click
from pgtk.cli import pass_environment
from pgtk.options import tmpdir
from pgtk.stats.linkage import run_ld_prune

logger = logging.getLogger(__name__)


@click.command(help=__doc__)
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
@tmpdir
@pass_environment
def main(env, vcf, threads, workers, **kwargs):
    """Prune variants based on LD."""
    if len(vcf) == 0:
        logger.warning("No input vcf files supplied")
    run_ld_prune(vcf, threads, workers, **kwargs)
