# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-campusonline is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Command line interface to interact with the CampusOnline-Connector module."""


from datetime import date as Date

from click import STRING, Choice, DateTime, group, option, secho
from click_params.domain import UrlParamType
from flask import current_app
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_access.utils import get_identity
from invenio_accounts import current_accounts

from .services import CampusOnlineRESTService, build_services
from .types import Color
from .utils import as_date


@group()
def campusonline() -> None:
    """Campusonline CLI."""


@campusonline.command()
@with_appcontext
@option("--endpoint", type=UrlParamType(may_have_port=True), required=True)
@option("--token", type=STRING, required=True)
@option("--campusonline-id", type=STRING, required=True)
@option("--user-email", type=STRING, required=True)
@option("--no-color", is_flag=True, default=False)
@build_services
def import_thesis(
    cms_service: CampusOnlineRESTService,
    campusonline_id: str,
    user_email: str,
    no_color: bool,  # noqa: FBT001
) -> None:
    """Import metadata and file (aka one thesis) from campusonline."""
    import_func = current_app.config["CAMPUSONLINE_IMPORT_FUNC"]
    user = current_accounts.datastore.get_user_by_email(user_email)
    identity = get_identity(user)
    record = import_func(identity, campusonline_id, cms_service)

    color = Color.success if not no_color else Color.neutral
    secho(f"record.id: {record.id}", fg=color)


@campusonline.command()
@with_appcontext
@option("--endpoint", type=UrlParamType(may_have_port=True), required=True)
@option("--token", type=STRING, required=True)
@option("--no-color", is_flag=True, default=False)
@build_services
def fetch_ids(
    cms_service: CampusOnlineRESTService,
    *,
    no_color: bool,
) -> None:
    """Fetch all to import ids."""
    theses_filter = current_app.config["CAMPUSONLINE_THESES_FILTER"]
    ids = cms_service.fetch_all_ids(system_identity, theses_filter)

    color = Color.success if not no_color else Color.neutral
    secho(f"ids: {ids}", fg=color)


@campusonline.command()
@with_appcontext
@option("--endpoint", type=UrlParamType(may_have_port=True))
@option("--token", type=STRING)
@option("--user-email", type=STRING, default="cms@tugraz.at")
def full_sync(cms_service: CampusOnlineRESTService, user_email: str) -> None:
    """Full sync."""
    import_func = current_app.config["CAMPUSONLINE_IMPORT_FUNC"]
    theses_filter = current_app.config["CAMPUSONLINE_THESES_FILTER"]

    user = current_accounts.datastore.get_user_by_email(user_email)
    identity = get_identity(user)
    ids = cms_service.fetch_all_ids(theses_filter)

    for cms_id in ids:
        try:
            import_func(identity, cms_id, cms_service)
        except RuntimeError as e:
            msg = f"ERROR cms_id: {cms_id} couldn't be imported because of {e}"
            secho(msg, fg=Color.error)


@campusonline.command()
@with_appcontext
@option("--endpoint", type=UrlParamType(may_have_port=True), required=True)
@option("--token", type=STRING, required=True)
@option("--campusonline-id", type=STRING, default="")
@build_services
def duplicate_check(cms_service: CampusOnlineRESTService, campusonline_id: str) -> None:
    """Duplicate check."""
    duplicate_func = current_app.config["CAMPUSONLINE_DUPLICATE_FUNC"]
    theses_filter = current_app.config["CAMPUSONLINE_THESES_FILTER"]

    if campusonline_id == "":
        ids = cms_service.fetch_all_ids(theses_filter)
    else:
        ids = [campusonline_id]

    duplicates = [cms_id for cms_id in ids if duplicate_func(cms_id)]

    for duplicate in duplicates:
        secho(duplicate, fg=Color.neutral)


@campusonline.command()
@with_appcontext
@option("--campusonline-id", type=STRING, required=True)
@option("--endpoint", type=UrlParamType(may_have_port=True), required=True)
@option("--token", type=STRING, required=True)
@option(
    "--status",
    type=Choice(["ARCHIVED", "PUBLISHED"], case_sensitive=True),
    required=True,
)
@option("--date", type=DateTime(["%Y-%m-%dT%H:%M:%S"]), callback=as_date, required=True)
@option("--user-email", type=STRING, default="cms@tugraz.at", required=True)
@option("--no-color", is_flag=True, default=False)
@build_services
def update_status(
    cms_service: CampusOnlineRESTService,
    campusonline_id: str,
    status: str,
    date: Date,
    user_email: str,
    *,
    no_color: bool,
) -> None:
    """Update status."""
    user = current_accounts.datastore.get_user_by_email(user_email)
    identity = get_identity(user)
    response = cms_service.set_status(
        identity,
        campusonline_id,
        status,
        date.strftime("%Y-%m-%dT%H:%M:%S"),
    )
    color = Color.success if not no_color else Color.neutral
    secho(f"response: {response}", fg=color)
