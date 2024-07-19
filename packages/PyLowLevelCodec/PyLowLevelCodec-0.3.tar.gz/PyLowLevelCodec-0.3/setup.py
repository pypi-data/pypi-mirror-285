import sys
import os

from pkg_resources import VersionConflict, require
from setuptools import setup, find_packages

try:
    require("setuptools>=42")
except VersionConflict:
    print("Error: version of setuptools is too old (<42)!")
    sys.exit(1)


if __name__ == "__main__":
    setup(
        name='PyLowLevelCodec',
        version='0.3',
        description='PyLowLevelCodec is vastai Python based video codec library for hardware accelerated video encode and decode on vastai device.',
        author='Fanxum',
        author_email='fanxu.meng@vastaitech.com',
        packages=find_packages(),
        install_requires=[' '],
    python_requires='>=3.10',
)