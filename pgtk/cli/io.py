def add_input_vcfs_argument(parser):
    parser.add_argument("vcfs", help=("Input vcf file(s)"), type=str, nargs="+")


def add_output_file_argument(parser):
    parser.add_argument("--output-file", "-o", help=("Output file name"), type=str)


def add_output_prefix_argument(parser):
    parser.add_argument("--output-prefix", "-o", help=("Output file prefix"), type=str)
