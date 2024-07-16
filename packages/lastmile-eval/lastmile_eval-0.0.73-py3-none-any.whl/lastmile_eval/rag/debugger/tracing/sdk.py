"""
File to define the SDKs implementations that users can use in code, see example
folder for example on how it can be implemented
"""

import json
import logging
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.trace.span import Span
from result import Err, Ok

from lastmile_eval.rag.debugger.common.utils import (
    get_auth_header,
    get_lastmile_api_token,
    http_get,
    WEBSITE_BASE_URL,
)

from ..api import LastMileTracer
from ..common import core
from ..common.types import ProjectName, RagFlowType
from ..common.utils import (
    get_project_id,
    raise_for_status,
)
from .exporters import LastMileConsoleSpanExporter, LastMileOTLPSpanExporter
from .lastmile_tracer import LastMileTracer as LastMileTracerImpl
from .utils import (
    log_all_trace_events_and_reset_trace_state,
    reset_trace_state,
)


class _LastMileTracerProvider(TracerProvider):
    """
    Subclass of TracerProvider that defines the connection between LastMile
    Jaeger collector endpoint to the LastMileTracer
    """

    def __init__(
        self,
        lastmile_api_token: str,
        output_filepath: Optional[str] = None,
    ):
        super().__init__()

        self._already_defined_tracer_provider = False
        self._tracers: Dict[str, LastMileTracer] = {}

        # If output_filepath is defined, then save trace data to that file
        # instead of forwarding to an OpenTelemetry collector. This is useful
        # for debugging and demo purposes but not recommended for production.
        if output_filepath is not None:
            output_destination = open(output_filepath, "w", encoding="utf-8")
            exporter = LastMileConsoleSpanExporter(
                out=output_destination, reset_trace_data_func=reset_trace_state
            )
            exporter = ConsoleSpanExporter(out=output_destination)
        else:
            exporter = LastMileOTLPSpanExporter(
                log_rag_query_func=lambda: log_all_trace_events_and_reset_trace_state(
                    lastmile_api_token
                ),
                endpoint=f"{WEBSITE_BASE_URL}/api/trace/create",
                headers={
                    "authorization": f"Bearer {lastmile_api_token}",
                    "Content-Type": "application/json",
                },
                # TODO: Add timeout argument and have default here
            )

        # We need to use SimpleSpanProcessor instead of BatchSpanProcessor
        # because BatchSpanProcessor does not call the exporter.export()
        # method until it is finished batching, but we need to call it at the
        # end of each span to reset the trace-level data otherwise we can
        # error.

        # The future workaround is to make all the trace-level data checks and
        # trace-data resetting occur OUTSIDE of the exporter.export() method,
        # and simply do those. Then we can have a state-level manager dict
        # where we keep track of traceId, and the state corresponding to that
        # so that when we call the callback log_rag_query_func(), it will take
        # in a trace_id arg to know which trace data to log
        span_processor = SimpleSpanProcessor(exporter)
        self.add_span_processor(span_processor)

    def get_tracer_from_name(
        self,
        token: str,
        tracer_name: str,
        project_name: Optional[str],
        rag_flow_type: Optional[RagFlowType] = None,
    ) -> LastMileTracer:
        """
        Get the tracer object from the tracer_name. If the tracer object is
        already defined, then return that. Otherwise, create a new tracer
        """
        if tracer_name in self._tracers:
            return self._tracers[tracer_name]

        if not self._already_defined_tracer_provider:
            trace_api.set_tracer_provider(self)
            self._already_defined_tracer_provider = True

        tracer_implementor: trace_api.Tracer = trace_api.get_tracer(
            tracer_name
        )
        tracer = LastMileTracerImpl(
            token,
            tracer_implementor,
            tracer_name,
            project_name,
            rag_flow_type,
        )
        self._tracers[tracer_name] = tracer
        return tracer


