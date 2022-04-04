import numpy as np
import pandas as pd
import tskit
from bokeh.io import output_file
from bokeh.io import show
from pgtk.plotting.stats import windowed_plot


def make_windows(windowsize, stop, start=0.0):
    if windowsize is None:
        return None
    return np.concatenate(
        (np.arange(start, float(stop), float(windowsize)), [float(stop)])
    )


def run_tskit_stats(args):
    for tsfile in args.tree_sequence:
        ts = tskit.load(tsfile)
        results = pd.DataFrame()
        windows = make_windows(args.window_size, stop=ts.sequence_length)
        if windows is not None:
            results["windows"] = windows[:-1]
        else:
            results["windows"] = [0.0]
        for statistic in args.statistic:
            try:
                statmethod = getattr(ts, statistic)
            except AttributeError:
                raise NotImplementedError(f"no such statistic {statistic}")
            try:
                data = statmethod(
                    sample_sets=args.sample_sets,
                    windows=windows,
                    mode=args.mode,
                    span_normalise=args.span_normalise,
                )
            except Exception:
                pass
            try:
                data = statmethod(
                    sample_sets=args.sample_sets, windows=windows, mode=args.mode
                )
            except Exception:
                pass
            results[statistic] = data
        p = windowed_plot(results)
        output_file(filename="tabort.html")
        show(p)
