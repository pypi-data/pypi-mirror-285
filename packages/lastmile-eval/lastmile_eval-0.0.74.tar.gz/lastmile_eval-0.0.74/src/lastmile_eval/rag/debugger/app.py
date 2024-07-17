import asyncio
import dataclasses
import json
import logging
import os
import subprocess
import sys
from typing import Any
from urllib.parse import urlencode

from lastmile_eval.rag.debugger.common.utils import load_dotenv_from_cwd

from fastapi.responses import StreamingResponse
import lastmile_utils.lib.core.api as core_utils
import requests
from aiconfig import AIConfigRuntime, ModelParserRegistry, Prompt
from fastapi import Depends, FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from result import Err, Ok

from lastmile_eval.rag.debugger.common.utils import ServerMode, load_api_token
from lastmile_eval.rag.debugger.model_settings_schemas.prompt_model_settings_schema import (
    PromptModelSettingsSchema,
)
import lastmile_eval.rag.debugger.prompt_iteration.run_user_llm_script as lib_run_user_llm_script
from lastmile_eval.rag.debugger.app_utils import (
    AIConfigPromptContainer,
    AppState,
    get_lastmile_endpoint,
    get_settings_schema_for_model,
    initialize_model_registry,
)
from lastmile_eval.rag.debugger.common.types import APIToken

logger = logging.getLogger(__name__)
logging.basicConfig()


app = FastAPI()

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_DIR = os.path.join(THIS_DIR, "client")
BUILD_DIR = os.path.join(CLIENT_DIR, "build")
STATIC_DIR = os.path.join(BUILD_DIR, "static")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=BUILD_DIR)


