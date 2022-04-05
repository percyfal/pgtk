def add_debug_argument(parser):
    parser.add_argument(
        "--debug", help=("Print debug messages"), action="store_true", default=False
    )


def add_threads_argument(parser):
    parser.add_argument(
        "--threads", "-t", type=int, help="number of threads", default=1
    )
