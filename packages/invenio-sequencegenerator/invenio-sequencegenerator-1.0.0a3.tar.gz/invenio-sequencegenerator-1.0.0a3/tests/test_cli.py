# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Test command-line interface."""

from __future__ import absolute_import, print_function

from functools import partial

from click.testing import CliRunner

from invenio_sequencegenerator.cli import sequences


def assert_success(res, expected):
    assert res.exit_code == 0
    assert res.exception is None
    assert expected in res.output


def test_cli_authors(script_info, db):
    """Test CLI for the use case of author identifiers."""
    runner = CliRunner()
    run = partial(runner.invoke, sequences, obj=script_info)

    assert_success(
        run(['create', 'AUTH', '{author}.{counter}',
             '--start', '1', '--step', '2']),
        'Template "AUTH" created successfully.'
    )

    author_1 = partial(run, ['next', 'AUTH', 'author=John.Tester'])
    assert_success(author_1(), 'John.Tester.1')
    assert_success(author_1(), 'John.Tester.3')
    assert_success(author_1(), 'John.Tester.5')

    author_2 = partial(run, ['next', 'AUTH', 'author=Tom.Phake'])
    assert_success(author_2(), 'Tom.Phake.1')
    assert_success(author_2(), 'Tom.Phake.3')
    assert_success(author_2(), 'Tom.Phake.5')


def test_cli_playlists(script_info, db):
    """Test CLI for the use case of video playlist identifiers."""
    runner = CliRunner()
    run = partial(runner.invoke, sequences, obj=script_info)

    assert_success(
        run(['create', 'PL', 'PL {counter}']),
        'Template "PL" created successfully.'
    )
    assert_success(
        run(['create', 'FL', '{PL} > {counter}']),
        'Template "FL" created successfully.'
    )

    assert_success(run(['next', 'PL']), 'PL 0')
    assert_success(run(['next', 'PL']), 'PL 1')

    fl1 = partial(run, ['next', 'FL', 'PL=PL 0'])
    fl2 = partial(run, ['next', 'FL', 'PL=PL 1'])

    assert_success(fl1(), 'PL 0 > 0')
    assert_success(fl1(), 'PL 0 > 1')
    assert_success(fl1(), 'PL 0 > 2')

    assert_success(fl2(), 'PL 1 > 0')
    assert_success(fl2(), 'PL 1 > 1')
    assert_success(fl2(), 'PL 1 > 2')
