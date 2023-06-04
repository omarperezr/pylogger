from typing import Any


class HTTPException(Exception):
    def __init__(self, status_code: int, reason: str, error: Any) -> None:
        self.status_code = status_code
        self.reason = reason
        self.error = error
        super().__init__(reason)

    def __str__(self) -> str:
        return f"{self.reason} - {self.error}"
