# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-campusonline is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Services."""

from .config import CampusOnlineRESTServiceConfig
from .decorators import build_services
from .services import CampusOnlineRESTService

__all__ = (
    "CampusOnlineRESTService",
    "CampusOnlineRESTServiceConfig",
    "build_services",
)
