# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from functools import cached_property
from typing import List, Optional

from contrast.agent.exclusions import TsExclusion, ExclusionType
from contrast.reporting.teamserver_responses.protect_rule import ProtectRule


class ApplicationSettings:
    """
    This class is responsible for safely parsing V1 TeamServer Application Settings from a response to a usable format.
    The format can be found here: https://github.com/Contrast-Security-Inc/contrast-agent-api-spec. At the time of the
    creation of this class, the specific schema is ApplicationSettings in agent-endpoints.yml.
    """

    def __init__(self, application_settings_json: Optional[dict] = None):
        self.application_settings_json = application_settings_json or {}

    @cached_property
    def disabled_assess_rules(self) -> List[str]:
        return [
            rule_name
            for rule_name, rule_details in self.application_settings_json.get(
                "assess", {}
            ).items()
            if not rule_details.get("enable", False)
        ]

    @cached_property
    def exclusions(self) -> List[TsExclusion]:
        """
        Build and return a plain list of TsExclusions based on raw application settings. TsExclusions represent the
        exclusions more or less exactly as they were given to us by teamserver.

        The list returned by this property will be converted into our own Exclusions class later, which is more useful
        when processing exclusion rules.
        """
        if not (
            ts_exclusions := self.application_settings_json.get("exclusions", None)
        ):
            return []

        exclusions = []
        for exclusion in ts_exclusions.get("url", []):
            exclusions.append(
                TsExclusion(
                    ExclusionType.URL_EXCLUSION_TYPE,
                    exclusion.get("name", ""),
                    exclusion.get("modes", []),
                    exclusion.get("match_strategy", ""),
                    exclusion.get("protect_rules", []),
                    exclusion.get("assess_rules", []),
                    exclusion.get("urls", []),
                )
            )

        for exclusion in ts_exclusions.get("input", []):
            exclusions.append(
                TsExclusion(
                    ExclusionType.INPUT_EXCLUSION_TYPE,
                    # there's a hiccup in the API where "name" was repurposed for input exclusions
                    None,
                    exclusion.get("modes", []),
                    exclusion.get("match_strategy", ""),
                    exclusion.get("protect_rules", []),
                    exclusion.get("assess_rules", []),
                    exclusion.get("urls", []),
                    exclusion.get("type", ""),
                    # there's a hiccup in the API where "name" was repurposed for input exclusions
                    exclusion.get("name", ""),
                )
            )

        return exclusions

    @cached_property
    def protect_rules(self) -> List[ProtectRule]:
        return [
            ProtectRule({"id": name, **value})
            for name, value in self.application_settings_json.get("protect", {})
            .get("rules", {})
            .items()
            if value
        ]

    @cached_property
    def sensitive_data_masking_policy(self) -> dict:
        return self.application_settings_json.get("sensitive_data_masking_policy", {})

    @cached_property
    def session_id(self) -> Optional[str]:
        return self.application_settings_json.get("session_id", None)
