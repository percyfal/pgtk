"""Make plot of PCA components.

Make plot of PCA components based on INPUT, which can be in a number
of different formats. Currently plink (*eigenvec) and sgkit (zarr) are
supported.

"""
import logging

import click
from pgtk.cli import pass_environment
from pgtk.plotting.pca import run_plot_pca

logger = logging.getLogger(__name__)


@click.command(help=__doc__)
@click.argument("input_file", type=click.Path())
@click.argument("metadata", type=click.Path(exists=True))
@click.option("--output-file", "-o", type=click.Path(), default="bokeh.html")
@click.option("--components", type=int, default=3, help="number of pca components")
@click.option(
    "--scaler",
    type=click.Choice(["patterson", "standard"]),
    default=None,
    help="scaling algorithm",
)
@click.option("--contig-id", type=str, default="1")
@click.option("--output-file", "-o", type=click.Path(), default="bokeh.html")
@click.option("--png", help="Make png plots for each pc combination", is_flag=True)
@click.option("--ncols", help="Number of columns in gridplot", default=None, type=int)
@click.option("--no-legend", help="Don't draw legend", is_flag=True)
@click.option("--bokeh-theme-file", help="bokeh theme file", type=click.Path())
# @click.option(
#     "--samples",
#     type=click.UNPROCESSED,
#     callback=validate_samples,
#     default=None,
#     help=("subset to samples. NB: in vcf files samples"
#           "and individuals are assumed equal"),
# )
# @click.option(
#     "--populations",
#     type=click.UNPROCESSED,
#     callback=validate_populations,
#     default=None,
#     help="subset to populations",
# )
@click.option(
    "--force",
    is_flag=True,
    help="force regeneration of zarr output",
)
@pass_environment
def main(
    env,
    input_file,
    metadata,
    output_file,
    components,
    scaler,
    bokeh_theme_file,
    **kwargs
):
    run_plot_pca(
        input_file,
        metadata,
        components,
        output_file,
        bokeh_theme=bokeh_theme_file,
        **kwargs
    )
