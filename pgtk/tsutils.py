#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import tskit
import pandas as pd


def get_metadata(tablerow):
    md_string = tablerow.metadata.decode()
    if md_string:
        md = json.loads(x.metadata.decode())
    else:
        md = {}
    return md


def update_metadata(key, index, md, df):
    if key in md.keys():
        x = df.loc[md[key]].to_dict()
    elif not bool(md):
        x = df.iloc[index].to_dict()
        x[key] = index
    else:
        x = df.iloc[index].to_dict()
    md.update(**x)
    return md


def update_tablerow_metadata(ts, metadata, tablename="individuals", key="id"):
    tc = ts.dump_tables()
    tablerows = list(getattr(tc, tablename))
    getattr(tc, tablename).reset()
    for i, row in enumerate(tablerows):
        md = get_metadata(row)
        md = update_metadata(key, i, md, metadata)
        row = row.replace(metadata=json.dumps(md).encode())
        getattr(tc, tablename).append(row)
    return tc.tree_sequence()
