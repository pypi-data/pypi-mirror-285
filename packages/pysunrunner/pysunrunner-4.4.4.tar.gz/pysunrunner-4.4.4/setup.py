#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="pysunrunner",
    version="4.4.4",
    packages=find_packages(),
    install_requires=[
        'numpy==2.0.0',
        'matplotlib==3.9.1',
        'scipy==1.14.0',
        'pillow==10.4.0',
    ],
    author="Bhargav Vaidya",
    author_email="bvaidya@iiti.ac.in",
    description="A package for imaging and plotting data from PLUTO simulations",
    url="https://github.com/BadOmen59/PySunRunner", 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

