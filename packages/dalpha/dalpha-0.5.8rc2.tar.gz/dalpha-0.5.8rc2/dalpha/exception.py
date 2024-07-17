from enum import Enum
from typing import Dict

class BaseStatusCode(Enum):
    BAD_REQUEST = 400
    CONFLICT = 409
    INTERNAL_ERROR = 525

    def __str__(self):
        return f"({self.value})"

class WaitException(Exception):
    def __init__(self, message: str = "Wait Exception occurred"):
        super().__init__(message)


class ExpectedError(Exception):
    def __init__(self, error_json: Dict, error_code: BaseStatusCode = BaseStatusCode.INTERNAL_ERROR, message: str = "Expected Error occured"):
        super().__init__(message)
        self.error_json = error_json
        self.error_code = error_code
