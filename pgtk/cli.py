"""Console script for pgtk."""
import argparse
import sys
import pgtk
from pgtk.tsutils import run_tsutils


def add_tsutils_subcommand(subparsers):
    parser = subparsers.add_parser("tsutils", help="Tree sequence utilities")
    parser.add_argument("ts", help=("Tree sequence file"))
    parser.add_argument(
        "--update_individual_metadata",
        "--uim",
        action="store",
        help=("Update individuals metadata in ts with provided metadata file."),
    )
    parser.add_argument(
        "--individual_metadata_key",
        "--imk",
        action="store",
        default="id",
        help=("Metadata key to merge on"),
    )
    parser.add_argument(
        "--outfile",
        "-o",
        action="store",
        default=sys.stdout,
        help=("Tree sequence output"),
    )
    parser.set_defaults(runner=run_tsutils)


def get_pgtk_parser():
    top_parser = argparse.ArgumentParser(description="Command line interface for pgtk.")
    top_parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {pgtk.__version__}"
    )

    subparsers = top_parser.add_subparsers(dest="subcommand")
    subparsers.required = True

    # Add subcommands here
    add_tsutils_subcommand(subparsers)

    return top_parser


def main(arg_list=None):
    """Console script for pgtk."""
    parser = get_pgtk_parser()
    args = parser.parse_args(arg_list)
    args.runner(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