def get_lastmile_tracer(
    tracer_name: str,
    pipeline_type: Optional[RagFlowType] = None,
    output_filepath: Optional[str] = None,
    project_name: Optional[str] = None,
    lastmile_api_token: Optional[str] = None,
) -> LastMileTracer:
    """
    Return a tracer object to instrument your code, log RAG-specific events
    (e.g. document embedding), and record application configuration
    parameters (e.g. chunk size, LLM temperature).

    See `lastmile_eval.rag.debugger.api.tracing.LastMileTracer for available
    APIs and more details

    @param tracer_name str: The name of the tracer to be used.
    @param lastmile_api_token (str): Used for authentication.
        Create one from the "API Tokens" section from this website:
        https://lastmileai.dev/settings?page=tokens
    @param project_name Optional(str): The project name that will be
        associated with the trace data. This can help group traces in the UI
    @param output_filepath Optional(str): By default, trace data is exported to
        an OpenTelemetry collector and saved into a hosted backend storage such
        as ElasticSearch. However if an output_filepath is defined,
        then the trace data is saved to that file instead. This is useful for
        debugging and demo purposes, but not recommened for production use.
    @param rag_flow_type Optional[RagFlowType]: The type of RAG flow that the
        tracer is being used in. If it is none, then the returned tracer can
        be used for both ingestion and query tracing.

    @return LastMileTracer: The tracer interface object to log OpenTelemetry data.
    """
    token = get_lastmile_api_token(lastmile_api_token)
    provider = _LastMileTracerProvider(token, output_filepath)
    return provider.get_tracer_from_name(
        token=token,
        tracer_name=tracer_name,
        project_name=project_name,
        rag_flow_type=pipeline_type,
    )


def get_trace(
    trace_id: str,
    lastmile_api_token: Optional[str] = None,
) -> core.JSONObject:
    """
    Download an individual trace.

    @param trace_id (str): The trace_id to get the trace data from. This is
        often the hexadecmial string representation of the trace_id int from
        the OpenTelemetry SDK.
        Ex: int_id = 123456789 -> hex value = 0x75BCD15 --> str = "75BCD15"
    @param lastmile_api_token (str): Used for authentication.
        Create one from the "API Tokens" section from this website:
        https://lastmileai.dev/settings?page=tokens

    @return core.JSONObject: The trace data from the trace_id
    """
    token = get_lastmile_api_token(lastmile_api_token)
    # TODO: Allow trace_id to also represent a rag_query_trace or rag_ingestion_trace entity ID too
    endpoint = f"trace/read?id={trace_id}"
    headers = get_auth_header(token)
    response = http_get(WEBSITE_BASE_URL, endpoint, headers)

    match response:
        case Ok(res):
            raise_for_status(
                res, f"Error fetching trace data for trace_id {trace_id}"
            )
            return res.json()
        case Err(err):
            raise err


def list_ingestion_trace_events(
    take: int = 10,
    project_name: Optional[str] = None,
    lastmile_api_token: Optional[str] = None,
    # TODO: Create macro for default timeout value
    timeout: int = 60,
    # TODO: Allow a verbose option so I don't have to keep setting SHOW_DEBUG
    # to true. If we do this, we'll also have to move print statement to logger
    # ones. This is P3 imo
) -> dict[str, Any]:  # TODO: Define eplicit typing for JSON response return
    """
    Get the list of ingestion trace events. TODO: Add more filtering options

    @param take (int): The number of trace events to take. Defaults to 10
    @param project_name (str): The project name associated with the trace events.
        If not provided, the trace events for the default project will be listed.
    @param lastmile_api_token (str): Used for authentication. If not
        defined, will try to get the token from the LASTMILE_API_TOKEN
        environment variable.
        You can create a token from the "API Tokens" section from this website:
        https://lastmileai.dev/settings?page=tokens

    @return dict[str, Any]: The JSON response of the ingestion trace events
    """
    token = get_lastmile_api_token(lastmile_api_token)

    if project_name is not None:
        project_id_res = get_project_id(
            ProjectName(project_name), token, create_if_not_exists=False
        )
        match project_id_res:
            case Ok(res_project_id):
                project_id = res_project_id
            case Err(err):
                raise err
    else:
        project_id = "default"

    encoded_params = urlencode(
        {
            "projectId": project_id,
            "pageSize": take,
        }
    )

    list_traces_endpoint = f"rag_ingestion_traces/list?{encoded_params}"
    headers = get_auth_header(token)
    response = http_get(
        WEBSITE_BASE_URL, list_traces_endpoint, headers, timeout
    )

    # TODO: Use @result_return_or_raise_for_apis_only from lastmile_utils once it's > 0.0.24
    match response:
        case Ok(res):
            raise_for_status(
                res,
                f"Error fetching ingestion trace events for {'default project' if project_name is None else project_name},"
                " pageSize={take}",
            )
            return res.json()
        case Err(err):
            raise err