origins = [
    "http://localhost:3001",  # dev client
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app_state = None

initialize_model_registry()


class AddOrRemoveTagsData(core_utils.Record):
    """
    Data for adding or removing tags to/from a an entity with id.
    """

    id: str
    tagIds: list[str]


class EvaluationTestCaseData(core_utils.Record):
    # TODO: Why is this erroring?
    # query: core_utils.JSONValue
    # context: core_utils.JSONValue | None = None
    # fullyResolvedPrompt: core_utils.JSONValue | None = None
    # output: core_utils.JSONValue | None = None
    # groundTruth: core_utils.JSONValue | None = None
    # metadata: core_utils.JSONObject | None = None
    # traceId: str | None = None
    input: str | list[str] | dict[str, Any]
    query: str | list[str] | dict[str, Any] | None = None
    context: str | list[str] | dict[str, Any] | None = None
    fullyResolvedPrompt: str | list[str] | dict[str, Any] | None = None
    output: str | list[str] | dict[str, Any] | None = None
    groundTruth: str | list[str] | dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    traceId: str | None = None


def read_global_app_state():
    try:
        # TODO: un-jank this (do it in memory)
        home_dir_path = os.path.expanduser("~")

        new_directory_path = os.path.join(
            home_dir_path, ".lastmile/rag-debugger"
        )
        os.makedirs(new_directory_path, exist_ok=True)

        file_path = os.path.join(new_directory_path, "initial_app_state.json")
        with open(file_path, "r") as f:
            contents = f.read()
            # print(f"Contents: {contents}")
            loaded = json.loads(contents)
            # print(f"Loaded: {loaded}")
            app_state = AppState(**loaded)
            logger.info(f"Loaded initial app state from json file")
            return app_state
    except Exception as e:
        logger.error(f"Failed to load initial app state: {e}")

        return AppState()


def get_app_state() -> AppState:
    global app_state
    if app_state is None:
        app_state = read_global_app_state()

    return app_state


def get_request(
    api_route: str, server_mode: ServerMode, lastmile_api_token: APIToken
):
    """
    Make a GET request to the lastmile API for given route.
    """

    global app_state
    res = requests.get(
        get_lastmile_endpoint(api_route, server_mode),
        headers={"Authorization": f"Bearer {lastmile_api_token}"},
        timeout=30,
    )
    return res.json()


def post_request(
    api_route: str,
    data: dict[str, Any],
    server_mode: ServerMode,
    lastmile_api_token: APIToken,
):
    """
    Make a POST request to the lastmile API for given route.
    """

    global app_state
    res = requests.post(
        get_lastmile_endpoint(api_route, server_mode),
        headers={
            "Authorization": f"Bearer {lastmile_api_token}",
            "Content-Type": "application/json",
        },
        json=data,
        timeout=30,
    )
    return res.json()


def put_request(
    api_route: str,
    data: dict[str, Any],
    server_mode: ServerMode,
    lastmile_api_token: APIToken,
):
    """
    Make a POST request to the lastmile API for given route.
    """

    global app_state
    res = requests.put(
        get_lastmile_endpoint(api_route, server_mode),
        headers={
            "Authorization": f"Bearer {lastmile_api_token}",
            "Content-Type": "application/json",
        },
        json=data,
        timeout=30,
    )
    return res.json()


@app.get("/app_state")
def test_app_state(app_state: AppState = Depends(get_app_state)):
    """
    Get the current app state.
    """
    return {"state": dataclasses.asdict(app_state)}


@app.get("/api/evaluation_feedback/list")
def list_evaluation_feedback(
    search: str | None = None,
    pageSize: int | None = None,
    cursor: str | None = None,
    projectId: str | None = None,
    traceId: str | None = None,
    spanId: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    List evaluation feedback.
    """
    params = {
        "search": search,
        "pageSize": pageSize,
        "cursor": cursor,
        "projectId": projectId,
        "traceId": traceId,
        "spanId": spanId,
    }
    params = {key: value for key, value in params.items() if value is not None}
    encoded_params = urlencode(params)
    api_route = f"evaluation_feedback/list?{encoded_params}"

    return get_request(
        api_route,
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.get("/api/evaluation_projects/list")
def list_evaluation_projects(
    search: str | None = None,
    pageSize: int | None = None,
    cursor: str | None = None,
    name: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    List evaluation projects.
    """
    params = {
        "search": search,
        "pageSize": pageSize,
        "cursor": cursor,
        "name": name,
    }
    params = {key: value for key, value in params.items() if value is not None}
    encoded_params = urlencode(params)
    api_route = f"evaluation_projects/list?{encoded_params}"

    return get_request(
        api_route,
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.get("/api/evaluation_projects/read")
def get_evaluation_project(
    id: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    Get an evaluation set by ID.
    """
    return get_request(
        f"evaluation_projects/read?id={id}",
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.get("/api/evaluation_sets/read")
def get_evaluation_set(
    id: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    Get an evaluation set by ID.
    """
    return get_request(
        f"evaluation_sets/read?id={id}",
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.get("/api/evaluation_sets/list")
def list_evaluation_sets(
    search: str | None = None,
    sort: str | None = None,
    pageSize: int | None = None,
    cursor: str | None = None,
    projectId: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    List evaluation sets.
    """
    params = {
        "search": search,
        "sort": sort,
        "pageSize": pageSize,
        "cursor": cursor,
        "projectId": projectId,
    }
    params = {key: value for key, value in params.items() if value is not None}
    encoded_params = urlencode(params)
    api_route = f"evaluation_sets/list?{encoded_params}"

    return get_request(
        api_route,
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.get("/api/evaluation_sets/run_details")
def get_evaluation_set_run_details(
    id: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    Get an evaluation set run details by ID.
    """
    return get_request(
        f"evaluation_sets/run_details?id={id}",
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.get("/api/evaluation_test_cases/list")
def list_evaluation_test_cases(
    evaluationSetId: str | None = None,
    testSetId: str | None = None,
    search: str | None = None,
    sort: str | None = None,
    tag: str | None = None,
    feedback: str | None = None,
    pageSize: int | None = None,
    cursor: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    List evaluation test cases.
    """
    params = {
        "evaluationSetId": evaluationSetId,
        "testSetId": testSetId,
        "search": search,
        "sort": sort,
        "tag": tag,
        "feedback": feedback,
        "pageSize": pageSize,
        "cursor": cursor,
    }
    params = {key: value for key, value in params.items() if value is not None}
    encoded_params = urlencode(params)
    api_route = f"evaluation_test_cases/list?{encoded_params}"

    return get_request(
        api_route,
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.get("/api/evaluation_test_cases/read")
def get_evaluation_test_case(
    id: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    Get an evaluation test case by ID.
    """
    return get_request(
        f"evaluation_test_cases/read?id={id}",
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.post("/api/evaluation_test_cases/tags/add")
def add_evaluation_test_cases_tags(
    add_tags_data: AddOrRemoveTagsData,
    app_state: AppState = Depends(get_app_state),
):
    """
    Add tags to an evaluation test case.
    """
    return post_request(
        "evaluation_test_cases/tags/add",
        add_tags_data.model_dump(),
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.post("/api/evaluation_test_cases/tags/remove")
def remove_evaluation_test_cases_tags(
    remove_tags_data: AddOrRemoveTagsData,
    app_state: AppState = Depends(get_app_state),
):
    """
    Remove tags from an evaluation test case.
    """
    return post_request(
        "evaluation_test_cases/tags/remove",
        remove_tags_data.model_dump(),
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.get("/api/evaluation_test_sets/read")
def get_evaluation_test_set(
    id: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    Get an evaluation test set by ID.
    """
    return get_request(
        f"evaluation_test_sets/read?id={id}",
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


class CreateTestSetsData(core_utils.Record):
    """
    Data for creating evaluation test sets.
    """

    name: str
    testCases: list[EvaluationTestCaseData]
    description: str | None = None
    orgId: str | None = None
    projectId: str | None = None
    # metadata: core_utils.JSONObject | None = None, TODO: Why is this erroring?
    metadata: dict[str, Any] | None = None


@app.post("/api/evaluation_test_sets/create")
def create_evaluation_test_sets(
    create_test_sets_data: CreateTestSetsData,
    app_state: AppState = Depends(get_app_state),
):
    """
    Create an evaluation test set.
    """
    return post_request(
        "evaluation_test_sets/create",
        create_test_sets_data.model_dump(),
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.post("/api/evaluation_test_sets/tags/add")
def add_evaluation_test_set_tags(
    test_set_add_tags_data: AddOrRemoveTagsData,
    app_state: AppState = Depends(get_app_state),
):
    """
    Add tags to an evaluation test set.
    """
    return post_request(
        "evaluation_test_sets/tags/add",
        test_set_add_tags_data.model_dump(),
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.post("/api/evaluation_test_sets/tags/remove")
def remove_evaluation_test_set_tags(
    test_set_remove_tags_data: AddOrRemoveTagsData,
    app_state: AppState = Depends(get_app_state),
):
    """
    Remove tags from an evaluation test set.
    """
    return post_request(
        "evaluation_test_sets/tags/remove",
        test_set_remove_tags_data.model_dump(),
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.get("/api/evaluation_test_sets/list")
def list_evaluation_test_sets(
    search: str | None = None,
    sort: str | None = None,
    tag: str | None = None,
    pageSize: int | None = None,
    cursor: str | None = None,
    projectId: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    List evaluation sets.
    """
    params = {
        "search": search,
        "sort": sort,
        "tag": tag,
        "pageSize": pageSize,
        "cursor": cursor,
        "projectId": projectId,
    }
    params = {key: value for key, value in params.items() if value is not None}
    encoded_params = urlencode(params)
    api_route = f"evaluation_test_sets/list?{encoded_params}"

    return get_request(
        api_route,
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


class PromptModel(core_utils.Record):
    """
    Model for running prompts.
    """

    id: str
    name: str
    # Specifies whether the environment has the necessary API key to run
    # prompts with this model. None if no API key is required.
    hasApiKey: bool | None = None
    settingsSchema: PromptModelSettingsSchema


@app.get("/api/prompt_models/list")
def list_prompt_models():
    """
    List models available for running prompts.
    """
    load_dotenv_from_cwd()
    has_openai_key = os.getenv("OPENAI_API_KEY") is not None
    registered_models = ModelParserRegistry.display_parsers()
    return [
        PromptModel(
            id=key,
            name=value,
            hasApiKey=has_openai_key,
            settingsSchema=get_settings_schema_for_model(key),
        )
        for key, value in registered_models.items()
    ]


@app.get("/api/rag_events/list")
def list_rag_events(
    search: str | None = None,
    pageSize: int | None = None,
    cursor: str | None = None,
    eventName: str | None = None,
    traceId: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    List evaluation test cases.
    """
    params = {
        "search": search,
        "pageSize": pageSize,
        "cursor": cursor,
        "eventName": eventName,
        "traceId": traceId,
    }
    params = {key: value for key, value in params.items() if value is not None}
    encoded_params = urlencode(params)
    api_route = f"rag_events/list?{encoded_params}"

    return get_request(
        api_route,
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.get("/api/rag_ingestion_traces/list")
def list_rag_ingestion_traces(
    search: str | None = None,
    sort: str | None = None,
    tag: str | None = None,
    pageSize: int | None = None,
    cursor: str | None = None,
    startTime: int | None = None,
    endTime: int | None = None,
    projectId: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    List RAG ingestion traces.
    """
    params = {
        "search": search,
        "sort": sort,
        "tag": tag,
        "pageSize": pageSize,
        "cursor": cursor,
        "startTime": startTime,
        "endTime": endTime,
        "projectId": projectId,
    }
    params = {key: value for key, value in params.items() if value is not None}
    encoded_params = urlencode(params)
    api_route = f"rag_ingestion_traces/list?{encoded_params}"

    return get_request(
        api_route,
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.get("/api/rag_ingestion_traces/read")
def get_rag_ingestion_trace(
    id: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    Get a RAG ingestion trace by ID.
    """
    return get_request(
        f"rag_ingestion_traces/read?id={id}",
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.get("/api/rag_query_traces/list")
def list_rag_query_traces(
    search: str | None = None,
    sort: str | None = None,
    tag: str | None = None,
    feedback: str | None = None,
    pageSize: int | None = None,
    cursor: str | None = None,
    startTime: int | None = None,
    endTime: int | None = None,
    projectId: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    List RAG query traces.
    """
    params = {
        "search": search,
        "sort": sort,
        "tag": tag,
        "feedback": feedback,
        "pageSize": pageSize,
        "cursor": cursor,
        "startTime": startTime,
        "endTime": endTime,
        "projectId": projectId,
    }
    params = {key: value for key, value in params.items() if value is not None}
    encoded_params = urlencode(params)
    api_route = f"rag_query_traces/list?{encoded_params}"

    return get_request(
        api_route,
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.post("/api/rag_ingestion_traces/tags/add")
def add_rag_ingestion_trace_tags(
    add_tags_data: AddOrRemoveTagsData,
    app_state: AppState = Depends(get_app_state),
):
    """
    Add tags to a rag ingestion trace.
    """
    return post_request(
        "rag_ingestion_traces/tags/add",
        add_tags_data.model_dump(),
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.post("/api/rag_ingestion_traces/tags/remove")
def remove_rag_ingestion_trace_tags(
    remove_tags_data: AddOrRemoveTagsData,
    app_state: AppState = Depends(get_app_state),
):
    """
    Remove tags from a rag ingestion trace.
    """
    return post_request(
        "rag_ingestion_traces/tags/remove",
        remove_tags_data.model_dump(),
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.get("/api/rag_query_traces/read")
def get_rag_query_trace(
    id: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    Get a RAG query trace by ID.
    """
    return get_request(
        f"rag_query_traces/read?id={id}",
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.post("/api/rag_query_traces/tags/add")
def add_rag_query_trace_tags(
    add_tags_data: AddOrRemoveTagsData,
    app_state: AppState = Depends(get_app_state),
):
    """
    Add tags to a rag query trace.
    """
    return post_request(
        "rag_query_traces/tags/add",
        add_tags_data.model_dump(),
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.post("/api/rag_query_traces/tags/remove")
def remove_rag_query_trace_tags(
    remove_tags_data: AddOrRemoveTagsData,
    app_state: AppState = Depends(get_app_state),
):
    """
    Remove tags from a rag query trace.
    """
    return post_request(
        "rag_query_traces/tags/remove",
        remove_tags_data.model_dump(),
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


class CreateTagData(core_utils.Record):
    """
    Data for creating a tag.
    """

    name: str


@app.post("/api/tags/create")
def create_tag(
    create_tag_data: CreateTagData,
    app_state: AppState = Depends(get_app_state),
):
    """
    Create a tag.
    """
    return post_request(
        "tags/create",
        create_tag_data.model_dump(),
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.get("/api/tags/list")
def list_tags(
    search: str | None = None,
    pageSize: int | None = None,
    cursor: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    List RAG query traces.
    """
    params = {
        "search": search,
        "pageSize": pageSize,
        "cursor": cursor,
    }
    params = {key: value for key, value in params.items() if value is not None}
    encoded_params = urlencode(params)
    api_route = f"tags/list?{encoded_params}"

    return get_request(
        api_route,
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.get("/api/trace/read")
def get_trace(
    id: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    Get an OTEL trace by ID.
    """
    return get_request(
        f"trace/read?id={id}",
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


@app.post("/api/prompt/run_stream")
def run_prompt_stream(prompt_container: AIConfigPromptContainer):
    script = os.path.join(THIS_DIR, "scripts/run_aiconfig_prompt_container.py")
    cmd = f"{sys.executable} {script}"
    print(f"Running command: {cmd}")
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True,
        shell=True,
    )
    process.stdin.write(prompt_container.model_dump_json())
    process.stdin.flush()
    process.stdin.close()

    async def streamer():
        # Loop over the lines in the stdout
        for line in iter(process.stdout.readline, ""):
            yield line.strip()
            await asyncio.sleep(0)  # gives control back to the event loop

    return StreamingResponse(streamer())


@app.post("/api/prompt/run")
def run_prompt(prompt_container: AIConfigPromptContainer):
    """
    Run a prompt.
    """
    try:
        load_dotenv_from_cwd()
        aiconfig = AIConfigRuntime.create()
        system_prompt = None
        input = None
        # TODO: Handle dynamic number of messages
        for message in prompt_container.messages:
            if system_prompt is not None and input is not None:
                break
            if message.role == "system" and system_prompt is None:
                system_prompt = message.content
            elif message.role == "user" and input is None:
                input = message.content

        model_name = prompt_container.model_name
        inference_kwargs = prompt_container.inference_kwargs

        new_prompt = Prompt(
            name="prompt1",
            input=input or "",
            metadata={
                "model": {
                    "name": model_name,
                    "settings": {
                        "system_prompt": system_prompt or "",
                        **inference_kwargs,
                    },
                },
            },
        )

        aiconfig.add_prompt("prompt1", new_prompt)

        out = asyncio.run(aiconfig.run(new_prompt.name))
        return {"response": out}
    except Exception as e:
        return {
            "response": {
                "exception_type": str(type(e)),
                "exception_message": str(e),
            }
        }


class PromptContainer(BaseModel):
    prompt: str


@app.post("/api/run_user_llm_script")
def run_user_llm_script(
    prompt_container: PromptContainer,
    response: Response,
    app_state: AppState = Depends(get_app_state),
):
    """
    Run the user LLM script.
    """

    script_path = app_state.run_llm_script_path
    logger.debug(f"Script path: {script_path}")
    if script_path is None:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message": "No script path configured. Please rerun app with --help."
        }

    logger.info("Running user LLM script")
    config = lib_run_user_llm_script.RunUserLLMScriptconfig(
        executable=script_path,
        timeout_s=app_state.run_llm_script_timeout_s,
    )

    script_response = lib_run_user_llm_script.run_user_llm_script(
        config, prompt_container.prompt
    )

    match script_response:
        case Ok(response_):
            return {"response": response_}
        case Err(error):
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message": error}


@app.get("/api/evaluation_trace_log/list")
def get_trace_logs(
    traceId: str,
    projectId: str | None = None,
    orgId: str | None = None,
    app_state: AppState = Depends(get_app_state),
):
    """
    Get uploads for ids
    """
    params = {
        "traceId": traceId,
        "projectId": projectId,
        "orgId": orgId,
    }
    params = {key: value for key, value in params.items() if value is not None}
    encoded_params = urlencode(params)
    api_route = f"evaluation_trace_log/list?{encoded_params}"

    return get_request(
        api_route,
        app_state.server_mode,
        APIToken(load_api_token(app_state.server_mode)),
    )


# Defines a route handler for `/*` essentially.
# NOTE: this needs to be the last route defined b/c it's a catch all route
@app.get("/{rest_of_path:path}")
async def react_app(
    req: Request, app_state: AppState = Depends(get_app_state)
):
    """
    Serve the frontend react app (DEBUG ONLY).
    """
    if app_state.server_mode == ServerMode.DEBUG:  # type: ignore
        return {
            "message": "Not serving bundle in DEBUG mode, use yarn start in client/"
        }
    return templates.TemplateResponse("index.html", {"request": req})
