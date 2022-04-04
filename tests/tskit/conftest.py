#!/usr/bin/env python3
import msprime
from pytest import fixture


@fixture(scope="session")
def ts_ancestry_fixture():
    ts = msprime.sim_ancestry(4, random_seed=42)
    return ts
