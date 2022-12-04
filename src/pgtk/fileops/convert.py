from pgtk.config import init_dask_client
from pgtk.io.vcf import convert_vcf_to_zarr


def run_convert(args):
    # print(args)
    init_dask_client(threads_per_worker=args.threads, workers=args.workers)
    # with dask.config.set(scheduler="threads",
    # num_workers=args.workers, num_threads=args.threads):
    convert_vcf_to_zarr(args.vcf, args.tmpdir)
