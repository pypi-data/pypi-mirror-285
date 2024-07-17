# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from functools import cached_property
from typing import Dict, Optional


from contrast.reporting.teamserver_responses.sampling import Sampling
from contrast.utils.mapping import GlomDict


class ServerSettings:
    """
    This class is responsible for safely parsing V1 TeamServer Server Settings from a response to a usable format.
    The format can be found here: https://github.com/Contrast-Security-Inc/contrast-agent-api-spec. At the time of the
    creation of this class, the specific schema is ServerSettings in agent-endpoints.yml.
    """

    def __init__(self, server_settings_json: Optional[dict] = None):
        self.server_settings_json = GlomDict(server_settings_json or {})

    @cached_property
    def assess_enabled(self) -> bool:
        return self.server_settings_json.get("assess.enable", False)

    @cached_property
    def protect_enabled(self) -> bool:
        return self.server_settings_json.get("protect.enable", False)

    @cached_property
    def sampling(self) -> Optional[Sampling]:
        return Sampling(self.server_settings_json.get("assess.sampling"), ng=False)

    def common_config(self) -> Dict[str, object]:
        """
        Returns the settings in a flattened common configuration format.
        """

        return {
            "agent.logger.level": self.server_settings_json.get("logger.level"),
            "agent.logger.path": self.server_settings_json.get("logger.path"),
            "agent.security_logger.syslog.enable": self.server_settings_json.get(
                "security_logger.syslog.enable"
            ),
            "agent.security_logger.syslog.protocol": self.server_settings_json.get(
                "security_logger.syslog.protocol"
            ),
            # security_logger.syslog.connection_type is ignored because the protocol
            # includes the connection type.
            "agent.security_logger.syslog.server_host": self.server_settings_json.get(
                "security_logger.syslog.ip"
            ),
            "agent.security_logger.syslog.port": self.server_settings_json.get(
                "security_logger.syslog.port"
            ),
            "agent.security_logger.syslog.facility": self.server_settings_json.get(
                "security_logger.syslog.facility"
            ),
            "agent.security_logger.syslog.severity_exploited": self.server_settings_json.get(
                "security_logger.syslog.severity_exploited"
            ),
            "agent.security_logger.syslog.severity_blocked": self.server_settings_json.get(
                "security_logger.syslog.severity_blocked"
            ),
            "agent.security_logger.syslog.severity_blocked_perimeter": self.server_settings_json.get(
                "security_logger.syslog.severity_blocked_perimeter"
            ),
            "agent.security_logger.syslog.severity_probed": self.server_settings_json.get(
                "security_logger.syslog.severity_probed"
            ),
            "agent.security_logger.syslog.severity_suspicious": self.server_settings_json.get(
                "security_logger.syslog.severity_suspicious"
            ),
        }
