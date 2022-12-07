"""Console script for pgtk."""
import argparse
import sys

import pgtk
from pgtk.cli import add_fileops_subcommand
from pgtk.cli import add_plot_subcommand
from pgtk.cli import add_stats_subcommand
from pgtk.cli import add_tskit_subcommand
from pgtk.cli.log import add_debug_argument
from pgtk.cli.log import add_threads_argument
from pgtk.cli.log import add_workers_argument


def get_pgtk_parser():
    top_parser = argparse.ArgumentParser(
        description="Command line interface for pgtk.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    top_parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {pgtk.__version__}"
    )
    top_parser.add_argument(
        "--tmpdir",
        type=str,
        default=None,
        help="write temporary results to tmp directory",
    )

    top_parser.add_argument(
        "--tmpfile",
        type=str,
        default=None,
        help="write temporary results to tmp file",
    )
    add_debug_argument(top_parser)
    add_threads_argument(top_parser)
    add_workers_argument(top_parser)

    subparsers = top_parser.add_subparsers(dest="subcommand")
    subparsers.required = True

    # Add subcommands here
    add_tskit_subcommand(subparsers)
    add_stats_subcommand(subparsers)
    add_fileops_subcommand(subparsers)
    add_plot_subcommand(subparsers)

    return top_parser


def main(arg_list=None):
    """Console script for pgtk."""
    parser = get_pgtk_parser()
    args = parser.parse_args(arg_list)
    args.runner(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover