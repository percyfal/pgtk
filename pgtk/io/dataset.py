import pandas as pd
import xarray as xr
from sgkit.typing import PathType


def to_bed(ds: xr.Dataset, output: PathType) -> None:
    try:
        x = pd.DataFrame(
            [
                [ds.contigs[i] for i in ds.variant_contig.values],
                [str(i - 1) for i in ds.variant_position.values],
                [str(i) for i in ds.variant_position.values],
            ]
        ).T
    except Exception:
        raise
    print(f"converting dataset {repr(ds)} to {output}")
    x.to_csv(output, index=False, sep="\t", header=False)
