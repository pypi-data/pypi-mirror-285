# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from functools import cached_property
from typing import List, Optional

from contrast.agent.exclusions import TsExclusion, ExclusionType
from contrast.reporting.teamserver_responses.protect_rule import ProtectRule


class NGApplicationSettings:
    def __init__(self, settings_json=None):
        self._raw_settings = settings_json or {}

    @cached_property
    def disabled_assess_rules(self) -> List[str]:
        return (
            self._raw_settings.get("settings", {})
            .get("assessment", {})
            .get("disabledRules", [])
        )

    @cached_property
    def protection_rules(self) -> List[ProtectRule]:
        return [
            ProtectRule(r)
            for r in self._raw_settings.get("settings", {})
            .get("defend", {})
            .get("protectionRules", [])
        ]

    @cached_property
    def session_id(self) -> Optional[str]:
        return (
            self._raw_settings.get("settings", {})
            .get("assessment", {})
            .get("session_id", None)
        )

    @cached_property
    def sensitive_data_masking_policy(self) -> dict:
        return self._raw_settings.get("settings", {}).get(
            "sensitive_data_masking_policy"
        )

    @cached_property
    def exclusions(self) -> Optional[List[TsExclusion]]:
        """
        Build and return a plain list of TsExclusions based on raw application settings.
        TsExclusions represent the exclusions more or less exactly as they were given to
        us by teamserver.

        The list returned by this property will be converted into our own Exclusions
        class later, which is more useful when processing exclusion rules.
        """
        ts_exclusions = self._raw_settings.get("settings", {}).get("exceptions")
        if ts_exclusions is None:
            return None

        exclusions = []

        for exclusion in ts_exclusions.get("urlExceptions", []):
            exclusions.append(
                TsExclusion(
                    ExclusionType.URL_EXCLUSION_TYPE,
                    exclusion.get("name", ""),
                    exclusion.get("modes", []),
                    exclusion.get("matchStrategy", ""),
                    exclusion.get("protectionRules", []),
                    exclusion.get("assessmentRules", []),
                    exclusion.get("urls", []),
                )
            )

        for exclusion in ts_exclusions.get("inputExceptions", []):
            exclusions.append(
                TsExclusion(
                    ExclusionType.INPUT_EXCLUSION_TYPE,
                    exclusion.get("name", ""),
                    exclusion.get("modes", []),
                    exclusion.get("matchStrategy", ""),
                    exclusion.get("protectionRules", []),
                    exclusion.get("assessmentRules", []),
                    exclusion.get("urls", []),
                    exclusion.get("inputType", ""),
                    exclusion.get("inputName", ""),
                )
            )

        return exclusions

    # note: there are more fields on ApplicationSettings that we currently don't use
