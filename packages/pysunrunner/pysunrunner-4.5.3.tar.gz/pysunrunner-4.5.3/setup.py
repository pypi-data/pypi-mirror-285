#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="pysunrunner",
    version="4.5.3",
    packages=find_packages(),
    install_requires=[
        'numpy==2.0.0',
        'matplotlib==3.9.1',
        'scipy==1.14.0',
        'pillow==10.4.0',
    ],
    author="Jackson Riley (pyPLUTO routines by Dr. Bhargav Vaidya)",
    author_email="jriley@predsci.com",
    description="A package for imaging and plotting data from sunrunner simulations",
    url="https://github.com/BadOmen59/PySunRunner", 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

