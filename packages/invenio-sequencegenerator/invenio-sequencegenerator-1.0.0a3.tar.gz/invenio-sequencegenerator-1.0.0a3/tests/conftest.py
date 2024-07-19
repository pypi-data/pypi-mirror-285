# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Pytest configuration."""

from __future__ import absolute_import, print_function

import pytest
from flask import Flask
from invenio_db import InvenioDB

from invenio_sequencegenerator.ext import InvenioSequenceGenerator


@pytest.fixture(scope='module')
def create_app():
    """Application factory fixture."""
    def factory(**config):
        app = Flask('testapp')
        app.config.update(**config)

        InvenioDB(app)
        InvenioSequenceGenerator(app)

        return app

    return factory
