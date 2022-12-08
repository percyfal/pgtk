import os.path

import pytest
from pgtk.tools.vcf.polarize import main

VCF_SMALL = os.path.join(pytest.project, "tests", "data", "ooa.chr21.small.vcf")


@pytest.fixture
def vcf_small():
    pass


def test_polarize(runner, cd_tmp_path):
    """Test"""
    p = cd_tmp_path / "polarize.vcf"
    results = runner.invoke(main, [VCF_SMALL, p.name])
    assert not results.exception
    data = [d.split("\t") for d in p.read_text().split("\n") if not d.startswith("#")]

    # First case
    assert data[0][3] == "G"
    assert data[0][4] == "A,C"
    assert data[0][9] == "0|1"
    assert data[0][10] == "0|0"
    assert data[0][11] == "1|2"

    # Second case
    assert data[1][3] == "A"
    assert data[1][4] == "G"
    assert data[1][9] == "0|0"
    assert data[1][10] == "0|0"
    assert data[1][11] == "1|1"

    # Third case
    assert data[2][3] == "A"
    assert data[2][4] == "C,T"
    assert data[2][9] == "0|0"
    assert data[2][10] == "1|2"
    assert data[2][11] == "0|1"

    # Fourth case
    assert data[3][3] == "A"
    assert data[3][4] == "T"
    assert data[3][9] == "0|0"
    assert data[3][10] == "0|0"
    assert data[3][11] == "0|0"

    # Fifth case
    assert data[4][3] == "T"
    assert data[4][4] == "A,G,C"
    assert data[4][9] == "0|1"
    assert data[4][10] == "2|0"
    assert data[4][11] == "3|1"
