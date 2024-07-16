import dataclasses
import json
import logging
import os
import socket
from textwrap import dedent

import uvicorn
from result import Err, Ok, Result

from lastmile_eval.rag.debugger.app import CLIENT_DIR, get_request
from lastmile_eval.rag.debugger.app_utils import (
    AppState,
    LaunchConfig,
    run_frontend_server_background,
    update_app_state_from_launch_config,
)

from lastmile_eval.rag.debugger.common.utils import ServerMode, load_api_token
from lastmile_eval.rag.debugger.common.types import APIToken

logger = logging.getLogger(__name__)
logging.basicConfig()

ACCEPTABLE_ERROR_STATUS_CODES = [
    200,
    201,  # This is specifically for CORS policy for upload logging files to AWS S3
]


def serve(launch_config: LaunchConfig) -> Result[str, str]:
    should_reload = launch_config.server_mode != "PROD"
    app_state = update_app_state_from_launch_config(launch_config, AppState())

    # TODO: un-jank this (do it in memory)
    home_dir_path = os.path.expanduser("~")

    new_directory_path = os.path.join(home_dir_path, ".lastmile/rag-debugger")
    os.makedirs(new_directory_path, exist_ok=True)

    file_path = os.path.join(new_directory_path, "initial_app_state.json")
    with open(file_path, "w") as f:
        f.write(json.dumps(dataclasses.asdict(app_state), indent=2))
        logger.debug(f"Wrote initial app state to initial_app_state.json")

    if launch_config.server_mode == ServerMode.DEBUG:
        run_frontend_server_background(CLIENT_DIR)

    resp = get_request(
        "tokens/list",
        launch_config.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )
    if (
        "status" in resp
        and resp["status"] not in ACCEPTABLE_ERROR_STATUS_CODES
    ):
        return Err(
            dedent(
                f"""
                LastMile token did not work. Please double check:
                * your .env
                * your LastMile account (https://lastmileai.dev/settings?page=tokens)
                    You can create a new token if necessary.

                LastMile server returned:
                {resp}
                """
            )
        )
    else:
        logger.info("Token is good. Starting server.")

        port = launch_config.server_port
        while is_port_in_use(port):
            port += 1

        if port != launch_config.server_port:
            logger.warning(
                f"Ports {launch_config.server_port} through {port - 1} are in use. "
                f"Using {port} instead."
            )

        uvicorn.run(
            "lastmile_eval.rag.debugger.app:app",
            port=port,
            log_level=logger.level,
            reload=should_reload,
        )

        return Ok("Stopped serving.")


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0
