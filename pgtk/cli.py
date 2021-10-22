"""Console script for pgtk."""
import argparse
import sys
import pgtk
import tskit
import pandas as pd


def run_update_table_metadata(args):
    from pgtk import tsutils

    ts = tskit.load(args.tree_sequence)
    key = args.merge_key
    metadata = pd.read_table(args.metadata)
    metadata.set_index([key], inplace=True)
    tsout = tsutils.update_tablerow_metadata(
        ts, metadata=metadata, tablename=args.table_name, key=key
    )
    tsout.dump(args.outfile)


def add_input_trees_argument(parser):
    parser.add_argument("tree_sequence", help=("Input tree sequence"))


def add_output_trees_argument(parser):
    parser.add_argument(
        "-o",
        "--outfile",
        action="store",
        default=sys.stdout,
        help=("Tree sequence output"),
    )


def add_tsutils_subcommand(subparsers):
    parser = subparsers.add_parser("tsutils", help="Tree sequence utilities")
    ts_subparsers = parser.add_subparsers(dest="subcommand")
    ts_subparsers.required = True

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
    print(args)
    args.runner(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
