# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-campusonline is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Services."""


from datetime import date as Date
from xml.etree.ElementTree import Element

from flask_principal import Identity

from ..records import CampusOnlineAPI
from ..types import CampusOnlineID, CampusOnlineStatus, FilePath, ThesesFilter
from .config import CampusOnlineRESTServiceConfig


class CampusOnlineRESTService:
    """Campusonline REST service."""

    def __init__(self, config: CampusOnlineRESTServiceConfig) -> None:
        """Construct."""
        self._config = config
        self.api = self.api_cls(config=config)

    @property
    def api_cls(self) -> CampusOnlineAPI:
        """Get api cls."""
        return self._config.api_cls

    def fetch_all_ids(
        self,
        _: Identity,
        theses_filter: ThesesFilter,
    ) -> list[CampusOnlineID]:
        """Fetch all ids."""
        return self.api.fetch_ids(theses_filter)

    def download_file(self, _: Identity, cms_id: CampusOnlineID) -> FilePath:
        """Download file."""
        return self.api.download_file(cms_id)

    def get_metadata(self, _: Identity, cms_id: CampusOnlineID) -> Element:
        """Get metadata."""
        return self.api.get_metadata(cms_id)

    def set_status(
        self,
        _: Identity,
        cms_id: CampusOnlineID,
        status: CampusOnlineStatus,
        date: Date,
    ) -> bool:
        """Set Status."""
        self.api.set_status(cms_id, status, date)
