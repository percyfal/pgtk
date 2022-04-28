import argparse

from pgtk.cli.io import add_output_file_argument


def add_plot_subcommand(subparsers):
    parser = subparsers.add_parser("plot", help="plotting utilities")
    plot_subparsers = parser.add_subparsers(dest="subcommand.plot")
    plot_subparsers.required = True

    pca_help = """Make pca plot"""
    pca_parser = plot_subparsers.add_parser(
        "pca", help=pca_help, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    add_output_file_argument(pca_parser)
