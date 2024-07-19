# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-campusonline is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Records."""

from .api import CampusOnlineAPI
from .config import CampusOnlineRESTConfig
from .models import CampusOnlineConnection

__all__ = (
    "CampusOnlineAPI",
    "CampusOnlineConnection",
    "CampusOnlineRESTConfig",
)
