import dataclasses
import logging
import subprocess
from dataclasses import dataclass
from typing import Any, Literal, Optional

import lastmile_utils.lib.core.api as core_utils
from aiconfig import DefaultOpenAIParser, ModelParserRegistry
from pydantic import BaseModel, field_validator


from lastmile_eval.rag.debugger.common.utils import ServerMode
from lastmile_eval.rag.debugger.model_settings_schemas.openai_model_settings_schema import (
    OpenAIModelSettingsSchema,
)
from lastmile_eval.rag.debugger.common.utils import get_website_base_url

logger = logging.getLogger(__name__)
logging.basicConfig()


class LaunchConfig(core_utils.Record):
    run_llm_script_path: Optional[str] = None
    run_llm_timeout_s: int = 2
    server_port: int = 8000
    server_mode: ServerMode = ServerMode.PROD
    # TODO:
    # env_file_path: Optional[str] = None

    @field_validator("server_mode", mode="before")
    def convert_to_mode(cls, value: Any) -> ServerMode:
        # pylint: disable=no-self-argument
        if isinstance(value, str):
            try:
                return ServerMode[value.upper()]
            except KeyError as e:
                raise ValueError(f"Unexpected value for mode: {value}") from e
        return value


@dataclass
class AppState:
    server_mode: ServerMode = ServerMode.PROD
    run_llm_script_path: str | None = None
    run_llm_script_timeout_s: int = 2


def update_app_state_from_launch_config(
    launch_config: LaunchConfig, app_state: AppState
):
    app_state = dataclasses.replace(
        app_state,
        server_mode=launch_config.server_mode,
        run_llm_script_path=launch_config.run_llm_script_path,
        run_llm_script_timeout_s=launch_config.run_llm_timeout_s,
    )
    return app_state


def run_frontend_server_background(client_dir: str) -> bool:
    logger.info("Running frontend server in background")
    # Yarn settles dependencies
    subprocess.Popen(["yarn"], cwd=client_dir)

    # Start the frontend server
    subprocess.Popen(
        ["yarn", "start"],
        cwd=client_dir,
        stdin=subprocess.PIPE,
    )

    return True


def get_lastmile_endpoint(api_route: str, server_mode: ServerMode):
    """
    Get the lastmile endpoint for a given route.
    """
    if server_mode == ServerMode.DEBUG:
        return f"http://localhost:3000/api/{api_route}"
    else:
        return get_website_base_url() + f"/api/{api_route}"


def initialize_model_registry():
    """
    Initialize the model registry with the desired models.
    """
    ModelParserRegistry.clear_registry()
    openai_models = [
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-4",
        "gpt-4-32k",
    ]
    for model in openai_models:
        ModelParserRegistry.register_model_parser(DefaultOpenAIParser(model))


def get_settings_schema_for_model(_model: str):
    """
    Get the settings schema for the model.
    """
    # TODO: Dynamically handle other model settings schemas
    return OpenAIModelSettingsSchema()


PromptMessageRole = Literal["user", "system", "assistant"]


class PromptMessage(core_utils.Record):
    role: PromptMessageRole
    content: str


class AIConfigPromptContainer(BaseModel):
    messages: list[PromptMessage]
    model_name: str
    inference_kwargs: dict[str, Any]
