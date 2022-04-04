from pgtk.cli.io import add_input_vcfs_argument
from pgtk.cli.io import add_output_prefix_argument
from pgtk.stats.pca import run_pca


def add_pca_arguments(parser):
    parser.add_argument("--ld-size", type=int, default=500, help="ld size to prune")
    parser.add_argument("--ld-step", type=int, default=100, help="ld step size")
    parser.add_argument("--ld-threshold", type=float, default=0.1, help="ld threshold")
    parser.add_argument(
        "--ld-iter", type=int, default=5, help="number of pruning iterations"
    )
    parser.add_argument(
        "--components", type=int, default=10, help="number of pca components"
    )
    parser.add_argument(
        "--scaler", type=str, default="patterson", help="scaling algorithm"
    )


def add_stats_subcommand(subparsers):
    parser = subparsers.add_parser("stats", help="stats utilities")
    stats_subparsers = parser.add_subparsers(dest="subcommand.stats")
    stats_subparsers.required = True

    # pca parser
    pca_parser = stats_subparsers.add_parser("pca", help="create pca")
    add_input_vcfs_argument(pca_parser)
    add_pca_arguments(pca_parser)
    add_output_prefix_argument(pca_parser)
    pca_parser.set_defaults(runner=run_pca)
