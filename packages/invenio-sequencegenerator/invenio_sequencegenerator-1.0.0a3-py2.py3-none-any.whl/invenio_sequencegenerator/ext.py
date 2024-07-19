# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Flask extension for Invenio-SequenceGenerator."""

from __future__ import absolute_import, print_function

from flask import Blueprint


class InvenioSequenceGenerator(object):
    """Invenio-SequenceGenerator extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        app.extensions['invenio-sequencegenerator'] = self

        # Register dummy blueprint just for loading templates
        app.register_blueprint(Blueprint(
            'invenio_sequencegenerator', __name__, template_folder='templates')
        )
