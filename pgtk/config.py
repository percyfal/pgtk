import dask.distributed


def init_dask_client(threads=1, workers=1):
    try:
        client = dask.distributed.Client(
            processes=False, n_workers=workers, threads_per_worker=threads
        )
        print(client)
    except Exception:
        raise
