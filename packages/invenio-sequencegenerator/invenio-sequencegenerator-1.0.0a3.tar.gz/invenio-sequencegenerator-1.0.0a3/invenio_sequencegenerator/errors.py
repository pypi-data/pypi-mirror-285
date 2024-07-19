# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Errors for sequence generation."""

from __future__ import absolute_import, print_function


class SequenceGeneratorError(Exception):
    """Base class for errors in SequenceGenerator module."""


class SequenceNotFound(SequenceGeneratorError):
    """No such sequence error."""


class InvalidTemplate(SequenceGeneratorError):
    """Invalid template error."""

    def __init__(self, reason):
        """Initialize exception."""
        self.reason = reason

    def __str__(self):
        """String representation of error."""
        return self.reason


class InvalidResetCall(SequenceGeneratorError):
    """Invalid reset call error."""

    def __str__(self):
        """String representation of error."""
        return 'Cannot reset sequence: children exist'
