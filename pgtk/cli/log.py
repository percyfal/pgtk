def add_debug_argument(parser):
    parser.add_argument(
        "--debug", help=("Print debug messages"), action="store_true", default=False
    )
