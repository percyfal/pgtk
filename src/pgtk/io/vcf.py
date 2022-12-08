import logging
import tempfile
from pathlib import Path
from typing import Optional

from sgkit.io import vcf as sgvcf
from sgkit.typing import PathType


__shortname__ = __name__.split(".")[-1]

logger = logging.getLogger(__name__)


def convert_vcf_to_zarr(path: PathType, tmpdir: Optional[PathType] = None) -> PathType:
    output = Path(f"{path}.zarr")
    if tmpdir is not None:
        if isinstance(tmpdir, str):
            tmpdir = Path(tmpdir)
        elif isinstance(tmpdir, tempfile.TemporaryDirectory):
            tmpdir = Path(tmpdir.name)
        output = tmpdir.joinpath(output.name)
    logger.info(f"converting {path} to {output}...")
    sgvcf.vcf_to_zarr(path, output)
    return output
