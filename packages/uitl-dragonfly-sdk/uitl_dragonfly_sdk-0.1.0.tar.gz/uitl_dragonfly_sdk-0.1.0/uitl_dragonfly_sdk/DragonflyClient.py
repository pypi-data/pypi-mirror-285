import json
import os
from typing import Dict, Any

import requests

from uitl_dragonfly_sdk.common.DragonflyException import DragonflyException
from uitl_dragonfly_sdk.common.LowDcrException import LowDcrException
from uitl_dragonfly_sdk.common.util import DRAGONFLY_API_HEALTH_REPORT_URL, DEFAULT_MIN_DCR, \
    resolve_mandatory_param


class DragonflyClient:
    def __init__(self: "DragonflyClient",
                 client_id: str = "",
                 client_secret: str = "",
                 auth_server_realm_baseurl: str = "",
                 api_server_baseurl: str = "") -> None:
        self.access_token = None

        client_id = resolve_mandatory_param(client_id, "UITL_DRAGONFLY_CLIENT_ID", "client_id")
        client_secret = resolve_mandatory_param(client_secret, "UITL_DRAGONFLY_CLIENT_SECRET", "client_secret")
        auth_server_realm_baseurl = resolve_mandatory_param(auth_server_realm_baseurl,
                                                            "UITL_DRAGONFLY_AUTH_SERVER_REALM_BASEURL",
                                                            "auth_server_realm_baseurl")
        api_server_baseurl = resolve_mandatory_param(api_server_baseurl,
                                                     "UITL_DRAGONFLY_API_SERVER_BASEURL",
                                                     "api_server_baseurl")

        self.auth_server_url = f"{auth_server_realm_baseurl}/protocol/openid-connect/token"
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_server_baseurl = api_server_baseurl

        env_min_dcr = os.getenv("UITL_DRAGONFLY_MINIMUM_DCR")
        self._minimum_dcr = float(env_min_dcr) if env_min_dcr is not None else DEFAULT_MIN_DCR

        self.get_new_access_token()

    @property
    def minimum_dcr(self) -> float:
        return self._minimum_dcr

    @minimum_dcr.setter
    def minimum_dcr(self, dcr: float) -> None:
        self._minimum_dcr = dcr

    def get_new_access_token(self):
        self.access_token = self.get_token()

    def get_token(self):
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", self.auth_server_url, headers=headers, data=payload, verify=False)

        if response.status_code != 200:
            raise DragonflyException("Failed to get access token. Reason: {}", response.text)

        response_data = json.loads(response.text)
        return response_data["access_token"]

    def run_health_report(self, pipeline_id: int = 0, component_id: int = 0, run_id: str = "", pipeline_name: str = "",
                          component_name: str = "", log_result: bool = False, fail_on_low_dcr: bool = False) -> Any:
        if not pipeline_id and not pipeline_name:
            raise DragonflyException("Either pipeline_id or pipeline_name must be provided.")

        health_report_url = self.api_server_baseurl + DRAGONFLY_API_HEALTH_REPORT_URL
        headers = self.build_auth_headers()

        payload: Dict[str, int | str] = {}
        if pipeline_id != 0:
            payload["pipelineId"] = pipeline_id
        if component_id != 0:
            payload["componentId"] = component_id
        if pipeline_name != "":
            payload["pipelineName"] = pipeline_name
        if component_name != "":
            payload["componentName"] = component_name
        if run_id != "":
            payload["runId"] = run_id

        response = requests.request("POST", health_report_url, headers=headers, json=payload, verify=False)

        if response.status_code != 200:
            raise DragonflyException("Failed to execute health report. Reason: {}", response.text)

        health_log = response.json()

        if not component_id and not component_name:  # pipeline level run
            if log_result:
                self.print_pipeline_health(health_log)

            if fail_on_low_dcr:
                print("Failing on low DCR is currently supported only for component level executions.")

        else:
            component_health = self.find_component_health(health_log["nodes"], component_name, component_id)

            if log_result:
                self.print_component_health_wrapper(component_health)

            if fail_on_low_dcr and self.is_component_dcr_low(component_health):
                if not log_result:
                    self.print_component_health_wrapper(component_health)

                raise LowDcrException("Component health did not meet minimum required health criteria to proceed!")

        return health_log

    def build_auth_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.access_token}"
        }

    def is_component_dcr_low(self, component_health: Dict[str, Any]) -> bool:
        return component_health["health"]["value"] <= self._minimum_dcr

    # @staticmethod
    def find_component_health(self, nodes_health_log: Any, component_name: str = "", component_id: int = 0) -> Any:
        for i in nodes_health_log:
            if i["name"] == component_name or i["id"] == component_id:
                return i

        return {"health": 0.0}

    # @staticmethod
    def print_pipeline_health(self, health_log: Any) -> None:
        print("============================== Dragonfly Log: Start ==============================")
        print(f"Pipeline Name: {health_log['name']}")
        print(f"Pipeline Id: {health_log['id']}")
        for i in health_log["nodes"]:
            self.print_component_health(i)
        print("=============================== Dragonfly Log: End ===============================")

    def print_component_health_wrapper(self, component_health_log: Any):
        print("============================== Dragonfly Log: Start ==============================")
        self.print_component_health(component_health_log)
        print("=============================== Dragonfly Log: End ===============================")

    # @staticmethod
    def print_component_health(self, component_health_log: Any):
        print("-------------------------------- Component: Start --------------------------------")
        print(f"Component Name: {component_health_log['name']}")
        print(f"Component Id: {component_health_log['id']}")
        print(f"Component Health: {component_health_log['health']['value']}")
        print(f"Component Dependencies Health: {component_health_log['health']['dependenciesHealth']}")
        print("Executed Checks:")
        for ch in (component_health_log['health']["executedChecks"] or []):
            print("----- Dragonfly Check Result -----")
            print(f"\tCheck Name: {ch['healthCheckName']}")
            print(f"\tCheck Result Health: {ch['value']}")
            print(f"\tCheck Additional Information: {ch['meta']}")
            print("----------------------------------")
        print("-------------------------------- Component: End ----------------------------------")
