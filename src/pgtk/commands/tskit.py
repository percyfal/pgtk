"""tskit utilities

"""
import logging
import os

import click
from pgtk.cli import CONTEXT_SETTINGS
from pgtk.cli import pass_environment
from pgtk.cli import pgtk_CLI

__shortname__ = __name__.split(".")[-1]

logger = logging.getLogger(__name__)


class pgtk_tools_CLI(pgtk_CLI):
    cmd_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, "tools", "tskit")
    )
    module = "pgtk.tools.tskit"


@click.command(
    cls=pgtk_tools_CLI, context_settings=CONTEXT_SETTINGS, help=__doc__, name="tools"
)
@pass_environment
def main(env):
    logger.debug(f"Running command {__shortname__}")
