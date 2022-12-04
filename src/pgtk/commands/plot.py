"""plotting utilities

"""
import logging

import click
from pgtk.cli import pass_environment

__shortname__ = __name__.split(".")[-1]

logger = logging.getLogger(__name__)


@click.group(help=__doc__, name=__shortname__)
@pass_environment
def main(env):
    logger.debug(f"Running command {__shortname__}")
