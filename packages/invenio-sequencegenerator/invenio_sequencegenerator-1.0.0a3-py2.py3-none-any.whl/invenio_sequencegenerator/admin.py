# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Admin views for invenio-accounts."""

from flask import redirect, request, url_for
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from invenio_i18n import gettext as _
from invenio_db import db

from .models import Counter, TemplateDefinition


class TemplateDefinitionView(ModelView):
    """Flask-Admin view for template definitions."""

    column_list = (
        "name",
        "meta_template",
        "parent_name",
        "start",
        "step",
    )


class CounterView(ModelView):
    """Admin view for counters."""

    list_template = "invenio_sequencegenerator/custom_list.html"

    column_list = (
        "template_instance",
        "counter",
        "definition_name",
    )

    @expose("/reset", methods=("POST",))
    def reset_view(self):
        """Reset selected counter."""
        start = request.form.get("start", default=0, type=int)
        template_instance = request.form["rowid"]
        Counter.query.get(template_instance).reset(start=start)
        db.session.commit()
        return redirect(url_for(".index_view"))


templatedefinition_adminview = {
    "model": TemplateDefinition,
    "modelview": TemplateDefinitionView,
    "category": _("Sequences"),
}

counter_adminview = {
    "model": Counter,
    "modelview": CounterView,
    "category": _("Sequences"),
}

__all__ = ("templatedefinition_adminview", "counter_adminview")
