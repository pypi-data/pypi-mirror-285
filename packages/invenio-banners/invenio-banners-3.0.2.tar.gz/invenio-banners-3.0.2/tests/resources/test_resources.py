# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Banners is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Banner resource tests."""
from datetime import date, datetime

import pytest
from invenio_records_resources.services.errors import PermissionDeniedError

from invenio_banners.records import BannerModel

banners = {
    "banner1": {
        "message": "banner1",
        "url_path": "/banner1",
        "category": "info",
        "active": True,
        "start_datetime": date(2022, 7, 20),
        "end_datetime": date(2023, 1, 29),
    },
    "banner2": {
        "message": "banner2",
        "url_path": "/banner2",
        "category": "other",
        "active": False,
        "start_datetime": date(2022, 12, 15),
        "end_datetime": date(2023, 1, 5),
    },
    "banner3": {
        "message": "banner3",
        "url_path": "/banner3",
        "category": "warning",
        "active": True,
        "start_datetime": date(2023, 1, 20),
        "end_datetime": date(2023, 2, 25),
    },
}


def _create_banner(client, data, headers, status_code=None):
    """Send POST request."""
    result = client.post(
        "/banners/",
        headers=headers,
        json=data,
    )
    assert result.status_code == status_code
    return result


def _update_banner(client, id, data, headers, status_code=None):
    """Send PUT request."""
    result = client.put(
        "/banners/{0}".format(id),
        headers=headers,
        json=data,
    )
    assert result.status_code == status_code
    return result


def _delete_banner(client, id, headers, status_code=None):
    """Send DELETE request."""
    result = client.delete("/banners/{0}".format(id), headers=headers)
    assert result.status_code == status_code
    return result


def _get_banner(client, id, status_code=None):
    """Send GET request."""
    result = client.get("/banners/{0}".format(id))
    assert result.status_code == status_code
    return result


def _search_banners(client, status_code=None, query_string=None):
    """Send GET request."""
    result = client.get("/banners/", query_string=query_string)
    assert result.status_code == status_code
    return result


def test_create_is_forbidden(client, user, headers):
    """Test that the simple user cannot create a new banner."""
    user.login(client)

    # try to create a banner
    with pytest.raises(PermissionDeniedError):
        _create_banner(client, banners["banner1"], headers)


def test_create_banner(client, admin, headers):
    """Create a banner."""
    banner_data = banners["banner1"]
    admin.login(client)

    banner = _create_banner(client, banner_data, headers, 201).json
    assert banner["message"] == banner_data["message"]
    assert banner["url_path"] == banner_data["url_path"]
    assert banner["category"] == banner_data["category"]
    assert banner["active"] == banner_data["active"]


def test_disable_expired_after_create_action(client, admin, headers):
    """Disable expired banners after a create a banner action."""
    # create banner first
    banner1 = BannerModel.create(banners["banner1"])
    assert banner1.active is True
    banner_data = banners["banner2"]

    admin.login(client)

    _create_banner(client, banner_data, headers, 201).json

    expired_banner = BannerModel.get(banner1.id)
    assert expired_banner.active is False


def test_update_banner(client, admin, headers):
    """Update a banner."""
    # create banner first
    banner = BannerModel.create(banners["banner1"])

    admin.login(client)

    new_data = {
        "start_datetime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "active": True,
        "message": "New banner message",
        "category": "info",
    }

    updated_banner = _update_banner(client, banner.id, new_data, headers, 200).json

    assert updated_banner["message"] == new_data["message"]
    assert updated_banner["category"] == new_data["category"]
    assert updated_banner["url_path"] == banner.url_path
    assert updated_banner["active"] == banner.active


def test_disable_expired_after_update_action(client, admin, headers):
    """Disable expired banners after an update a banner action."""
    # create banner first
    banner1 = BannerModel.create(banners["banner1"])
    banner2 = BannerModel.create(banners["banner2"])
    assert banner1.active is True

    admin.login(client)

    new_data = {
        "start_datetime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "active": True,
        "message": "New banner message",
        "category": "info",
    }

    _update_banner(client, banner2.id, new_data, headers, 200).json

    expired_banner = BannerModel.get(banner1.id)
    assert expired_banner.active is False


def test_update_is_forbidden(client, user, headers):
    """Test that the simple user cannot update a banner."""
    # create banner first
    banner = BannerModel.create(banners["banner1"])

    user.login(client)

    new_data = {"message": "New banner message"}

    # try to update a banner
    with pytest.raises(PermissionDeniedError):
        _update_banner(client, banner.id, new_data, headers)


def test_update_non_existing_banner(client, admin, headers):
    """Update a non-existing banner."""
    admin.login(client)

    new_data = {"message": "New banner message"}

    # try to update a banner (get 404)
    banner = _update_banner(client, 1, new_data, headers, 404).json

    assert banner["message"] == "Banner with id 1 is not found."


def test_delete_banner(client, admin, headers):
    """Delete a banner."""
    # create banner first
    banner = BannerModel.create(banners["banner1"])

    admin.login(client)

    _delete_banner(client, banner.id, headers, 204)

    # check that it's not present in db
    assert BannerModel.query.filter_by(id=banner.id).one_or_none() is None


