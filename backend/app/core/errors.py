from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class AppError(Exception):
    status_code: int
    error_code: str
    message: str
    field_errors: Optional[Dict[str, List[str]]] = None


def build_error_payload(
    error_code: str,
    message: str,
    field_errors: Optional[Dict[str, List[str]]] = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "error_code": error_code,
        "message": message,
    }
    if field_errors:
        payload["field_errors"] = field_errors
    return payload
