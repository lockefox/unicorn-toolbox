#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is used to create the package we'll publish to PyPI.
.. currentmodule:: setup.py
.. moduleauthor:: John <jpurcell.ee@gmail.com>
"""


from pathlib import Path
from setuptools import setup, find_namespace_packages
from codecs import open  # Use a consistent encoding.
from pathlib import Path

__package_name__ = "unicorn-toolbox"
__library_name__ = "toolbox"
HERE = Path(__file__).resolve().parent

with open("README.md", "r", "utf-8") as f:
    __readme__ = f.read()

with open(HERE / "unicorn" / __library_name__ / "VERSION", "r", "utf-8") as f:
    __version__ = f.read().strip()

setup(
    name=__package_name__,
    description="CLI and python tools for homelab help",
    long_description=__readme__,
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    version=__version__,
    install_requires=[
        # Include dependencies here
        "plumbum",
        "requests[security]",
        "python-dotenv",
    ],
    extras_require={
        "dev": [
            "tox",
            "black",
            "sphinx",
        ]
    },
    package_data={"": ["README"], f"unicorn.{__library_name__}": ["VERSION",],},
    entry_points={
        "console_scripts": []
    },
    python_requires=">=3.6",
    license="Unlicense",
    author="John Purcell",
    author_email="jpurcell.ee@gmail.com",
    # Use the URL to the github repo.
    url=f"https://github.com/lockefox/{__package_name__}",
    download_url=(
        f"https://github.com/lockefox/" f"{__package_name__}/archive/{__version__}.tar.gz"
    ),
    keywords=[
        # TODO
    ],
    classifiers=[
        # TODO https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
    ],
    include_package_data=True,
)
