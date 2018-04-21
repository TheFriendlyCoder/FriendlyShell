#!/usr/bin/env python
"""Packaging script"""
import os
from setuptools import setup, find_packages


def check_tag_name(tag_name):
    """Ensures the name of the current SCM tag is correctly formatted

    Tag should represent a version number of the form X.Y.Z

    :returns: True if the tag name satisfies the expected format, false if not
    """

    parts = tag_name.split(".")
    if len(parts) != 3:
        return False

    for cur_digit in parts:
        if not cur_digit.isdigit():
            return False

    return True


def get_version_number():
    """Retrieves the version number for a project"""

    # If we are building from a tag using Travis-CI,
    # set our version number to the tag name
    if 'TRAVIS_TAG' in os.environ and not os.environ['TRAVIS_TAG'] == '':
        if not check_tag_name(os.environ['TRAVIS_TAG']):
            raise Exception(
                "Invalid tag name {0}. Must be of the form 'X.Y.Z'".format(
                    os.environ['TRAVIS_TAG']))
        return os.environ['TRAVIS_TAG']

    # if we get here we know we're building a pre-release version
    # so we set a fake version as a place holder
    retval = "0.0"

    # If we are building from a branch using Travis-CI,
    # append the build number so we know where the package came from
    if 'TRAVIS_BUILD_NUMBER' in os.environ:
        retval += "." + os.environ['TRAVIS_BUILD_NUMBER']
    else:
        retval += ".0"

    # Pre release versions need a non-numeric suffix on the version number
    retval += ".dev0"

    return retval


setup(
    name='friendlyshell',
    version=get_version_number(),
    author='Kevin S. Phillips',
    author_email='kevin@thefriendlycoder.com',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    description="Framework for writing interactive Python command line "
                "interfaces, similar to the 'cmd' built in class.",
    long_description=open('README.rst').read(),
    url='https://github.com/TheFriendlyCoder/FriendlyShell',
    install_requires=['pyparsing', 'tabulate'],
    keywords='cmd command line shell interactive interpreter',
    license="GPL",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: "
        "GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Microsoft",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries"
    ]
)
