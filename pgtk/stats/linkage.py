import re

import numpy as np
from pgtk.config import init_dask_client
from pgtk.io.dataset import to_bed
from pgtk.io.vcf import convert_vcf_to_zarr


def run_ld_prune(args):
    kwargs = dict(
        subsample=args.subsample,
        subsample_fraction=args.subsample_fraction,
        plot_ld=args.plot_ld,
        plot_ld_variants=args.plot_ld_variants,
        window_size=args.window_size,
        window_step=args.window_step,
        threshold=args.threshold,
        n_iter=args.n_iter,
        exclude=args.exclude,
        output_suffix=args.output_suffix,
        as_bed=args.as_bed,
    )
    init_dask_client(args.threads)
    for vcf in args.vcfs:
        zarrdata = convert_vcf_to_zarr(vcf, tmpdir=args.tmpdir)
        _ld_prune(zarrdata, **kwargs)


def _ld_prune(
    zarrdata,
    *,
    subsample=None,
    subsample_fraction=None,
    plot_ld=False,
    plot_ld_variants=1000,
    window_size=500,
    window_step=250,
    threshold=0.1,
    n_iter=5,
    exclude=None,
    output_suffix=None,
    as_bed=False,
):
    try:
        import sgkit as sg
    except ImportError:
        raise
    print("loading dataset...")
    ds = sg.load_dataset(zarrdata)
    n = None
    if subsample is not None:
        n = subsample
    if subsample_fraction is not None:
        n = min(len(ds.variants), int(len(ds.variants) * subsample_fraction))
    if n is not None:
        vidx = sorted(np.random.choice(len(ds.variants), n, replace=False))
        print(f"subsetting dataset to {n} variants...")
        ds = ds.isel(variants=sorted(vidx))

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
    ds = ds.chunk(original_chunk_size)

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
