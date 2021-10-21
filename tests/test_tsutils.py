#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def test_metadata(ts_ancestry_fixture):
    print(ts_ancestry_fixture)
    print(list(ts_ancestry_fixture.individuals()))
