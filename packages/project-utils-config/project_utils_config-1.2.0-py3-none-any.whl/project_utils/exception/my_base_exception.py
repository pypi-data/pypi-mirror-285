from typing import Optional


class MyBaseException(Exception):
    error_summary: Optional[str]
    error_detail: Optional[str]

    error_id: str = "ffe2f6c7bd8b499db440d1064103779e"

    def __init__(self, error_summary: Optional[str] = None, error_detail: Optional[str] = None, *args: ...):
        self.error_summary = error_summary
        self.error_detail = error_detail
        super().__init__(*args)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}:{self.error_summary}"
