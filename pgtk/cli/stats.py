from pgtk.cli.io import add_input_vcfs_argument
from pgtk.cli.io import add_output_prefix_argument
from pgtk.cli.log import add_debug_argument
from pgtk.stats.pca import run_pca


def add_pca_arguments(parser):
    parser.add_argument(
        "--window-size",
        type=int,
        default=500,
        help=(
            "the window size, measured in number of snps, ",
            "to use for identifying ld blocks",
        ),
    )
    parser.add_argument("--window-step", type=int, default=250, help="window step size")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.1,
        help="maximum value of r^2 to include variants",
    )
    parser.add_argument(
        "--iter", type=int, default=5, help="number of pruning iterations"
    )
    parser.add_argument(
        "--components", type=int, default=10, help="number of pca components"
    )
    parser.add_argument(
        "--scaler",
        type=str,
        default=None,
        choices=["patterson", "standard", None],
        help="scaling algorithm",
    )
    parser.add_argument(
        "--plot-ld",
        default=False,
        action="store_true",
        help="Make ld plots before and after pruning",
    )
    parser.add_argument(
        "--plot-ld-variants", type=int, default=1000, help="Number of variants to plot"
    )
    parser.add_argument(
        "--subsample",
        "-s",
        type=int,
        default=None,
        help="subsample raw input to this number of sites",
    )


def add_stats_subcommand(subparsers):
    parser = subparsers.add_parser("stats", help="stats utilities")
    stats_subparsers = parser.add_subparsers(dest="subcommand.stats")
    stats_subparsers.required = True

    # pca parser
    pca_help = """
    Calculate pca coordinates.

    This example is based on Alistair Miles Fast PCA example
    (https://alimanfoo.github.io/2015/09/28/fast-pca.html). The output
    is principal components and a pickled model file with information
    on loadings and more.

    """
    pca_parser = stats_subparsers.add_parser("pca", help=pca_help)
    add_input_vcfs_argument(pca_parser)
    add_pca_arguments(pca_parser)
    add_output_prefix_argument(pca_parser)
    add_debug_argument(pca_parser)
    pca_parser.set_defaults(runner=run_pca)
