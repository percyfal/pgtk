import sys

from pgtk.tskit.stats import run_tskit_stats
from pgtk.tskit.table import run_update_table_metadata


def add_stats_arguments(parser):
    # NB: distinguish one-way and multi-way stats
    parser.add_argument(
        "--statistic", action="store", type=str, nargs="+", default=["diversity"]
    )
    parser.add_argument(
        "--sample-sets", action="store", type=str, nargs="+", default=None
    )
    parser.add_argument("-w", "--window-size", action="store", type=int, default=None)
    parser.add_argument(
        "-m",
        "--mode",
        action="store",
        type=str,
        default="site",
        choices=["site", "branch", "node"],
    )
    parser.add_argument("--span_normalise", action="store_false", default=True)


def add_input_trees_argument(parser):
    parser.add_argument(
        "tree_sequence", help=("Input tree sequence"), type=str, nargs="+"
    )


def add_output_trees_argument(parser):
    parser.add_argument(
        "-o",
        "--outfile",
        action="store",
        default=sys.stdout,
        help=("Tree sequence output"),
    )


def add_tskit_subcommand(subparsers):
    parser = subparsers.add_parser("tskit", help="Tree sequence utilities")
    ts_subparsers = parser.add_subparsers(dest="subcommand.tskit")
    ts_subparsers.required = True

    stats_parser = ts_subparsers.add_parser(
        "stats", help="Calculate tree sequence statistics"
    )
    add_input_trees_argument(stats_parser)
    add_stats_arguments(stats_parser)
    stats_parser.set_defaults(runner=run_tskit_stats)

    update_parser = ts_subparsers.add_parser(
        "update", help="Update tree sequence table metadata"
    )
    add_input_trees_argument(update_parser)
    update_parser.add_argument("metadata", help=("Metadata file to update table"))
    add_output_trees_argument(update_parser)

    update_parser.add_argument(
        "--merge-key",
        "-k",
        action="store",
        default="id",
        help="Metadata key to merge on",
    )
    update_parser.add_argument(
        "--table-name", "-t", action="store", default="individuals"
    )
    update_parser.set_defaults(runner=run_update_table_metadata)
