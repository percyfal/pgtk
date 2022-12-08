import os

import pytest
from click.testing import CliRunner

# import msprime
# from pytest import fixture

collect_ignore = ["setup.py"]


def pytest_addoption(parser):
    """
    Add options, e.g. to skip tests marked with `@pytest.mark.slow`
    """
    parser.addoption(
        "--skip-slow", action="store_true", default=False, help="Skip slow tests"
    )


def pytest_configure(config):
    """
    Add docs on the "slow" marker
    """
    config.addinivalue_line("markers", "slow: mark test as slow to run")
    pytest.dname = os.path.dirname(__file__)
    pytest.project = os.path.dirname(pytest.dname)


def pytest_collection_modifyitems(config, items):
    if config.getoption("--skip-slow"):
        skip_slow = pytest.mark.skip(reason="--skip-slow specified")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


@pytest.fixture(autouse=False)
def cd_tmp_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture(scope="function")
def runner(request):
    return CliRunner(mix_stderr=False)
