import os

from uitl_dragonfly_sdk.common.DragonflyException import DragonflyException


def resolve_mandatory_param(provided_val: str, env_var_name: str, param_name: str):
    param = provided_val or str(os.getenv(env_var_name))
    verify_mandatory_param(param, param_name)
    return param


def verify_mandatory_param(param: str, name: str) -> None:
    if not param:
        raise DragonflyException("Mandatory parameter missing: {}", name)


DRAGONFLY_API_HEALTH_REPORT_URL = "/api/health-reports"
DEFAULT_MIN_DCR = 95.0
