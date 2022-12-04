"""Common arguments for click commands"""
import click

tsfile = click.argument("tsfile", type=click.Path())
