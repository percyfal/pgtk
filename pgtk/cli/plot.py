import argparse

from pgtk.cli.io import add_bokeh_theme_argument
from pgtk.cli.io import add_input_file_argument
from pgtk.cli.io import add_metadata_argument
from pgtk.cli.io import add_output_file_argument
from pgtk.plotting.pca import run_plot_pca


def add_plot_subcommand(subparsers):
    parser = subparsers.add_parser("plot", help="plotting utilities")
    plot_subparsers = parser.add_subparsers(dest="subcommand.plot")
    plot_subparsers.required = True

    pca_help = """Make pca plot"""
    pca_parser = plot_subparsers.add_parser(
        "pca", help=pca_help, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    add_input_file_argument(pca_parser)
    add_output_file_argument(pca_parser)
    add_metadata_argument(pca_parser)
    add_bokeh_theme_argument(pca_parser)
    pca_parser.add_argument(
        "--png",
        help="Make png plots for each pc combination",
        action="store_true",
        default=False,
    )
    pca_parser.add_argument(
        "--no-legend", help="Don't draw legend", action="store_true", default=False
    )
    pca_parser.add_argument(
        "--ncols",
        help="Number of columns in gridplot",
        action="store",
        type=int,
        default=None,
    )
    pca_parser.add_argument(
        "--ncomp",
        help="Number of pc components",
        action="store",
        type=int,
        default=None,
    )
    pca_parser.set_defaults(runner=run_plot_pca)
