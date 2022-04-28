def run_concat(args):
    """Concatenate files"""
    if args.filetype == "zarr":
        _run_concat_zarr(args)
    else:
        pass


def _run_concat_zarr(args):
    pass
