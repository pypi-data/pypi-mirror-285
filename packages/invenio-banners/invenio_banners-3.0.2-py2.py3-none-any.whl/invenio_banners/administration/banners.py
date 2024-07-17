# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-Banners is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio administration banners view module."""

from invenio_administration.views.base import (
    AdminResourceCreateView,
    AdminResourceDetailView,
    AdminResourceEditView,
    AdminResourceListView,
)
from invenio_i18n import lazy_gettext as _


class BannerListView(AdminResourceListView):
    """Search admin view."""

    api_endpoint = "/banners"
    name = "banners"
    resource_config = "banners_resource"
    title = "Banners"
    menu_label = "Banners"
    category = _("Site management")
    pid_path = "id"
    icon = "newspaper"

    display_search = True
    display_delete = True
    display_create = True
    display_edit = True

    item_field_list = {
        "id": {"text": _("Id"), "order": 1, "width": 1},
        "start_datetime": {"text": _("Start time (UTC)"), "order": 2, "width": 2},
        "end_datetime": {"text": _("End time (UTC)"), "order": 3, "width": 2},
        "message": {"text": _("Message"), "order": 4, "width": 7},
        "active": {"text": _("Active"), "order": 5, "width": 1},
        "url_path": {"text": _("URL path"), "order": 6, "width": 2},
        "category": {"text": _("Category"), "order": 7, "width": 1},
    }

    create_view_name = "banner_create"

    search_config_name = "BANNERS_SEARCH"
    search_sort_config_name = "BANNERS_SORT_OPTIONS"


class BannerEditView(AdminResourceEditView):
    """Configuration for Banner edit view."""

    name = "banner_edit"
    url = "/banners/<pid_value>/edit"
    resource_config = "banners_resource"
    pid_path = "id"
    api_endpoint = "/banners"
    title = "Edit Banner"

    list_view_name = "banners"

    form_fields = {
        "start_datetime": {
            "order": 1,
            "text": _("Start time"),
            "description": _(
                "Input format: yyyy-mm-dd hh:mm:ss. "
                "Set to current or future date/time to delay the banner. "
                "Note: specify time in UTC time standard."
            ),
            "placeholder": _("YYYY-MM-DD hh:mm:ss"),
        },
        "end_datetime": {
            "order": 2,
            "text": _("End time"),
            "description": _(
                "Input format: yyyy-mm-dd hh:mm:ss. Date/time "
                "to make the banner inactive. Empty value will make "
                "the banner active until manually disabled via the active flag. "
                "Note: specify time in UTC time standard."
            ),
            "placeholder": _("YYYY-MM-DD hh:mm:ss"),
        },
        "message": {
            "order": 3,
            "text": _("Message"),
            "description": _(
                "Message to be displayed on the banner. HTML format is supported."
            ),
            "rows": 10,
        },
        "url_path": {
            "order": 4,
            "text": _("URL path"),
            "description": _(
                "Enter the URL path (including the first /) to define in "
                "which part of the site the message will be active. For "
                "example, if you enter `/records`, any URL starting with "
                "`/records` will return an active banner (/records, "
                "/records/1234, etc...). Empty value will make the banner "
                "active for any URL."
            ),
        },
        "category": {
            "order": 5,
            "text": _("Category"),
            "description": _(
                "Banner category. Info option displays the banner "
                "with information message in a blue color. "
                "Warning - a warning information in an orange color. "
                "Other - all the rest types of massages in a gray color."
            ),
            "options": [
                {"title_l10n": "Info", "id": "info"},
                {"title_l10n": "Warning", "id": "warning"},
                {"title_l10n": "Other", "id": "other"},
            ],
            "placeholder": "Select a category",
        },
        "active": {
            "order": 6,
            "text": _("Active"),
            "description": _(
                "Tick it to activate the banner: banner will be"
                "displayed according to start/end times. If not "
                "activated, start/end times will be ignored."
            ),
        },
        "created": {"order": 7},
        "updated": {"order": 8},
    }


class BannerCreateView(AdminResourceCreateView):
    """Configuration for Banner create view."""

    name = "banner_create"
    url = "/banners/create"
    resource_config = "banners_resource"
    pid_path = "id"
    api_endpoint = "/banners"
    title = "Create Banner"

    list_view_name = "banners"

    form_fields = {
        "start_datetime": {
            "order": 1,
            "text": _("Start time"),
            "description": _(
                "Input format: yyyy-mm-dd hh:mm:ss. "
                "Set to current or future date/time to delay the banner. "
                "Note: specify time in UTC time standard."
            ),
            "placeholder": _("YYYY-MM-DD hh:mm:ss"),
        },
        "end_datetime": {
            "order": 2,
            "text": _("End time"),
            "description": _(
                "Input format: yyyy-mm-dd hh:mm:ss. Date/time "
                "to make the banner inactive. Empty value will make "
                "the banner active until manually disabled via the active flag. "
                "Note: specify time in UTC time standard."
            ),
            "placeholder": _("YYYY-MM-DD hh:mm:ss"),
        },
        "message": {
            "order": 3,
            "text": _("Message"),
            "description": _(
                "Message to be displayed on the banner. HTML format is supported."
            ),
            "rows": 10,
        },
        "url_path": {
            "order": 4,
            "text": _("URL path"),
            "description": _(
                "Enter the URL path (including the first /) to define in "
                "which part of the site the message will be active. For "
                "example, if you enter `/records`, any URL starting with "
                "`/records` will return an active banner (/records, "
                "/records/1234, etc...). Empty value will make the banner "
                "active for any URL."
            ),
        },
        "category": {
            "order": 5,
            "text": _("Category"),
            "description": _(
                "Banner category. Info option displays the banner "
                "with information message in a blue color. "
                "Warning - a warning information in an orange color. "
                "Other - all the rest types of messages in a gray color."
            ),
            "options": [
                {"title_l10n": "Info", "id": "info"},
                {"title_l10n": "Warning", "id": "warning"},
                {"title_l10n": "Other", "id": "other"},
            ],
            "placeholder": "Select a category",
        },
        "active": {
            "order": 6,
            "text": _("Active"),
            "description": _(
                "Tick it to activate the banner: banner will be"
                "displayed according to start/end times. If not "
                "activated, start/end times will be ignored."
            ),
        },
    }


class BannerDetailView(AdminResourceDetailView):
    """Admin banner detail view."""

    url = "/banners/<pid_value>"
    api_endpoint = "/banners"
    name = "banner-details"
    resource_config = "banners_resource"
    title = "Banner Details"

    display_delete = True
    display_edit = True

    list_view_name = "banners"
    pid_path = "id"

    item_field_list = {
        "start_datetime": {"text": _("Start time"), "order": 1},
        "end_datetime": {"text": _("End time"), "order": 2},
        "message": {"text": _("Message"), "order": 3},
        "url_path": {"text": _("URL path"), "order": 4},
        "category": {"text": _("Category"), "order": 5},
        "active": {"text": _("Active"), "order": 6},
        "created": {"text": _("Created"), "order": 7},
        "updated": {"text": _("Updated"), "order": 8},
    }
