#!/usr/bin/env python
# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import io
import os

import setuptools


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return io.open(file_path, encoding="utf-8").read()


version = "0.0.2"

assert version


setuptools.setup(
    name="ai-models-fourcastnet-gfs",
    version=version,
    description="An ai-models plugin to run FourCastNet",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Jacob Radford",
    author_email="jacob.t.radford@gmail.com",
    license="Apache License Version 2.0",
    url="https://github.com/jacob-radford/ai-models-fourcastnet-gfs",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "torch>=2.0.0",
        "timm>=0.6.13",
        "einops>=0.6.0",
        "ruamel.yaml>=0.17.21",
    ],
    zip_safe=True,
    keywords="tool",
    entry_points={
        "ai_models_gfs.model": [
            "fourcastnet = ai_models_fourcastnet_gfs.model:model",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
    ],
)
