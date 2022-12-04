"""Polarize vcf with respect to a haplotype in VCF file.

Use a haplotype from a reference individual (sample) in VCF as
reference and polarize all other entries with respect to haplotype.
Outputs repolarized vcf, potentially excluding the reference
individual.

"""
import logging

import click
from pgtk.cli import pass_environment

logger = logging.getLogger(__name__)


@click.command(help=__doc__)
@click.argument("vcf", type=click.Path())
@click.argument("output-file", type=click.File("w"))
@pass_environment
def cli(env, vcf, output_file):
    output_file.write(str(vcf))
    output_file.write("\n")
