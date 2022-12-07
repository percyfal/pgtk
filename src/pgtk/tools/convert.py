"""Convert file formats

"""
import logging

import click
from pgtk.cli import pass_environment

logger = logging.getLogger(__name__)


@click.command(help=__doc__)
@click.argument("infile", type=click.Path())
@click.argument("outfile", type=click.Path())
@pass_environment
def cli(env, infile, outfile):
    pass
