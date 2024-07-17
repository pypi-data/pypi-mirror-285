# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from typing import Literal
import requests

from .base_ts_message import BaseTsServerMessage
from contrast.utils.decorators import fail_loudly


class ServerInventory(BaseTsServerMessage):
    def __init__(self, cloud_provider: Literal["aws", "azure"], cloud_resource_id: str):
        super().__init__()

        # TODO: PYT-3378 use v1.1
        self.base_url = f"{self.settings.api_url}/agents/v1.0/"

        self.body = {
            "cloud_provider": cloud_provider,
            "cloud_resource_id": cloud_resource_id,
        }

    # TODO: PYT-3381 Remove special 404 logic completely for this message
    @property
    def ignore_404(self) -> bool:
        return True

    @property
    def name(self) -> str:
        return "server-inventory"

    @property
    def path(self) -> str:
        return "/".join(
            [
                "servers",
                self.server_name_b64,
                self.server_path_b64,
                self.server_type_b64,
                "inventory",
            ]
        )

    @property
    def request_method(self):
        return requests.Session.post

    @fail_loudly()
    def process_response(self, response, reporting_client):
        self.process_response_code(response, reporting_client)
