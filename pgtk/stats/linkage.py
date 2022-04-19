# import multiprocessing
import re

import numpy as np
from pgtk.io.dataset import to_bed
from pgtk.io.vcf import convert_vcf_to_zarr
from pgtk.plotting.allel import plot_ld as make_plot_ld

# from multiprocessing.pool import ThreadPool

try:
    import allel
except ImportError:
    raise


def run_ld_prune(args):
    kwargs = dict(
        subsample=args.subsample,
        plot_ld=args.plot_ld,
        plot_ld_variants=args.plot_ld_variants,
        window_size=args.window_size,
        window_step=args.window_step,
        threshold=args.threshold,
        n_iter=args.n_iter,
        exclude=args.exclude,
        output_suffix=args.output_suffix,
        tmp=args.tmp,
        as_bed=args.as_bed,
    )
    if args.stats_backend == "sgkit":
        try:
            from dask.distributed import LocalCluster, Client

            cluster = LocalCluster(threads_per_worker=1, n_workers=args.threads)
            client = Client(cluster)
            print(client)
        except Exception:
            raise
        _ld_prune = _ld_prune_sgkit
        for vcf in args.vcfs:
            zarrdata = convert_vcf_to_zarr(vcf, tmpdir=args.tmp)
            _ld_prune(zarrdata, **kwargs)

    elif args.stats_backend == "allel":
        _ld_prune = _ld_prune_allel
        # inputs = args.vcf

    # fargs = ((vcf, *kwa crgs.values()) for vcf in args.vcfs)
    # if args.threads > 1 and multiprocessing.cpu_count() > 1:
    #     pool = ThreadPool(args.threads)
    #     bedlist = pool.starmap(_ld_prune, fargs)
    #     pool.close()
    #     pool.terminate()
    # else:
    #     bedlist = []
    #     for vcf in args.vcfs:
    #         bedlist.append(_ld_prune(vcf, **kwargs))


def _ld_prune_sgkit(
    zarrdata,
    *,
    subsample=None,
    plot_ld=False,
    plot_ld_variants=1000,
    window_size=500,
    window_step=250,
    threshold=0.1,
    n_iter=5,
    exclude=None,
    output_suffix=None,
    tmp=None,
    as_bed=False,
):
    try:
        import sgkit as sg
    except ImportError:
        raise
    print("loading dataset...")
    ds = sg.load_dataset(zarrdata)
    # For rechunking
    original_chunk_size = ds.chunks["variants"][0]
    ds["dosage"] = ds["call_genotype"].sum(dim="ploidy")
    ds = sg.window_by_variant(ds, size=window_size, step=window_step)
    # Possibly plot before here

    print("pruning by ld...")
    for i in range(n_iter):
        n_start = len(ds.variants)
        ds = sg.ld_prune(ds, threshold=threshold)
        n_retain = len(ds.variants)
        n_remove = n_start - n_retain
        print(
            f"ld_prune_sgkit: iteration {i + 1}; retaining {n_retain}, "
            f"removing {n_remove}"
        )
        if n_remove == 0:
            print(f"ld pruning has converged after {i+1} iterations; quitting")
            break
        ds = ds.drop_vars(["window_contig", "window_start", "window_stop"])
        ds = sg.window_by_variant(ds, size=window_size, step=window_step)
    # Plot after

    # Save dataset
    re_zarr = re.compile("(.zarr)$")
    output = re_zarr.sub(f"{output_suffix}.zarr", str(zarrdata))
    ds.chunk(original_chunk_size)

    try:
        ds["variant_id"] = ds.variant_id.astype(str)
        ds["variant_allele"] = ds.variant_allele.astype(str)
        ds["sample_id"] = ds.sample_id.astype(str)
        sg.save_dataset(ds, output, mode="w")
    except Exception as e:
        print(e)
        raise
    if as_bed:
        bedout = re_zarr.sub(".bed", output)
        to_bed(ds, bedout)


def _ld_prune_allel(
    vcf,
    *,
    subsample=None,
    plot_ld=False,
    plot_ld_variants=1000,
    no_ld_prune=False,
    window_size=500,
    window_step=250,
    threshold=0.1,
    n_iter=5,
    exclude=None,
    **kwargs,
):
    print(f"Processing file {vcf}\n")
    regions = allel.read_vcf(vcf, fields=["CHROM"])["variants/CHROM"]
    samples = allel.read_vcf_headers(vcf).samples
    if exclude is not None:
        samples = [s for s in samples if s not in exclude]

    for reg in np.unique(regions):
        print(f"Reading region {reg}\n")
        gf = load_genotypes(vcf, reg, samples=samples)
        gn = gf.to_n_alt()
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
    g = allel.GenotypeDaskArray(callset["calldata/GT"])
    ac = g.count_alleles()[:]
    flt = (ac.max_allele() == 1) & (ac[:, :2].min(axis=1) > 1)
    gf = g.compress(flt, axis=0)
    return gf


# def _run_ld_prune_allel(args):


#     kwargs = dict(
#         subsample=args.subsample,
#         plot_ld=args.plot_ld,
#         plot_ld_variants=args.plot_ld_variants,
#         window_size=args.window_size,
#         window_step=args.window_step,
#         threshold=args.threshold,
#         n_iter=args.n_iter,
#         exclude=args.exclude,
#     )
#     fargs = ((vcf, *kwargs.values()) for vcf in args.vcfs)
#     if args.threads > 1 and multiprocessing.cpu_count() > 1:
#         pool = ThreadPool(args.threads)
#         gnulist = pool.starmap(process_vcf, fargs)
#         pool.close()
#         pool.terminate()
#     else:
#         gnulist = []
#         for vcf in args.vcfs:
#             gnulist.append(process_vcf(vcf, **kwargs))
#     if len(gnulist) > 1:
#         genotype_data = gnulist[0].concatenate(gnulist[1:])
#     else:
#         genotype_data = gnulist[0]
#     print(dir(genotype_data))
#     import sys

# print(allel.write_vcf(sys.stdout, genotype_data))
# for g in genotype_data:
#     print(g)
# print(dir(g), type(g))
# print(dir(genotype_data), type(genotype_data))
# print(genotype_data.chunks)
