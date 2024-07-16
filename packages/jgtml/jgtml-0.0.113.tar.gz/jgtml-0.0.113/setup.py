#!/usr/bin/env Python
"""
jgtml
"""

from setuptools import find_packages, setup

#from jgtml import __version__ as version
def read_version():
    with open("jgtml/__init__.py") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.strip().split()[-1][1:-1]

version = read_version()


setup(
    name="jgtml",
    version=version,
    description="JGTrading Data maker' Dataframes",
    long_description=open("README.rst").read(),
    author="GUillaume Isabelle",
    author_email="jgi@jgwill.com",
    url="https://github.com/jgwill/jgtml",
    packages=find_packages(include=["jgtml"], exclude=["*test*"]),

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.7.16",
    ],
)
