"""
Utils file for various needs in the RAG debugger. 

Note: DO NOT IMPORT ANY UI DEPENDENCIES HERE. This file should be UI agnostic.
"""

import logging
import os
from enum import Enum
from textwrap import dedent
from typing import Mapping, Optional
from urllib.parse import urlencode

import lastmile_utils.lib.core.api as core_utils
import requests
from dotenv import find_dotenv, load_dotenv
from lastmile_eval.rag.debugger.common.general_functional_utils import (
    exn_to_err,
)
from lastmile_eval.rag.debugger.common.types import (
    APIToken,
    ParsedHTTPResponse,
    ProjectID,
    ProjectName,
    Res,
    T_Inv,
)
from requests import Response
from result import do, Err, Ok, Result

SHOW_DEBUG = False
LASTMILE_SPAN_KIND_KEY_NAME = "lastmile.span.kind"
WEBSITE_BASE_URL = "https://lastmileai.dev"

DEFAULT_PROJECT_ID = ProjectID("default")
DEFAULT_PROJECT_NAME = ProjectName("default")


class Singleton:
    """
    Define a Singleton object that we can extend to create singleton classes.
    This is needed/helpful for ensuring trace-level data is the same when used
    across multiple classes. An alternative to using a singleton is ensuring
    that a shared state object is passed around correctly to all callsites

    This implementation is what's found on the Python docs:
    https://www.python.org/download/releases/2.2/descrintro/#__new__
    Please note that it is not thread-safe
    """

    def __new__(cls, *args, **kwargs):  # type: ignore[errggh *pukes*]
        it = cls.__dict__.get("__it__")  # dude
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwargs)  # type: ignore[im going to pretend i didnt see that *pukes*]
        return it

    def init(self, *args, **kwargs):  # type: ignore[mate]
        """
        Sets the _is_already_initialized flag to True. Use this in your
        cubslass with the following implementation

        class MySingleton(Singleton):
            _is_already_initialized = False

            def __init__(self):
                if self._is_already_initialized:
                    return
                super().__init__()
                # Other logic here to initialize singleton once
                ...
                _is_already_initialized = False
        """


def raise_for_status(response: Response, message: str) -> None:
    """
    Raise an HTTPError exception if the response is not successful
    """
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        raise requests.HTTPError(f"{message}: {response.content}") from e


def log_for_status(
    response: Response, message: str, logger: Optional[logging.Logger] = None
) -> Result[Response, requests.HTTPError]:
    """
    Checks the status of an HTTP response and logs an error if the response is not successful.

    Args:
        response (Response): The HTTP response object to check.
        error_message (str): The error message to include in the log.

    Returns:
        Result[Response, requests.HTTPError]:
            - If the response is successful (status code in the 2xx range), returns Ok(response).
            - If the response is not successful, logs an error and returns Err(requests.HTTPError).

    Raises:
        None

    Example:
        response = requests.get("https://api.example.com/data")
        result = log_for_status(response, "Failed to fetch data")
        match result:
            case Ok(response):
                # Handle successful response
                pass
            case Err(http_error):
                # Handle the specific HTTPError exception
                pass
    """
    try:
        response.raise_for_status()
        return Ok(response)
    except requests.HTTPError as e:
        if logger:
            logger.error(
                "%s: %s - %s - %s",
                message,
                response.status_code,
                response.reason,
                response.text,
                stack_info=True,
            )  # % formatting is preferred over fstrings by logging lib
        else:
            logging.error(
                "%s: %s - %s - %s",
                message,
                response.status_code,
                response.reason,
                response.text,
                stack_info=True,
            )  # % formatting is preferred over fstrings by logging lib
        return Err(e)


class ServerMode(str, Enum):
    """
    Server mode dictates how the application is run and how it communicates with
    the lastmile endpoints.

    PROD: The application is run with bundled frontend assets and hits the production
    lastmileai.dev endpoints.

    DEBUG: The application is run with the frontend server running in the background
    on port 3001 and hits the localhost:3000 lastmile endpoints.
    """

    DEBUG = "DEBUG"
    PROD = "PROD"


def load_dotenv_from_cwd() -> bool:
    """
    Helper method needed to ensure that when we load the .env file, we load it
    from user's current cwd, not the published package location, which could
    otherwise lead to error since we wil lbe unable to detect an .env file.
    """
    dotenv_path = find_dotenv(usecwd=True)
    return load_dotenv(dotenv_path=dotenv_path)


def load_api_token(server_mode: ServerMode):
    """
    Load the Lastmile API token from the environment.
    """
    load_dotenv_from_cwd()

    token_key = (
        "LASTMILE_API_TOKEN_DEV"
        if server_mode == ServerMode.DEBUG
        else "LASTMILE_API_TOKEN"
    )

    token = os.getenv(token_key)
    if token is None:
        raise ValueError(
            dedent(
                f"""Missing API token: {token_key}.
            * If you don't have a LastMile token:
                please log in here https://lastmileai.dev/settings?page=tokens
                then click "Create new token" next to "API Tokens".
            * Once you have your token:
                please create a .env file in your current directory, 
                and add the following entry:
                {token_key}=<your token>
            * Then, restart the application.

            """
            )
        )

    return token


