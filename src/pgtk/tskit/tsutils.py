# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.9.5 (default, Jun  4 2021, 12:28:51)
# [GCC 7.5.0]
# Embedded file name: /domus/h1/perun/dev/pgtk/pgtk/tsutils.py
# Compiled at: 2021-10-21 23:28:55
# Size of source mod 2**32: 1219 bytes
import json

import pandas as pd
import tskit


def run_tsutils(args):
    if args.update_individual_metadata is not None:
        run_update_individual_metadata(args)


def run_update_individual_metadata(args):
    ts = tskit.load(args.ts)
    key = args.individual_metadata_key
    tc = ts.dump_tables()
    metadata = pd.read_table(args.update_individual_metadata)
    metadata.set_index([key], inplace=True)
    individuals = list(tc.individuals)
    tc.individuals.reset()
    for i, ind in enumerate(individuals):
        md = {}
        md_string = ind.metadata.decode()
        if md_string:
            md = json.loads(ind.metadata.decode())
        elif key in md.keys():
            x = metadata.loc[md[key]].to_dict()
            (md.update)(**x)
        else:
            if not bool(md):
                md = metadata.iloc[i].to_dict()
                md[key] = i
            else:
                x = metadata.iloc[i].to_dict()
                (md.update)(**x)
        ind = ind.replace(metadata=(json.dumps(md).encode()))
        tc.individuals.append(ind)

    tsout = tc.tree_sequence()
    tsout.dump(args.outfile)
