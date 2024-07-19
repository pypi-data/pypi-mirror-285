from typing import Any, Optional

from uitl_dragonfly_sdk.common.DragonflyException import DragonflyException


class LowDcrException(DragonflyException):
    def __init__(self, message: str, *params: Any, e: Optional[Exception] = None) -> None:
        super().__init__(message, params, e)
        self.message = message
