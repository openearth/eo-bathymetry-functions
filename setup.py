import io
import os
import re

from setuptools import find_packages
from setuptools import setup

__version__ = '0.6.0'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="eo_bathymetry_functions",
    version=__version__,
    url="https://github.com/openearth/eo-bathymetry-functions",
    license='MIT',

    author="Jaap Langemeijer",
    author_email="jaaplangemeijer@gmail.com",

    description="Functions work with EO bathymetry.",
    long_description_content_type="text/markdown",
    long_description=long_description,

    packages=find_packages(exclude=('tests',)),

    install_requires=[
        "eepackages==0.17.0",
        "earthengine-api==0.1.317",
        "geojson>=2.5.0",
        "google-api-python-client>=1.12.8",
        "python-dateutil>=2.8.2",
    ],

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
    ],
)
