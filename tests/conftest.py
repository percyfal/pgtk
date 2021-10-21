#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import msprime
import numpy as np
import pytest


@pytest.fixture(scope="session")
def ts_ancestry_fixture():
    ts = msprime.sim_ancestry(4, random_seed=42)
    return ts
