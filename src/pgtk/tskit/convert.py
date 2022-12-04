import numpy as np
from sgkit import (
    create_genotype_call_dataset,
)
from sgkit.typing import ArrayLike


# See sgkit.tests.test_popgen
def ts_to_sgkit_dataset(ts, contig_id="1", chunks=None, samples=None, ploidy=2):
    """Convert tskit tree sequence into an sgkit dataset.

    Based on sgkit.tests.test_popgen.ts_to_dataset
    """
    if samples is None:
        samples = ts.samples()
    nind = int(len(samples) / 2)
    tables = ts.dump_tables()
    alleles = []
    genotypes = []
    max_alleles = 0
    for var in ts.variants(samples=samples):
        alleles.append(var.alleles)
        max_alleles = max(max_alleles, len(var.alleles))
        genotypes.append(var.genotypes)
    padded_alleles = [
        list(site_alleles) + [""] * (max_alleles - len(site_alleles))
        for site_alleles in alleles
    ]
    alleles: ArrayLike = np.array(padded_alleles).astype("S")
    genotypes = np.expand_dims(genotypes, axis=2)
    # Shape DIM_VARIANT, DIM_SAMPLE, DIM_PLOIDY
    genotypes = np.reshape(genotypes, (len(genotypes), nind, ploidy))

    ds = create_genotype_call_dataset(
        variant_contig_names=["1"],
        variant_contig=np.zeros(len(tables.sites), dtype=int),
        variant_position=tables.sites.position.astype(int),
        variant_allele=alleles,
        sample_id=np.array([f"tsk_{u}" for u in np.arange(nind)]).astype("U"),
        call_genotype=genotypes,
    )
    ds["sample_cohort"] = ts.individuals_population
    ds = ds.assign(
        {
            "cohorts": [
                pop.metadata.get("id", pop.metadata.get("name", None))
                for pop in ts.populations()
            ]
        }
    )

    if chunks is not None:
        ds = ds.chunk(dict(zip(["variants", "samples"], chunks)))
    return ds
