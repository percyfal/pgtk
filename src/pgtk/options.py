"""Common options for click commands"""
import click

tsfile = click.option("--tsfile", help="tree sequence file")

threads = click.option(
    "--threads",
    "-t",
    help="number of threads",
    default=1,
    type=click.IntRange(
        1,
    ),
)

workers = click.option(
    "--workers",
    "-w",
    help="number of workers",
    default=1,
    type=click.IntRange(
        1,
    ),
)

tmpdir = click.option(
    "--tmpdir", help="temporary directory to write to", default=None, type=click.Path()
)
