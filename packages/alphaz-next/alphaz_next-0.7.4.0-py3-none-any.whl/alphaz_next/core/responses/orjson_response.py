# MODULES
from typing import Any as _Any, Dict as _Dict

# FASTAPI
from fastapi.responses import ORJSONResponse as _ORJSONResponse

# STARLETTE
from starlette.background import BackgroundTask as _BackgroundTask

# CORE
from alphaz_next.core._base import (
    extend_headers as _extend_headers,
    ExtHeaders as _ExtHeaders,
)


class ORJSONResponse(_ORJSONResponse):
    """
    Represents a ORJSON response that can be returned by an HTTP endpoint.
    """

    def __init__(
        self,
        content: _Any,
        status_code: int = 200,
        headers: _Dict[str, str] | None = None,
        ext_headers: _ExtHeaders | None = None,
        media_type: str | None = None,
        background: _BackgroundTask | None = None,
    ) -> None:
        """
        Initializes a new instance of the ORJSONResponse class.

        Args:
            content (Any): The response content.
            status_code (int, optional): The HTTP status code. Defaults to 200.
            headers (Dict[str, str] | None, optional): The response headers. Defaults to None.
            ext_headers (ExtHeaders | None, optional): The extended response headers. Defaults to None.
            media_type (str | None, optional): The media type of the response. Defaults to None.
            background (BackgroundTask | None, optional): The background task to be executed. Defaults to None.
        """
        headers = _extend_headers(
            headers=headers,
            ext_headers=ext_headers,
        )

        super().__init__(content, status_code, headers, media_type, background)
