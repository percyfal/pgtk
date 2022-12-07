"""Convert TREE_SEQUENCE file to sgkit-compatible dataset.


"""
import logging

import click
from pgtk.cli import pass_environment

logger = logging.getLogger(__name__)


@click.command(help=__doc__)
@click.argument("tree_sequence", type=click.Path())
@click.option("--output-file", type=click.Path())
@pass_environment
def cli(env, infile, outfile):
    pass
