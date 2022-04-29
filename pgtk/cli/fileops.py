import argparse

from pgtk.cli.io import add_input_vcfs_argument
from pgtk.cli.io import add_input_zarrs_argument
from pgtk.cli.io import add_output_file_argument
from pgtk.cli.io import add_to_argument
from pgtk.fileops.concat import run_concat
from pgtk.fileops.convert import run_convert


def add_fileops_subcommand(subparsers):
    vcf_parser = subparsers.add_parser("vcf", help="vcf file utilities")
    vcf_parser_subparsers = vcf_parser.add_subparsers(dest="subcommand.vcf")
    vcf_parser_subparsers.required = True

    zarr_parser = subparsers.add_parser("zarr", help="zarr file utilities")
    zarr_parser_subparsers = zarr_parser.add_subparsers(dest="subcommand.zarr")
    zarr_parser_subparsers.required = True

    # Convert parser
    convert_help = """
    Convert input file to other formats and back.
    """

    # Concat parser
    concat_help = """
    Concatenate input files
    """

    vcf_parser_convert_parser = vcf_parser_subparsers.add_parser(
        "convert",
        help=convert_help,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    add_input_vcfs_argument(vcf_parser_convert_parser)
    add_to_argument(vcf_parser_convert_parser, choices=["zarr"], default="zarr")
    vcf_parser_convert_parser.set_defaults(runner=run_convert)

    zarr_parser_concat_parser = zarr_parser_subparsers.add_parser(
        "concat",
        help=concat_help,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    add_input_zarrs_argument(zarr_parser_concat_parser, single=False)
    add_output_file_argument(zarr_parser_concat_parser, default="concat.zarr")
    zarr_parser_concat_parser.filetype = "zarr"
    zarr_parser_concat_parser.set_defaults(runner=run_concat)
