def add_input_vcfs_argument(parser):
    parser.add_argument("vcfs", help=("Input vcf file(s)"), type=str, nargs="+")


def add_output_file_argument(parser):
    parser.add_argument("--output-file", "-o", help=("Output file name"), type=str)


def add_output_prefix_argument(parser):
    parser.add_argument("--output-prefix", "-op", help=("Output file prefix"), type=str)


def add_output_suffix_argument(parser, default):
    parser.add_argument(
        "--output-suffix", "-os", help=("Output file suffix"), type=str, default=default
    )


def add_output_type_argument(parser, default, types):
    parser.add_argument(
        "--output-type",
        "-O",
        help="output file type",
        type=str,
        choices=types,
        default=default,
    )


def add_as_bed_argument(parser):
    parser.add_argument(
        "--as-bed", help="save output as bed", action="store_true", default=False
    )
