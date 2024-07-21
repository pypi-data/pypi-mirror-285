"""Resource client to obtain information about sidecars."""

from enum import Enum
from typing import Any, Dict, List, Optional

from .resource import ResourceClient


class SidecarClient(ResourceClient):
    """class SidecarClient can be used to obtain information about sidecars."""

    class LogLevel(str, Enum):
        """Possible log levels for a cyral sidecar"""

        TRACE = "trace"
        DEBUG = "debug"
        INFO = "info"
        WARN = "warn"
        ERROR = "error"
        FATAL = "fatal"

    def get(self, sidecar_id: str) -> Dict[str, Any]:
        """get fetches information related to the sidecar"""
        uri = f"/v1/sidecars/{sidecar_id}"
        return self.do_get(uri)

    def set_log_level(self, sidecar_id: str, **services: LogLevel) -> None:
        """set_log_level sets the log level of different services"""
        uri = f"/v1/sidecars/{sidecar_id}"
        data = {
            "services": {
                service: {
                    "log-level": log_level,
                }
                for (service, log_level) in services.items()
            }
        }
        return self.do_put(uri, data)

    def list_sidecars(self) -> List[Dict[str, Any]]:
        """lists all sidecars in the control plane"""
        uri = "/v1/sidecars"
        return self.do_get(uri)

    def get_binding(self, sidecar_id: str, binding_id: str) -> Dict[str, Any]:
        """fetch information related to a port binding"""
        uri = f"/v1/sidecars/{sidecar_id}/bindings/{binding_id}"
        return self.do_get(uri)

    def list_bindings(self, sidecar_id: str) -> Dict[str, Any]:
        """list all port bindings on a sidecar"""
        uri = f"/v1/sidecars/{sidecar_id}/bindings"
        return self.do_get(uri)

    def get_listener(
        self, sidecar_id: str, listener_id: str
    ) -> Dict[str, Any]:
        """fetch information related to a network listener"""
        uri = f"/v1/sidecars/{sidecar_id}/listeners/{listener_id}"
        return self.do_get(uri)

    def list_listeners(self, sidecar_id: str) -> Dict[str, Any]:
        """get all network listeners in a sidecar"""
        uri = f"/v1/sidecars/{sidecar_id}/listeners"
        return self.do_get(uri)

    def port_for_binding(
        self,
        sidecar_id: str,
        binding_info: Dict[str, Any],
        proxy_mode: bool = False,
    ) -> int:
        """
        port_for_binding returns the (first) sidecar listener port for the
        binding. For S3 and dynamo_db repos, the port for the specified proxy
        mode is returned.
        """
        binding_listeners: List[Dict[str, Any]] = binding_info["binding"][
            "listenerBindings"
        ]

        for binding_listener in binding_listeners:
            listener_id = binding_listener["listenerId"]
            listener_info = self.get_listener(sidecar_id, listener_id)
            listener_config = listener_info["listenerConfig"]
            repo_types = listener_config["repoTypes"]
            matched_listener = False
            if "s3" in repo_types:
                s3_settings = listener_config.get("s3Settings", {})
                if s3_settings.get("proxyMode", False) == proxy_mode:
                    matched_listener = True
            elif "dynamodb" in repo_types:
                ddb_settings = listener_config.get("dynamoDbSettings", {})
                if ddb_settings.get("proxyMode", False) == proxy_mode:
                    matched_listener = True
            else:
                # neither S3 nor dynamoDB, use the first listener we found.
                matched_listener = True
            if matched_listener:
                return listener_config["address"]["port"]

        # we didn't find any matching listener, raise an exception
        raise NoMatchingListenerException(
            "the binding has no listener with matching settings"
        )

    @staticmethod
    def endpoint(sidecar_info: Dict[str, Any]) -> Optional[str]:
        """endpoint returns the DNS name for the sidecar."""
        user_endpoint = sidecar_info.get("userEndpoint")
        return user_endpoint if user_endpoint else sidecar_info.get("endpoint")


class NoMatchingListenerException(Exception):
    """NoMatchingListenerException is raised if the binding has no listener
    with the requested settings."""