def test_delete_is_forbidden(client, user, headers):
    """Test that the simple user cannot delete a banner."""
    # create banner first
    banner = BannerModel.create(banners["banner1"])

    user.login(client)

    # try to delete a banner
    with pytest.raises(PermissionDeniedError):
        _delete_banner(client, banner.id, headers)


def test_delete_non_existing_banner(client, admin, headers):
    """Delete a non-existing banner."""
    admin.login(client)

    # try to delete a banner (get 404)
    banner = _delete_banner(client, 1, headers, 404).json

    assert banner["message"] == "Banner with id 1 is not found."


def test_read_banner(client, user):
    """Read a banner by id."""
    # create banner first
    banner = BannerModel.create(banners["banner1"])

    user.login(client)

    banner_result = _get_banner(client, banner.id, 200).json
    assert banner_result["message"] == banner.message
    assert banner_result["url_path"] == banner.url_path
    assert banner_result["category"] == banner.category
    assert banner_result["active"] == banner.active


def test_read_non_existing_banner(client, user):
    """Read a non-existing banner."""
    user.login(client)

    # try to get a banner (get 404)
    banner = _get_banner(client, 1, 404).json

    assert banner["message"] == "Banner with id 1 is not found."


def test_search_banner(client, user):
    """Search for banners without query parameters."""
    # create banners first
    BannerModel.create(banners["banner1"])
    BannerModel.create(banners["banner2"])

    user.login(client)

    banners_result = _search_banners(client, 200).json

    result_hits = banners_result["hits"]
    assert result_hits["total"] == 2
    result_list = result_hits["hits"]
    assert len(result_list) == 2
    assert result_list[0]["message"] == "banner1"
    assert result_list[1]["message"] == "banner2"


def test_search_banner_with_params(client, user):
    """Search for banners with the query string."""
    # create banners first
    BannerModel.create(banners["banner1"])
    BannerModel.create(banners["banner2"])
    BannerModel.create(banners["banner3"])

    user.login(client)

    # filtering
    # filter by string(category)
    query_string = {"q": "warning"}
    banners_result = _search_banners(client, 200, query_string).json

    result_hits = banners_result["hits"]
    assert result_hits["total"] == 1
    assert result_hits["hits"][0]["message"] == "banner3"

    # filter by bool(active)
    query_string = {"q": "false"}
    banners_result = _search_banners(client, 200, query_string).json

    result_hits = banners_result["hits"]
    assert result_hits["total"] == 1
    assert result_hits["hits"][0]["message"] == "banner2"

    # filter by datetime(start_datetime)
    query_string = {"q": "2023-1-20"}
    banners_result = _search_banners(client, 200, query_string).json

    result_hits = banners_result["hits"]
    assert result_hits["total"] == 1
    assert result_hits["hits"][0]["message"] == "banner3"

    # sorting
    # default sort (by created field in asc order)
    banners_result = _search_banners(client, 200).json
    result_hits = banners_result["hits"]
    assert result_hits["total"] == 3
    assert result_hits["hits"][0]["message"] == "banner1"
    assert result_hits["hits"][1]["message"] == "banner2"
    assert result_hits["hits"][2]["message"] == "banner3"

    # sort by string(category)
    query_string = {"sort": "category"}
    banners_result = _search_banners(client, 200, query_string).json
    result_hits = banners_result["hits"]
    assert result_hits["total"] == 3
    assert result_hits["hits"][0]["message"] == "banner1"
    assert result_hits["hits"][1]["message"] == "banner2"
    assert result_hits["hits"][2]["message"] == "banner3"

    # sort by bool(active)
    query_string = {"sort": "active"}
    banners_result = _search_banners(client, 200, query_string).json
    result_hits = banners_result["hits"]
    assert result_hits["total"] == 3
    assert result_hits["hits"][0]["message"] == "banner2"
    assert result_hits["hits"][1]["message"] == "banner1"
    assert result_hits["hits"][2]["message"] == "banner3"

    # sort by datetime(end_datetime)
    query_string = {"sort": "end_datetime"}
    banners_result = _search_banners(client, 200, query_string).json
    result_hits = banners_result["hits"]
    assert result_hits["total"] == 3
    assert result_hits["hits"][0]["message"] == "banner2"
    assert result_hits["hits"][1]["message"] == "banner1"
    assert result_hits["hits"][2]["message"] == "banner3"

    # sorting direction
    # descending order
    query_string = {"sort_direction": "desc"}
    banners_result = _search_banners(client, 200, query_string).json
    result_hits = banners_result["hits"]
    assert result_hits["total"] == 3
    assert result_hits["hits"][0]["message"] == "banner3"
    assert result_hits["hits"][1]["message"] == "banner2"
    assert result_hits["hits"][2]["message"] == "banner1"

    # paginated search
    query_string = {"size": "2"}
    banners_result = _search_banners(client, 200, query_string).json
    result_hits = banners_result["hits"]
    assert len(result_hits) == 2
    assert result_hits["total"] == 3
    assert result_hits["hits"][0]["message"] == "banner1"
    assert result_hits["hits"][1]["message"] == "banner2"


def test_search_banner_empty_list(client, user):
    """Search for banners (no banner found)."""
    user.login(client)

    banners = _search_banners(client, 200).json

    result = banners["hits"]
    assert len(result["hits"]) == 0
    assert result["total"] == 0
