# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-campusonline is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""The module is used to import/export from/to the CampusOnline System."""


from .ext import InvenioCampusonline
from .proxies import current_campusonline
from .services import CampusOnlineRESTService
from .types import CampusOnlineID, ThesesFilter

__version__ = "0.5.0"

__all__ = (
    "__version__",
    "InvenioCampusonline",
    "CampusOnlineID",
    "CampusOnlineRESTService",
    "ThesesFilter",
    "current_campusonline",
)
