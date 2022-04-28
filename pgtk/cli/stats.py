import argparse

from pgtk.cli.io import add_as_bed_argument
from pgtk.cli.io import add_input_vcfs_argument
from pgtk.cli.io import add_input_zarrs_argument
from pgtk.cli.io import add_output_file_argument
from pgtk.cli.io import add_output_suffix_argument
from pgtk.cli.log import add_debug_argument
from pgtk.cli.log import add_threads_argument
from pgtk.cli.log import add_workers_argument
from pgtk.stats.linkage import run_ld_prune
from pgtk.stats.pca import run_pca


def add_ld_prune_arguments(parser):
    parser.add_argument(
        "--window-size",
        type=int,
        default=500,
        help=(
            "the window size, measured in number of snps, "
            "to use for identifying ld blocks"
        ),
    )
    parser.add_argument("--window-step", type=int, default=250, help="window step size")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.1,
        help="maximum value of r^2 to include variants",
    )
    parser.add_argument(
        "--n-iter", type=int, default=5, help="number of pruning iterations"
    )
    parser.add_argument(
        "--plot-ld",
        default=False,
        action="store_true",
        help="Make ld plots before and after pruning",
    )
    parser.add_argument(
        "--plot-ld-variants", type=int, default=1000, help="Number of variants to plot"
    )
    parser.add_argument(
        "--subsample",
        "-s",
        type=int,
        default=None,
        help="subsample raw input to this number of sites",
    )
    parser.add_argument(
        "--subsample-fraction",
        "-f",
        type=float,
        default=None,
        help="subsample raw input to this fraction of sites",
    )
    parser.add_argument(
        "--exclude",
        "-e",
        type=str,
        nargs="*",
        default=None,
        help="list of samples to exclude",
    )


def add_pca_arguments(parser):
    parser.add_argument(
        "--components", type=int, default=10, help="number of pca components"
    )
    parser.add_argument(
        "--scaler",
        type=str,
        default=None,
        choices=["patterson", "standard", None],
        help="scaling algorithm",
    )
    parser.add_argument(
        "--subsample",
        "-s",
        type=int,
        default=None,
        help="subsample raw input to this number of sites",
    )
    parser.add_argument(
        "--subsample-fraction",
        "-f",
        type=float,
        default=None,
        help="subsample raw input to this fraction of sites",
    )
    parser.add_argument(
        "--exclude",
        "-e",
        type=str,
        nargs="*",
        default=None,
        help="list of samples to exclude",
    )


def add_stats_subcommand(subparsers):
    parser = subparsers.add_parser("stats", help="stats utilities")
    stats_subparsers = parser.add_subparsers(dest="subcommand.stats")
    stats_subparsers.required = True

    # pca parser
    pca_help = """Calculate pca coordinates using sgkit.

    The example is based on
    https://github.com/pystatgen/sgkit/issues/752. The output consists
    of a zarr data structure.

    """
    pca_parser = stats_subparsers.add_parser(
        "pca", help=pca_help, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    add_input_zarrs_argument(pca_parser)
    add_pca_arguments(pca_parser)
    add_output_file_argument(pca_parser, default="pca.zarr")
    add_threads_argument(pca_parser)
    add_workers_argument(pca_parser)
    add_debug_argument(pca_parser)
    pca_parser.set_defaults(runner=run_pca)

    # ld prune parser
    ld_prune_help = """
    Prune variants based on LD.
    """
    ld_prune_parser = stats_subparsers.add_parser(
        "ld_prune",
        help=ld_prune_help,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    add_input_vcfs_argument(ld_prune_parser, single=False)
    add_ld_prune_arguments(ld_prune_parser)
    add_as_bed_argument(ld_prune_parser)
    add_output_file_argument(ld_prune_parser)
    add_output_suffix_argument(ld_prune_parser, default=".ld_prune")
    add_threads_argument(ld_prune_parser)
    add_workers_argument(ld_prune_parser)
    add_debug_argument(ld_prune_parser)
    ld_prune_parser.set_defaults(runner=run_ld_prune)
