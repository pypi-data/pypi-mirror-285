# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for generating sequences."""

import os

from setuptools import find_packages, setup

readme = open("README.rst").read()
history = open("CHANGES.rst").read()

tests_require = ["pytest-invenio>=1.4.0"]

extras_require = {
    "docs": [
        "Sphinx>=3",
    ],
    "mysql": [
        "invenio-db[mysql,versioning]>=1.0.0",
    ],
    "postgresql": [
        "invenio-db[postgresql,versioning]>=1.0.0",
    ],
    "sqlite": [
        "invenio-db[versioning]>=1.0.0",
    ],
    "admin": [
        "Flask-Admin>=1.5.6",
    ],
    "tests": tests_require,
}

extras_require["all"] = []
for name, reqs in extras_require.items():
    if name in ("mysql", "postgresql", "sqlite"):
        continue
    extras_require["all"].extend(reqs)

setup_requires = [
    "Babel>=1.3",
    "pytest-runner>=3.0.0,<5",
]

install_requires = [
    "sqlalchemy-utils>=0.31",
    "invenio-admin>=1.0.0",
    "invenio-base>=1.2.0",
    "invenio-db>=1.0.0",
    "invenio-i18n>=2.0.0",
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("invenio_sequencegenerator", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name="invenio-sequencegenerator",
    version=version,
    description=__doc__,
    long_description=readme + "\n\n" + history,
    keywords="invenio minter pidstore autoincrement",
    license="MIT",
    author="CERN",
    author_email="info@inveniosoftware.org",
    url="https://github.com/inveniosoftware/invenio-sequencegenerator",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    entry_points={
        "flask.commands": [
            "sequences = invenio_sequencegenerator.cli:sequences",
        ],
        "invenio_base.apps": [
            "invenio_sequencegenerator = "
            "invenio_sequencegenerator:InvenioSequenceGenerator",
        ],
        "invenio_i18n.translations": [
            "messages = invenio_sequencegenerator",
        ],
        "invenio_db.models": [
            "invenio_sequencegenerator = " "invenio_sequencegenerator.models",
        ],
        "invenio_admin.views": [
            "invenio_sequencegenerator_templatedefinition = "
            "invenio_sequencegenerator.admin:templatedefinition_adminview",
            "invenio_sequencegenerator_counter = "
            "invenio_sequencegenerator.admin:counter_adminview",
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Development Status :: 4 - Beta",
    ],
)
