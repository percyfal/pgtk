"""Console script for pgtk based on click."""
import logging
import os
import pathlib

import click
from pgtk import decorators
from pgtk.env import Environment

from . import __version__

__author__ = "Per Unneberg"


logger = logging.getLogger(__name__)


PKG_DIR = pathlib.Path(__file__).absolute().parent
CONTEXT_SETTINGS = dict(auto_envvar_prefix="PGTK", show_default=True)

pass_environment = click.make_pass_decorator(Environment, ensure=True)


class pgtk_CLI(click.MultiCommand):
    module = "pgtk.commands"
    cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "commands"))

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(self.cmd_folder):
            if os.path.isdir(filename):
                continue
            if filename.endswith(".py") and not filename.startswith("__"):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            mod = __import__(f"{self.module}.{name}", None, None, ["main"])
        except ImportError:
            raise
            return
        return mod.main


@click.command(
    cls=pgtk_CLI, context_settings=CONTEXT_SETTINGS, help=__doc__, name="pgtk"
)
@click.version_option(version=__version__)
@decorators.debug_option()
@pass_environment
def cli(env):
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s [%(name)s:%(funcName)s]: %(message)s"
    )
    if env.debug:
        logging.getLogger().setLevel(logging.DEBUG)