def get_latest_ingestion_trace_id(
    project_name: Optional[str] = None,
    lastmile_api_token: Optional[str] = None,
) -> Optional[str]:
    """
    Convenience function to get the latest ingestion trace id.
    You can pass in this ID into the tracer to link a query trace with an
    ingestion trace.

    @param lastmile_api_token Optional(str): Used for authentication. If not
        defined, will try to get the token from the LASTMILE_API_TOKEN
        environment variable.
        You can create a token from the "API Tokens" section from this website:
        https://lastmileai.dev/settings?page=tokens

    @return Optional[str]: The ingestion trace ID if found, otherwise None
    """
    ingestion_traces: dict[str, Any] = list_ingestion_trace_events(
        take=1,
        project_name=project_name,
        lastmile_api_token=lastmile_api_token,
    )

    if (
        "ingestionTraces" not in ingestion_traces
        or len(ingestion_traces["ingestionTraces"]) == 0
    ):
        logging.error(
            "Could not find ingestion trace. Please check that the project name is correct.",
            stack_info=True,
        )
        return None
    ingestion_trace_id: str = ingestion_traces["ingestionTraces"][0]["traceId"]
    return ingestion_trace_id


def get_query_trace_event(
    query_trace_event_id: str,
    lastmile_api_token: Optional[str] = None,
    # TODO: Create macro for default timeout value
    timeout: int = 60,
    # TODO: Allow a verbose option so I don't have to keep setting SHOW_DEBUG
    # to true. If we do this, we'll also have to move print statement to logger
    # ones. This is P3 imo
) -> dict[str, Any]:  # TODO: Define eplicit typing for JSON response return
    """
    Get the query trace event from the query_trace_event_id

    @param query_trace_event_id (str): The ID for the table row under which
        this RAG query trace event is stored
    @param lastmile_api_token (str): Used for authentication. If not
        defined, will try to get the token from the LASTMILE_API_TOKEN
        environment variable.
        You can create a token from the "API Tokens" section from this website:
        https://lastmileai.dev/settings?page=tokens

    @return dict[str, Any]: The JSON response of the query trace events
    """
    token = get_lastmile_api_token(lastmile_api_token)
    endpoint = f"rag_query_traces/read?id={query_trace_event_id}"
    headers = get_auth_header(token)
    response = http_get(WEBSITE_BASE_URL, endpoint, headers, timeout)

    match response:
        case Ok(res):
            raise_for_status(
                res,
                f"Error fetching query trace event for id {query_trace_event_id}",
            )
            return res.json()
        case Err(err):
            raise err


## Helper functions
def export_span(span: Span) -> str:
    """
    Return a serialized representation of the span that can be used to start subspans in other places. See `Span.start_span` for more details.
    """
    span_context = span.get_span_context()
    span_context_dict = {
        "trace_id": span_context.trace_id,
        "span_id": span_context.span_id,
        "trace_flags": span_context.trace_flags,
        "trace_state": span_context.trace_state.to_header(),
        "is_remote": span_context.is_remote,
    }

    return json.dumps(span_context_dict)


def get_span_id(span: Optional[Span] = None) -> int:
    """
    Get the span ID from the provided span object.

    If no span object is provided, the span ID is retrieved from the current span.

    Args:
        span: The span object to retrieve the span ID from. Defaults to None.

    Returns:
        The span ID as an integer.
    """
    if span:
        return span.get_span_context().span_id

    current_span: Span = trace_api.get_current_span()
    return current_span.get_span_context().span_id


def get_trace_id(span: Optional[Span] = None) -> int:
    """
    Get the trace ID from the provided span object.

    If no span object is provided, the trace ID is retrieved from the current span.

    Args:
        span: The span object to retrieve the trace ID from. Defaults to None.

    Returns:
        The trace ID as an integer.
    """
    if span:
        return span.get_span_context().trace_id

    current_span: Span = trace_api.get_current_span()
    return current_span.get_span_context().trace_id
