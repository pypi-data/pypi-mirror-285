#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function

import os
from glob import glob
from os.path import join as pjoin

from jupyter_packaging import (
    combine_commands,
    create_cmdclass,
    ensure_targets,
    get_version,
    install_npm,
)
from setuptools import find_namespace_packages, setup

HERE = os.path.dirname(os.path.abspath(__file__))

with open("README.md") as f:
    readme = f.read()

# The name of the project
name = "foursquare.map-sdk"
# Directory as a tuple since we use namespace packaging
code_directory = ("foursquare", "map_sdk")

# Get the version
version = get_version(pjoin(*code_directory, "_version.py"))

# Representative files that should exist after a successful build
jstargets = [
    pjoin(HERE, *code_directory, "nbextension", "index.js"),
    pjoin(HERE, "lib", "plugin.js"),
]

package_data_spec = {name: ["nbextension/**js*", "labextension/**"]}

data_files_spec = [
    (
        "share/jupyter/nbextensions/foursquare/map_sdk",
        pjoin(*code_directory, "nbextension"),
        "**",
    ),
    # These are intended to be npm package name
    (
        "share/jupyter/labextensions/@foursquare/jupyter-map-sdk",
        pjoin(*code_directory, "labextension"),
        "**",
    ),
    ("share/jupyter/labextensions/@foursquare/jupyter-map-sdk", ".", "install.json"),
    ("etc/jupyter/nbconfig/notebook.d", ".", "foursquare.map_sdk.json"),
]

cmdclass = create_cmdclass(
    "jsdeps", package_data_spec=package_data_spec, data_files_spec=data_files_spec
)

cmdclass["jsdeps"] = combine_commands(
    install_npm(HERE, build_cmd="build:prod", npm=["yarn"]),
    ensure_targets(jstargets),
)

setup_args = dict(
    name=name,
    description="Jupyter Widget for Foursquare Studio Maps",
    long_description=readme,
    long_description_content_type="text/markdown",
    version=version,
    scripts=glob(pjoin("scripts", "*")),
    cmdclass=cmdclass,
    packages=find_namespace_packages(include=["foursquare.*"]),
    author="Foursquare Labs",
    author_email="info-studio@foursquare.com",
    license_files=("LICENSE.txt",),
    platforms="Linux, Mac OS X, Windows",
    keywords=["Jupyter", "Widgets", "IPython"],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: Jupyter",
    ],
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "geojson-pydantic==1.0.2",
        "ipykernel<6.18",
        "ipywidgets>=7.0.0,<8",
        "jinja2>=3,<4",
        "jupyter-ui-poll>=0.2.1,<0.3.0",
        "pydantic==2.6.3",
        "traitlets",
        "jupyterlab-widgets<=1.1.2",
        # pin this version until we fix it for newer versions
        "jupyterlab==3.2.9",
        # pin this version until we fix it for newer versions
        "jupyter-server==1.24.*",
        "glom==23.5.0",
        "",
    ],
    extras_require={
        "test": [
            "pytest<8.1",
            "pytest-cov",
            "pytest-snapshot",
            "pytest-mock",
            "nbval",
            "mypy==1.9.0",
            "jupyter_packaging",
            # This is the version used in ipywidgets ui tests https://github.com/jupyter-widgets/ipywidgets/blob/569ae06e53242c7f78790caf29a7e63ba1a06133/.github/workflows/tests.yml#L167
            "jupyterlab~=3.2",
            "pandas",
            "geopandas==0.10.2",
            "jupytext==1.13.6",
        ],
        "examples": [
            # Any requirements for the examples to run
        ],
        "docs": [
            "jupyter_sphinx",
            "nbsphinx",
            "nbsphinx-link",
            "pytest_check_links",
            "pypandoc",
            "recommonmark",
            "sphinx>=1.5",
            "sphinx_rtd_theme",
        ],
    },
    entry_points={},
)

if __name__ == "__main__":
    setup(**setup_args)
