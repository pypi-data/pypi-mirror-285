from typing import Any, Optional


class DragonflyException(Exception):
    def __init__(self, message: str, *params: Any, e: Optional[Exception] = None) -> None:
        if e is None:
            message = DragonflyException.get_formatted_message(message, *params)
            super().__init__(message)
        else:
            message = DragonflyException.get_formatted_message_with_exception(e, message, *params)
            super().__init__(message, e)
            self.original_exception = e

        self.message = message

    @staticmethod
    def get_formatted_message(message: str, *params: Any) -> str:
        return message.format(*params)

    @staticmethod
    def get_formatted_message_with_exception(e: Exception, message: str, *params: Any) -> str:
        return f"{DragonflyException.get_formatted_message(message, params)}; Original Exception: {e}"
