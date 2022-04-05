import pickle

import numpy as np
import pandas as pd
from pgtk.plotting.allel import plot_ld

try:
    import allel
except ImportError:
    raise


def run_pca(args):
    gnulist = []
    for vcf in args.vcfs:
        print(f"Processing file {vcf}\n")
        regions = allel.read_vcf(vcf)["variants/CHROM"]
        for reg in np.unique(regions):
            print(f"Reading region {reg}\n")
            gn = load_genotypes(vcf, reg)
            if args.subsample is not None:
                if args.subsample < gn.shape[0]:
                    vidx = np.random.choice(gn.shape[0], args.subsample, replace=False)
                    vidx.sort()
                    gnr = gn.take(vidx, axis=0)
                    gn = gnr
            if args.plot_ld:
                plot_ld(
                    gn,
                    f"{reg} ({vcf})",
                    n=args.plot_ld_variants,
                    filename=f"{vcf}.{reg}.ld.png",
                )
            gnu = ld_prune(
                gn,
                size=args.window_size,
                step=args.window_step,
                threshold=args.threshold,
                n_iter=args.iter,
            )
            if args.plot_ld:
                plot_ld(
                    gnu,
                    f"{reg} pruned ({vcf})",
                    n=args.plot_ld_variants,
                    filename=f"{vcf}.{reg}.ld.pruned.png",
                )
            gnulist.append(gnu)
    if len(gnulist) > 0:
        genotype_data = gnulist[0].concatenate(gnulist[1:])
    else:
        genotype_data = gnulist[0]
    coords, model = allel.pca(
        genotype_data[:], n_components=args.components, scaler=args.scaler
    )
    df_coords = pd.DataFrame(coords)
    df_coords.columns = map(lambda x: f"PC{x}", range(args.components))
    if args.output_prefix:
        with open(f"{args.output_prefix}.model.pickle", "wb") as fh:
            pickle.dump(model, fh)
        with open(f"{args.output_prefix}.coords.tsv", "w") as fh:
            df_coords.to_csv(fh, sep="\t", index=False)
    else:
        print(df_coords)


def ld_prune(gn, size, step, threshold=0.1, n_iter=1):
    for i in range(n_iter):
        loc_unlinked = allel.locate_unlinked(
            gn, size=size, step=step, threshold=threshold
        )
        n = np.count_nonzero(loc_unlinked)
        n_remove = gn.shape[0] - n
        print(
            "ld_prune: iteration",
            i + 1,
            "retaining",
            n,
            "removing",
            n_remove,
            "variants",
        )
        gn = gn.compress(loc_unlinked, axis=0)
        if n_remove == 0:
            print(f"ld pruning has converged after {i+1} iterations; quitting")
            break
    return gn


def load_genotypes(fn, region):
    callset = allel.read_vcf(fn, region=region)
    g = allel.GenotypeChunkedArray(callset["calldata/GT"])
    ac = g.count_alleles()[:]
    flt = (ac.max_allele() == 1) & (ac[:, :2].min(axis=1) > 1)
    gf = g.compress(flt, axis=0)
    gn = gf.to_n_alt()
    print(f"loaded {gn.shape[0]} genotypes")
    return gn
