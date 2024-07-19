# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2023 Graz University of Technology.
#
# invenio-campusonline is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""


from pathlib import Path
from xml.etree.ElementTree import Element, parse

import pytest
from flask import Flask

from invenio_campusonline import InvenioCampusonline


@pytest.fixture()
def minimal_record() -> Element:
    """Create minimal record."""
    return parse(Path(__file__).parent / "minimal_record.xml")


@pytest.fixture(scope="module")
def create_app(instance_path: str) -> Flask:
    """Application factory fixture."""

    def factory(**config: dict) -> Flask:
        app = Flask("testapp", instance_path=instance_path)
        app.config.update(**config)
        InvenioCampusonline(app)
        return app

    return factory
