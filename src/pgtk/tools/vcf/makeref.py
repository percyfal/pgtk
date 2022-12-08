"""Generate reference sequence from REF allele in VCF

Use the REF allele in VCF to generate reference sequence.
"""
import logging
import re
import textwrap
from dataclasses import dataclass
from random import choices

import click
import cyvcf2
import numpy as np
from pgtk.cli import pass_environment

logger = logging.getLogger(__name__)


class Sequence:
    def __init__(self, seq: str):
        seq = re.sub(r"[^a-zA-Z]", "", seq)
        self.seq = np.array([c for c in seq])

    def __setitem__(self, key, value):
        assert isinstance(key, int), "key must be integer"
        self.seq[key] = value

    def __getitem__(self, key):
        return self.seq[key]

    def __len__(self):
        return len(self.seq)

    def __str__(self):
        return "".join(self.seq)


@dataclass
class SeqRecord:
    id: str  # noqa
    seq: Sequence
    name: str = None
    desc: str = None
    haplotype: int = -1
    node: int = -1
    population: str = None

    @property
    def seqid(self):
        return f"{self.population}-{self.id}-{self.haplotype}"

    @property
    def description(self):
        if self.desc is not None:
            return self.desc
        return (
            f"id:{self.id}, node:{self.node}, name:{self.name}, "
            f"haplotype:{self.haplotype}, "
            f"population:{self.population}"
        )

    def __len__(self):
        return len(self.seq)

    def __str__(self):
        s = f">{self.id} {self.description}\n"
        s += "\n".join(
            textwrap.wrap(
                str(self.seq),
            )
        )
        return s

    def __repr__(self):
        return str(self)


@click.command(help=__doc__)
@click.argument("vcf", type=click.Path(exists=True))
@click.option(
    "--fasta-ref",
    "-f",
    help="reference sequence in fasta format",
    type=click.Path(exists=True),
)
@click.option(
    "--reference-id",
    help="sample id to use for polarization. Defaults to first individual",
)
@click.option("--output-file", "-o", type=click.Path())
@click.option("--description", help="contig description", type=str, default=None)
@pass_environment
@click.pass_context
def main(
    ctx,
    env,
    vcf,
    reference_id,
    fasta_ref,
    output_file,
    description,
):
    vcf_fh = cyvcf2.VCF(vcf)
    sequence_length = vcf_fh.seqlens[0]
    if reference_id is None:
        reference_id = vcf_fh.samples[0]
    if fasta_ref is not None:
        with open(fasta_ref) as fh:
            sid, desc = re.split(r"\s+", fh.readline().lstrip(">"), maxsplit=1)
            data = "".join([line.strip() for line in fh.readlines()])
            ref = SeqRecord(id=sid, desc=desc, seq=Sequence(data))
    else:
        dna = ["A", "C", "G", "T"]
        seq = choices(dna, k=int(sequence_length))
        ref = SeqRecord(id=1, desc=description, seq=Sequence("".join(seq)))

    if len(ref) != sequence_length:
        raise ValueError("reference must be same length as vcf sequence")

    for gt in vcf_fh:
        ref.seq[gt.POS - 1] = gt.REF
        if ref.id != gt.CHROM:
            ref.id = gt.CHROM
    if output_file is not None:
        with open(output_file, "w") as fh:
            fh.write(str(ref))
            fh.write("\n")
    else:
        print(ref)
