# MODULES
import logging as _logging
from logging.handlers import TimedRotatingFileHandler as _TimedRotatingFileHandler
from pathlib import Path as _Path
import sys as _sys
from typing import (
    Any as _Any,
    Dict as _Dict,
    List as _List,
    Optional as _Optional,
    Sequence as _Sequence,
    Union as _Union,
)

# FASTAPI
from fastapi import (
    APIRouter as _APIRouter,
    FastAPI as _FastAPI,
    HTTPException as _HTTPException,
    Request as _Request,
    Response as _Response,
)
from fastapi.exceptions import RequestValidationError as _RequestValidationError
from fastapi.exception_handlers import http_exception_handler as _http_exception_handler
from fastapi.exception_handlers import (
    request_validation_exception_handler as _request_validation_exception_handler,
)
from fastapi.openapi.docs import (
    get_swagger_ui_html as _get_swagger_ui_html,
    get_redoc_html as _get_redoc_html,
)
from fastapi.openapi.utils import get_openapi as _get_openapi
from fastapi.responses import (
    HTMLResponse as _HTMLResponse,
    JSONResponse as _JSONResponse,
    PlainTextResponse as _PlainTextResponse,
    RedirectResponse as _RedirectResponse,
)

# STARLETTE
from starlette.routing import BaseRoute as _BaseRoute
from starlette.types import Lifespan as _Lifespan

# MODELS
from alphaz_next.models.config.alpha_config import (
    AlphaConfigSchema as _AlphaConfigSchema,
)

# CORE
from alphaz_next.core._middleware import (
    log_request_middleware as _log_request_middleware,
    CORSMiddleware as _CORSMiddleware,
)
from alphaz_next.core._telemetry import setup_telemetry

# UTILS
# UTILS
from alphaz_next.utils.logging_filters import (
    ExcludeRoutersFilter as _ExcludeRoutersFilter,
)

_DEFAULT_FAVICON_URL = "https://fastapi.tiangolo.com/img/favicon.png"

_uvicorn_access = _logging.getLogger("uvicorn.access")
_uvicorn_access.disabled = True

uvicorn_logger = _logging.getLogger("uvicorn")


def _custom_openapi(
    config: _AlphaConfigSchema,
    routes: _List[_BaseRoute],
) -> _Dict[str, _Any]:
    """
    Generate a custom OpenAPI schema based on the provided configuration and routes.

    Args:
        config (AlphaConfigSchema): The configuration object containing project settings.
        routes (List[BaseRoute]): The list of routes to include in the OpenAPI schema.

    Returns:
        Dict[str, Any]: The generated OpenAPI schema.
    """
    title = config.project_name.upper()
    if config.environment.lower() != "prod":
        title = f"{title} [{config.environment.upper()}]"

    openapi_dict: _Dict[str, _Any] = {}
    if (openapi_config := config.api_config.openapi) is not None:
        openapi_dict["description"] = openapi_config.description
        openapi_dict["tags"] = openapi_config.tags

        if openapi_config.contact is not None:
            openapi_dict["contact"] = {
                "name": openapi_config.contact.name,
                "email": openapi_config.contact.email,
            }

    openapi_schema = _get_openapi(
        title=title,
        version=config.version,
        routes=routes,
        **openapi_dict,
    )

    return openapi_schema


