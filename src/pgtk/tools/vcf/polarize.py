"""Polarize vcf with respect to a haplotype in VCF file.

Use a haplotype from a reference individual (sample) in VCF as
reference and polarize all other entries with respect to haplotype.
Outputs repolarized vcf, potentially excluding the reference
individual.

"""
import copy
import logging
import sys
from datetime import datetime

import click
import cyvcf2
from pgtk.cli import pass_environment

logger = logging.getLogger(__name__)


@click.command(help=__doc__)
@click.argument("vcf", type=click.Path(exists=True))
@click.argument("output-file", type=click.Path())
@click.option(
    "--haplotype",
    help="haplotype to use",
    type=click.IntRange(
        1,
    ),
    default=1,
)
@click.option(
    "--reference-id",
    help="reference id to use for polarization. Defaults to first individual.",
    type=str,
    default=None,
)
@click.pass_context
@pass_environment
def main(env, ctx, vcf, output_file, haplotype, reference_id):
    vcf_fh = cyvcf2.VCF(vcf)
    if reference_id is None:
        reference_id = vcf_fh.samples[0]
    vcf_ref = cyvcf2.VCF(vcf, samples=reference_id)
    vcfwriter = cyvcf2.cyvcf2.Writer(output_file, vcf_fh, "w")
    vcfwriter.set_samples(vcf_fh.samples)
    vcfwriter.add_to_header(f"##{ctx.info_name}Version={env.version}")
    vcfwriter.add_to_header(
        f"##{ctx.info_name}Command={' '.join(sys.argv[1:])};"
        f"Date={datetime.now().ctime()}"
    )
    for gt, variant in zip(vcf_ref, vcf_fh):
        ref = gt.genotypes[0][0]
        if ref != 0:
            d = dict(enumerate(range(len(gt.ALT) + len(gt.REF))))
            # Map 0:ref and ref:0
            d[0] = ref
            d[ref] = 0
            for i in range(len(variant.genotypes)):
                alleles = variant.genotypes[i]
                variant.genotypes[i] = [
                    d[alleles[0]],
                    d[alleles[1]],
                    alleles[2],
                ]
            variant.genotypes = variant.genotypes
            variant.REF = variant.ALT[ref - 1]
            alt = copy.deepcopy(variant.ALT)
            alt[ref - 1] = gt.REF
            variant.ALT = alt
        vcfwriter.write_record(variant)
