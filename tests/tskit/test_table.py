#!/usr/bin/env python3
import json

import pandas as pd
import pytest
from pgtk.tskit import table


@pytest.fixture
def metadata_ind():
    df = pd.DataFrame.from_dict(
        {"id": [0, 1, 2, 3], "foo": ["bar0", "bar1", "bar2", "bar3"]}
    )
    df.set_index(["id"], inplace=True)
    return df


@pytest.fixture
def tablerow(ts_ancestry_fixture):
    return list(ts_ancestry_fixture.dump_tables().individuals)[0]


def test_get_metadata(tablerow):
    assert table.get_metadata(tablerow) == {}


def test_update(tablerow, metadata_ind):
    md = table.update_metadata("id", 0, dict(), metadata_ind)
    assert md == {"id": 0, "foo": "bar0"}


def test_update_tablerow(ts_ancestry_fixture, metadata_ind):
    ts = table.update_tablerow_metadata(ts_ancestry_fixture, metadata_ind)
    md = list(ts.individuals())[0].metadata.decode()
    assert json.loads(md) == {"id": 0, "foo": "bar0"}