def create_app(
    config: _AlphaConfigSchema,
    routes: _Optional[_List[_BaseRoute]] = None,
    routers: _Optional[_List[_APIRouter]] = None,
    lifespan: _Optional[_Lifespan[_FastAPI]] = None,
    allow_origins: _Sequence[str] = (),
    allow_methods: _Sequence[str] = ("GET",),
    allow_headers: _Sequence[str] = (),
    allow_credentials: bool = False,
    allow_private_network: bool = False,
    status_response: _Dict[str, _Any] = {"status": "OK"},
) -> _FastAPI:
    """
    Create a FastAPI application with the specified configuration.

    Args:
        config (AlphaConfigSchema): The configuration for the application.
        routes (Optional[List[BaseRoute]]): The list of routes to include in the application. Defaults to None.
        routers (Optional[List[APIRouter]]): The list of API routers to include in the application.
        container (Optional[containers.DeclarativeContainer]): The dependency injection container. Defaults to None.
        allow_origins (Sequence[str]): The list of allowed origins for CORS. Defaults to ().
        allow_methods (Sequence[str]): The list of allowed HTTP methods for CORS. Defaults to ("GET",).
        allow_headers (Sequence[str]): The list of allowed headers for CORS. Defaults to ().
        allow_credentials (bool): Whether to allow credentials for CORS. Defaults to False.
        allow_private_network (bool): Whether to allow private network for CORS. Defaults to False.
        status_response (Dict): The response to return for the "/status" endpoint. Defaults to {"status": "OK"}.

    Returns:
        FastAPI: The created FastAPI application.
    """

    # APP
    app = _FastAPI(
        routes=routes,
        title=config.project_name.upper(),
        version=config.version,
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(
        _CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        allow_private_network=allow_private_network,
    )

    app.middleware("http")(_log_request_middleware)

    setup_telemetry(config=config, app=app)

    for router in routers or []:
        app.include_router(router)

    app.openapi_schema = _custom_openapi(config=config, routes=app.routes)

    swagger_favicon_url = _DEFAULT_FAVICON_URL
    redoc_favicon_url = _DEFAULT_FAVICON_URL
    if (openapi_config := config.api_config.openapi) is not None:
        if openapi_config.swagger_favicon_url:
            swagger_favicon_url = openapi_config.swagger_favicon_url

        if openapi_config.redoc_favicon_url:
            redoc_favicon_url = openapi_config.redoc_favicon_url

    if (
        config.api_config.logging is not None
        and config.api_config.logging.rotation is not None
        and config.api_config.logging.retention is not None
    ):
        uvicorn_formatter = _logging.Formatter(
            config.api_config.logging.uvicorn_format,
            datefmt=config.api_config.logging.date_format,
        )

        directory_path = _Path(config.api_config.directories.logs)
        directory_path.mkdir(parents=True, exist_ok=True)

        handler = _TimedRotatingFileHandler(
            filename=directory_path / "uvicorn.log",
            when=config.api_config.logging.rotation,
            backupCount=config.api_config.logging.retention,
        )
        handler.setFormatter(uvicorn_formatter)

        uvicorn_logger.addHandler(handler)

        telemetry_handler = app.extra.get("telemetry_handler")
        if telemetry_handler is not None:
            uvicorn_logger.addHandler(telemetry_handler)

        uvicorn_logger.addFilter(
            _ExcludeRoutersFilter(
                router_names=config.api_config.logging.excluded_routers
            )
        )

    @app.exception_handler(_RequestValidationError)
    async def request_validation_exception_handler(
        request: _Request, exc: _RequestValidationError
    ) -> _JSONResponse:
        """
        This is a wrapper to the default RequestValidationException handler of FastAPI.
        This function will be called when client input is not valid.
        """
        body = await request.body()
        query_params = request.query_params._dict
        detail = {
            "errors": exc.errors(),
            "body": body.decode(),
            "query_params": query_params,
        }

        uvicorn_logger.info(detail)
        return await _request_validation_exception_handler(request, exc)

    @app.exception_handler(_HTTPException)
    async def http_exception_handler(
        request: _Request, exc: _HTTPException
    ) -> _Union[_JSONResponse, _Response]:
        """
        This is a wrapper to the default HTTPException handler of FastAPI.
        This function will be called when a HTTPException is explicitly raised.
        """
        return await _http_exception_handler(request, exc)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: _Request, exc: Exception
    ) -> _PlainTextResponse:
        """
        This middleware will log all unhandled exceptions.
        Unhandled exceptions are all exceptions that are not HTTPExceptions or RequestValidationErrors.
        """
        host = getattr(getattr(request, "client", None), "host", None)
        port = getattr(getattr(request, "client", None), "port", None)
        url = (
            f"{request.url.path}?{request.query_params}"
            if request.query_params
            else request.url.path
        )
        exception_type, exception_value, exception_traceback = _sys.exc_info()
        exception_name = getattr(exception_type, "__name__", None)

        uvicorn_logger.error(
            f'{host}:{port} - "{request.method} {url}" 500 Internal Server Error <{exception_name}: {exception_value}>'
        )
        return _PlainTextResponse(str(exc), status_code=500)

    @app.get("/status", include_in_schema=False)
    async def get_api_status() -> _Dict[str, _Any]:
        return status_response

    @app.get("/docs", include_in_schema=False)
    def swagger_ui_html(req: _Request) -> _HTMLResponse:
        root_path = req.scope.get("root_path", "").rstrip("/")

        openapi_url = root_path
        if app.openapi_url is not None:
            openapi_url += app.openapi_url

        oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url
        if oauth2_redirect_url:
            oauth2_redirect_url = root_path + oauth2_redirect_url

        return _get_swagger_ui_html(
            openapi_url=openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=oauth2_redirect_url,
            init_oauth=app.swagger_ui_init_oauth,
            swagger_favicon_url=swagger_favicon_url,
            swagger_ui_parameters=app.swagger_ui_parameters,
        )

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html() -> _HTMLResponse:
        if app.openapi_url is None:
            raise _HTTPException(
                status_code=404, detail="No OpenAPI URL has been provided."
            )
        return _get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
            redoc_favicon_url=redoc_favicon_url,
        )

    @app.get("/")
    async def home() -> _RedirectResponse:
        return _RedirectResponse("/docs")

    return app
