#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import tskit
import pandas as pd


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
    ind_table = tskit.IndividualTable()
    for i, ind in enumerate(individuals):
        md = {}
        md_string = ind.metadata.decode()
        if md_string:
            md = json.loads(ind.metadata.decode())
        if key in md.keys():
            x = metadata.loc[md[key]].to_dict()
            md.update(**x)
        # Assume metadata keys are in order
        elif not bool(md):
            md = metadata.iloc[i].to_dict()
        else:
            x = metadata.iloc[i].to_dict()
            md.update(**x)
        ind = ind.replace(metadata=json.dumps(md).encode())
        tc.individuals.append(ind)
    tsout = tc.tree_sequence()
    tsout.dump(args.outfile)
