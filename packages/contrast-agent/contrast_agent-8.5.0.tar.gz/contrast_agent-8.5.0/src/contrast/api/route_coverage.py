# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast_vendor import structlog as logging

logger = logging.getLogger("contrast")


class Route:
    """
    Route object used for various TS messages
    """

    def __init__(self, verb, url, signature, framework=None):
        self.verb = verb or "GET"
        self.url = url or "/"
        self.signature = signature or ""
        self.framework = framework
        self.sources = []

    def __hash__(self) -> int:
        return hash((self.verb, self.url, self.signature, self.framework))

    def __eq__(self, other) -> bool:
        return isinstance(other, Route) and (
            self.verb == other.verb
            and self.url == other.url
            and self.signature == other.signature
            and self.framework == other.framework
        )

    def __repr__(self):
        return f"<Route({self.verb!r}, {self.url!r}, {self.signature!r}, {self.framework!r})>"

    def to_json_inventory(self):
        """json representation used in v1.1 ApplicationInventory.routes"""
        return {
            "signature": self.signature,
            "verb": self.verb,
            "url": self.url,
            "framework": self.framework,
        }

    def to_json_traces(self):
        """json representation used in ng Traces.routes"""
        return {
            # "The number of times this route was observed; must be more than 0"
            "count": 1,
            "observations": [{"url": self.url, "verb": self.verb}],
            "signature": self.signature,
        }
