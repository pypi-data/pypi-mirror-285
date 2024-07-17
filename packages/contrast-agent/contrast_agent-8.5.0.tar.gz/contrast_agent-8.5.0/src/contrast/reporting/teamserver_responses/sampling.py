# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from functools import cached_property
from typing import Optional


class Sampling:
    def __init__(self, sampling_json: dict, ng: bool):
        self.sampling_json = sampling_json or {}
        self.ng = ng

    @cached_property
    def enable(self) -> bool:
        if self.ng:
            return self.sampling_json.get("enabled", False)
        return self.sampling_json.get("enable", False)

    @cached_property
    def baseline(self) -> Optional[int]:
        return self.sampling_json.get("baseline", None)

    @cached_property
    def request_frequency(self) -> Optional[int]:
        if self.ng:
            return self.sampling_json.get("frequency", None)
        return self.sampling_json.get("request_frequency", None)

    @cached_property
    def window_ms(self) -> Optional[int]:
        if self.ng:
            if window := self.sampling_json.get("window", None):
                return window * 1000
            return None
        if window := self.sampling_json.get("window_ms", None):
            return window * 1000
        return None
