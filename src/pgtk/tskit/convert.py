import numpy as np
from sgkit import (
    create_genotype_call_dataset,
)
from sgkit.typing import ArrayLike


# See sgkit.tests.test_popgen
def ts_to_sgkit_dataset(
    ts,
    contig_id="1",
    chunks=None,
    ploidy=2,
    samples=None,
    individuals=None,
    populations=None,
):
    """Convert tskit tree sequence into an sgkit dataset.

    Based on sgkit.tests.test_popgen.ts_to_dataset
    """
    if samples is None:
        samples = ts.samples()
    if populations is not None:
        popind = [
            pop.id
            for pop in ts.populations()
            if pop.metadata.get("name", None) in populations
        ]
        individuals = [
            i for i, ind in enumerate(ts.individual_populations) if ind in popind
        ]
        samples = [n for i in individuals for n in ts.individual(i).nodes]
    if individuals is None:
        individuals = list(set(ts.nodes_individual[samples]))
    nind = len(individuals)
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
        variant_contig_names=[contig_id],
        variant_contig=np.zeros(len(tables.sites), dtype=int),
        variant_position=tables.sites.position.astype(int),
        variant_allele=alleles,
        sample_id=np.array([f"tsk_{u}" for u in individuals]).astype("U"),
        call_genotype=genotypes,
    )
    ds["sample_cohort"] = ts.individuals_population[individuals]
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
