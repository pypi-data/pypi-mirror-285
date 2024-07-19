# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-campusonline is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE
# file for more details.


"""Types."""

from dataclasses import dataclass
from datetime import datetime

URL = str
"""Type to indicate that an URL is necessary."""

CampusOnlineToken = str
"""Type to indicate that the campus online token is necessary.

It will not have a special schema.
"""

CampusOnlineID = str
"""Type to indicate that the campus online id of the record is necessary.

It will not have a special schema.
"""

CampusOnlineStatus = str
"""Type to indicate the status of the record in the campus online system.

The value could be either ARCH (archived) or PUB (published).
"""

FilePath = str
"""The path to the file on the local machine."""

EmailAddress = str
"""The email address.

The address does not have to have a special format, but it has to be an email.
"""


@dataclass(frozen=True)
class Embargo:
    """The class is for the embargo management."""

    start: datetime = None
    end: datetime = None

    @property
    def end_date(self) -> str:
        """Calculate str date in format %Y-%m-%d."""
        return self.end.strftime("%Y-%m-%d")

    def __bool__(self) -> bool:
        """Check if values are set, otherwise return is false."""
        return bool(self.start and self.end)


@dataclass(frozen=True)
class Color:
    """The class is for the output color management."""

    neutral = "black"
    error = "red"
    warning = "yellow"
    abort = "magenta"
    success = "green"
    alternate = ("blue", "cyan")


@dataclass
class ThesesFilter:
    """Filter dataclass."""

    filter_: str

    def __str__(self) -> str:
        """Convert to string."""
        return self.filter_


@dataclass
class CampusOnlineConfigs:
    """Configs for campus online."""

    endpoint: URL
    token: CampusOnlineToken
    user_email: EmailAddress
    theses_filter: ThesesFilter
    recipients: list[EmailAddress]
    sender: EmailAddress
