import dask.distributed


def init_dask_client(threads=1, workers=1, threads_per_worker=None):
    if threads_per_worker is None:
        threads_per_worker = int(threads / workers)
    try:
        client = dask.distributed.Client(
            n_workers=workers,
            threads_per_worker=threads_per_worker,
            asynchronous=True,
            processes=False,
        )
    except Exception:
        raise
    return client
