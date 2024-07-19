# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-campusonline is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Helper proxy to the state object."""

from flask import current_app
from werkzeug.local import LocalProxy

current_campusonline = LocalProxy(
    lambda: current_app.extensions["invenio-campusonline"],
)
"""Helper proxy to get teh current campusonline extension."""