def load_project_name() -> Optional[ProjectName]:
    """
    Load the Lastmile Project Name from the environment.
    """
    load_dotenv_from_cwd()

    project_name = os.getenv("LASTMILE_PROJECT_NAME")
    return ProjectName(project_name) if project_name else None


def get_lastmile_api_token(
    lastmile_api_token: Optional[str] = None,
) -> APIToken:
    """
    Helper function to get the LastMile API token. If the lastmile_api_token
    is None, then we try to get the token from the environment variables. If
    the token is still None, then we raise a ValueError.

    @param lastmile_api_token Optional(str): The LastMile API token to use.
        If None, then we try to get the token from the environment variables

    @return str: The LastMile API token to use
    """
    if lastmile_api_token is not None:
        return APIToken(lastmile_api_token)
    return APIToken(load_api_token(ServerMode.PROD))


def get_auth_header(lastmile_api_token: APIToken):
    return {
        "Authorization": f"Bearer {lastmile_api_token}",
    }


def http_get(
    base_url: str,
    endpoint: str,
    headers: dict[str, str],
    timeout: int = 60,
) -> Res[requests.Response]:
    url = os.path.join(base_url, "api", endpoint)

    raw = requests.get(url, headers=headers, timeout=timeout)
    if raw.status_code != 200:
        return Err(
            ValueError(
                f"LastMile website returned error:\n{raw.text[:100]}..."
            )
        )
    return Ok(raw)


@exn_to_err
def http_post(
    base_url: str,
    endpoint: str,
    headers: dict[str, str],
    json: core_utils.JSONDict,
    timeout: int = 60,
) -> requests.Response:
    return requests.post(
        os.path.join(base_url, "api", endpoint),
        headers=headers,
        json=json,
        timeout=timeout,
    )


@exn_to_err
def _http_response_to_json(
    response: requests.Response,
):
    out = response.json()
    return out


def http_post_and_response_id_lookup(
    base_url: str,
    endpoint: str,
    headers: dict[str, str],
    json: core_utils.JSONDict,
) -> Res[ParsedHTTPResponse]:
    response = http_post(base_url, endpoint, headers, json)

    outcome: Res[ParsedHTTPResponse] = do(
        Ok(
            ParsedHTTPResponse(
                returned_id=id_ok,
                status_code=response_ok.status_code,
                text=response_ok.text,
            )
        )
        for response_ok in response
        for response_json_ok in _http_response_to_json(response_ok)
        for id_ok in key_lookup("id", response_json_ok).map_err(
            lambda _: ValueError(  # type: ignore[fixme]
                f"Expected 'id' in response ({base_url, endpoint}, {json}, {response_json_ok=}, {response_ok.text=})"
            )
        )
    )
    return outcome


def key_lookup(key: str, mapping: Mapping[str, T_Inv]) -> Res[T_Inv]:
    try:
        return Ok(mapping[key])
    except KeyError as e:
        # TODO(jll) return instead of printing this stuff
        # logger.error(f"Key not found: {key}, existing keys: {mapping.keys()}")
        # logger.error("\n".join(traceback.format_stack()))
        # logger.error(traceback.format_exc())
        return Err(e)


def get_project_id(
    project_name: ProjectName,
    lastmile_api_token: APIToken,
    create_if_not_exists: bool = False,
) -> Res[ProjectID]:
    """
    Return project ID for the requested name if it exists. If there is no
    project found with the given name and create_if_not_exists is True, then
    create a new project with the given name and return the project ID. If
    create_if_not_exists is False, then return an error.
    TODO (rossdan): Investigate into looking into sentinel value for
    project name instead
    """
    if project_name == DEFAULT_PROJECT_NAME:
        return Ok(DEFAULT_PROJECT_ID)

    list_project_endpoint = (
        f"evaluation_projects/list?{urlencode({'name': project_name})}"
    )
    headers = get_auth_header(lastmile_api_token)
    response = http_get(WEBSITE_BASE_URL, list_project_endpoint, headers)

    def _get_or_create_project_id(
        response_from_list_endpoint: requests.Response,
    ) -> Res[ProjectID]:
        # TODO (rossdan): Use @safe_res once that lands: https://github.com/lastmile-ai/eval/pull/723/files
        def _parse_project_id_from_list_response(
            response: requests.Response,
        ) -> Optional[ProjectID]:
            raw_projects = response.json()["evaluationProjects"]
            if len(raw_projects) == 0:
                return None
            return ProjectID(raw_projects[0]["id"])

        try:
            parsed_project_id = _parse_project_id_from_list_response(
                response_from_list_endpoint
            )
        except Exception as e:
            return Err(e)

        if parsed_project_id is not None:
            return Ok(parsed_project_id)

        if not create_if_not_exists:
            return Err(
                ValueError(
                    f"Project with name {project_name} does not exist and we are not allowed to create a new project in this API call."
                )
            )

        # project does not exist, create a new one
        create_project_endpoint = "evaluation_projects/create"
        parsed_http_response = http_post_and_response_id_lookup(
            WEBSITE_BASE_URL,
            create_project_endpoint,
            headers,
            {"name": project_name},
        )
        project_id: Res[ProjectID] = do(
            Ok(ProjectID(parsed_http_response_ok.returned_id))
            for parsed_http_response_ok in parsed_http_response
        )
        return project_id

    return response.and_then(_get_or_create_project_id)
