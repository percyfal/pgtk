from pathlib import Path
from typing import Optional

from sgkit.io import vcf as sgvcf
from sgkit.typing import PathType


def convert_vcf_to_zarr(path: PathType, tmpdir: Optional[PathType] = None) -> PathType:
    output = Path(f"{path}.zarr")
    if tmpdir is not None:
        if isinstance(tmpdir, str):
            tmpdir = Path(tmpdir)
        output = tmpdir.joinpath(output.name)
    print(f"converting {path} to {output}...")
    sgvcf.vcf_to_zarr(path, output)
    return output
