import warnings
from typing import Hashable
from typing import Optional

import numpy as np
from numcodecs import PackBits
from pgtk.config import init_dask_client
from xarray import Dataset

try:
    import sgkit as sg
except ImportError:
    raise

try:
    from numcodecs import Blosc

    DEFAULT_COMPRESSOR = Blosc(cname="zstd", clevel=7, shuffle=Blosc.AUTOSHUFFLE)
except ImportError:  # pragma: no cover
    warnings.warn("Cannot import Blosc, falling back to no compression", RuntimeWarning)
    DEFAULT_COMPRESSOR = None


def encode(ds: Dataset, encoding: Optional[dict] = None):
    chunk_width = 1_000
    chunk_length = 10_000
    compressor = DEFAULT_COMPRESSOR

    def get_chunk_size(dim: Hashable, size: int) -> int:
        if dim == "variants":
            return chunk_length
        elif dim == "samples":
            return chunk_width
        else:
            return size

    default_encoding = {}
    for var in ds.data_vars:
        var_chunks = tuple(
            get_chunk_size(dim, size)
            for (dim, size) in zip(ds[var].dims, ds[var].shape)
        )
        default_encoding[var] = dict(chunks=var_chunks, compressor=compressor)
        if ds[var].dtype.kind == "b":
            # ensure that booleans are not stored as int8 by xarray
            # https://github.com/pydata/xarray/issues/4386
            ds[var].attrs["dtype"] = "bool"
            default_encoding[var]["filters"] = [PackBits()]

    # values from function args (encoding) take precedence over default_encoding
    encoding = encoding or {}
    merged_encoding = {**default_encoding, **encoding}
    return merged_encoding


def run_pca(args):
    init_dask_client(args.threads)
    print(f"Loading dataset {args.zarr}")
    ds = sg.load_dataset(args.zarr)
    original_chunk_size = ds.chunks["variants"][0]

    nvar = len(ds.variants)
    if args.subsample is not None:
        print("subsampling ", args.subsample, " variants")
        ds = ds.isel(
            variants=sorted(np.random.choice(nvar, args.subsample, replace=False))
        )
    if args.subsample_fraction is not None:
        nchoice = int(args.subsample_fraction * nvar)
        print("subsampling ", nchoice, " variants")
        ds = ds.isel(variants=sorted(np.random.choice(nvar, nchoice, replace=False)))
    if args.exclude is not None:
        print("excluding samples", ", ".join(args.exclude))
        keep = ~np.isin(ds.sample_id.values, args.exclude)
        ds = ds.isel(samples=keep)

    ds = sg.variant_stats(ds)

    ds = ds.assign(**ds[["variant_allele_frequency"]].compute()).pipe(
        lambda ds: ds.sel(variants=(ds.variant_allele_frequency[:, 1] > 0.01))
    )
    ds = ds.chunk(original_chunk_size)

    ds_pca = sg.stats.pca.count_call_alternate_alleles(ds)
    variant_mask = ((ds_pca.call_alternate_allele_count < 0).any(dim="samples")) | (
        ds_pca.call_alternate_allele_count.std(dim="samples") <= 0.0
    )
    ds_pca = ds_pca.sel(variants=~variant_mask)
    ds_pca["call_alternate_allele_count"] = ds_pca.call_alternate_allele_count.chunk(
        (None, -1)
    )
    ds_pca = sg.pca(ds_pca, n_components=args.components)

    sg.save_dataset(ds_pca, args.output_file, encoding=encode(ds_pca), mode="w")
