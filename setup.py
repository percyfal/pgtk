#!/usr/bin/env python
"""The setup script."""
from setuptools import find_packages
from setuptools import setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "bokeh",
    "numpy",
    "daiquiri",
]

test_requirements = [
    "pytest>=3",
]

setup(
    author="Per Unneberg",
    author_email="per.unneberg@scilifelab.se",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="Population genomics toolkit",
    entry_points={
        "console_scripts": [
            "pgtk=pgtk.cli.main:main",
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="pgtk",
    name="pgtk",
    packages=find_packages(include=["pgtk", "pgtk.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/percyfal/pgtk",
    version="0.1.0",
    zip_safe=False,
    use_scm_version={"write_to": "pgtk/_version.py"},
)
