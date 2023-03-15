#!/usr/bin/env python

from distutils.core import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="cdpdocs",
    version="0.1",
    description="cahier-de-prepa documents downloader",
    long_description=readme(),
    author="Alexis Rossfelder",
    author_email="contact.liteapplication@gmail.com",
    url="https://github.com/LiteApplication/cdpdocs",
    packages=["cdpdocs"],
    package_dir={"cdpdocs": "cdpdocs"},
    scripts=["cdpdocs/cdpdocs.py"],
)
