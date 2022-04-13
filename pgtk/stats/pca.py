import multiprocessing
import pickle
from multiprocessing.pool import ThreadPool

import pandas as pd

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


def process_vcf():
    pass
