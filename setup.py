#!/usr/bin/env python
from setuptools import setup, find_packages

# Dynamically generate a list of sub-modules to be packaged with the project
# Always exclude unit test modules from the package
_packages = find_packages(exclude=['tests', 'tests.*'])

setup(
    name='friendlyshell',
    version='0.0.1',
    author='Kevin S. Phillips',
    author_email='thefriendlycoder@gmail.com',
    packages=_packages,
    description='Replacement for "cmd" built-in library with enhanced functionality',
    url='',
    install_requires=['pyparsing', 'tabulate'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Microsoft",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5"
    ]
)
