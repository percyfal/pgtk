import multiprocessing
import pickle
from multiprocessing.pool import ThreadPool

import numpy as np
import pandas as pd
from pgtk.plotting.allel import plot_ld as make_plot_ld

try:
    import allel
except ImportError:
    raise


def run_pca(args):
    kwargs = dict(
        subsample=args.subsample,
        plot_ld=args.plot_ld,
        plot_ld_variants=args.plot_ld_variants,
        no_ld_prune=args.no_ld_prune,
        window_size=args.window_size,
        window_step=args.window_step,
        threshold=args.threshold,
        n_iter=args.n_iter,
        exclude=args.exclude,
    )
    fargs = ((vcf, *kwargs.values()) for vcf in args.vcfs)
    if args.threads > 1 and multiprocessing.cpu_count() > 1:
        pool = ThreadPool(args.threads)
        gnulist = pool.starmap(process_vcf, fargs)
        pool.close()
        pool.terminate()
    else:
        gnulist = []
        for vcf in args.vcfs:
            gnulist.append(process_vcf(vcf, **kwargs))
    if len(gnulist) > 1:
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


def process_vcf(
    vcf,
    subsample=None,
    plot_ld=False,
    plot_ld_variants=1000,
    no_ld_prune=False,
    window_size=500,
    window_step=250,
    threshold=0.1,
    n_iter=5,
    exclude=None,
):
    print(f"Processing file {vcf}\n")
    regions = allel.read_vcf(vcf, fields=["CHROM"])["variants/CHROM"]
    samples = allel.read_vcf_headers(vcf).samples
    if exclude is not None:
        samples = [s for s in samples if s not in exclude]

    for reg in np.unique(regions):
        print(f"Reading region {reg}\n")
        gn = load_genotypes(vcf, reg, samples=samples)
        if subsample is not None:
            if subsample < gn.shape[0]:
                vidx = np.random.choice(gn.shape[0], subsample, replace=False)
                vidx.sort()
                gnr = gn.take(vidx, axis=0)
                gn = gnr
        if plot_ld:
            make_plot_ld(
                gn,
                f"{reg}, {gn.shape[0]} sites",
                n=plot_ld_variants,
                filename=f"{vcf}.{reg}.ld.png",
            )
        if not no_ld_prune:
            gnu = ld_prune(
                gn,
                size=window_size,
                step=window_step,
                threshold=threshold,
                n_iter=n_iter,
            )
        else:
            gnu = gn
        if plot_ld:
            make_plot_ld(
                gnu,
                f"{reg} pruned, {gnu.shape[0]} sites",
                n=plot_ld_variants,
                filename=f"{vcf}.{reg}.ld.pruned.png",
            )
    return gnu


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


def load_genotypes(fn, region, samples):
    callset = allel.read_vcf(fn, region=region, samples=samples)
    g = allel.GenotypeChunkedArray(callset["calldata/GT"])
    ac = g.count_alleles()[:]
    flt = (ac.max_allele() == 1) & (ac[:, :2].min(axis=1) > 1)
    gf = g.compress(flt, axis=0)
    gn = gf.to_n_alt()
    print(f"loaded {gn.shape[0]} genotypes")
    return gn
