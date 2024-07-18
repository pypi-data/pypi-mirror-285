#!/usr/bin/env python

import re
import setuptools
from setuptools import find_packages

version = ""
with open('migration_db/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="migration_db",
    version=version,
    author="xiaodong.li",
    author_email="",
    description="Migrate database files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://example.com",
    install_requires=[
        'lxml>=4.8.0',
        'redis>=4.3.1',
        'jinja2>=3.1.2',
        'mysql-connector-python>=8.3.0',
        'slicing>=1.0.6',
        'GitPython>=3.1.32',
        'werkzeug>=3.0.1',
    ],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.9",
    ],
    include_package_data=True,
)