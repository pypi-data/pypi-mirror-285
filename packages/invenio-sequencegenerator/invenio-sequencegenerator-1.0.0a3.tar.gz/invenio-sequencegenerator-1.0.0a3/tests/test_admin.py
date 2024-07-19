# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Test admin view."""

from __future__ import absolute_import, print_function

from flask import current_app, url_for
from flask_admin import Admin

from invenio_sequencegenerator.admin import counter_adminview as ca
from invenio_sequencegenerator.admin import templatedefinition_adminview as ta
from invenio_sequencegenerator.api import Sequence, Template


def test_admin(db):
    """Test admin interface."""
    assert isinstance(ca, dict)
    assert isinstance(ta, dict)

    assert 'model' in ca
    assert 'modelview' in ca
    assert 'model' in ta
    assert 'modelview' in ta

    # Create admin
    admin = Admin(current_app, name='Example: Sequence Generator')

    # Add views
    admin.add_view(ta['modelview'](ta['model'], db.session))
    admin.add_view(ca['modelview'](ca['model'], db.session))

    # Create test data
    seq = Sequence(Template.create('ID', 'File {counter}'))
    assert seq.next() == 'File 0'
    assert seq.next() == 'File 1'
    assert seq.next() == 'File 2'
    db.session.commit()

    with current_app.test_request_context():
        request_url = url_for('counter.reset_view')
    with current_app.test_client() as client:
        # Reset counter
        client.post(request_url,
                    data={'start': 0, 'rowid': 'File {counter}'},
                    follow_redirects=False)

    # Assert that reset was successful
    assert seq.next() == 'File 0'
