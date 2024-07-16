"""General utils file for the tracing SDK"""

import json
from typing import Optional, Union

from opentelemetry import trace as trace_api
from opentelemetry.context import Context
from opentelemetry.trace import SpanContext
from opentelemetry.trace.span import Span, TraceFlags, TraceState
from requests import Response

from ..common.types import RagFlowType
from ..common.utils import SHOW_DEBUG
from .trace_data_singleton import TraceDataSingleton

# TODO: Remove all the "utils" methods that rely on TraceDataSingleton, since
# that means they're technically not utils


def set_trace_data(
    project_id: Optional[str],
    rag_flow_type: Optional[RagFlowType] = None,
    span: Optional[Span] = None,
):
    """
    Helper function to initialize trace data for a new trace (creating a new
    span without a parent span attached to it).

    Args:
        project_id (Optional[str]): The project ID associated with the trace.
            The project_id is used to log the trace data to the correct
            project in the RAG traces table.
        rag_flow_type (Optional[RagFlowType]): The type of RAG flow (ingestion
            or query). This only gets set here if set inside of the
            `get_lastmile_tracer()` method.
        span (Optional[Span]): The current span. If provided, the trace_id will
            be retrieved from the span's context.

    Returns:
        None
    """
    trace_data_singleton = TraceDataSingleton()
    if SHOW_DEBUG:
        trace_id_before = trace_data_singleton.trace_id
        print(f"{trace_id_before=}")

    if trace_data_singleton.trace_id is None:
        # We need to pass in a span object directly sometimes because if
        # tracer.start_span() is run as the root span without context manager
        # (with statement or annotation), it will create a new span
        # and get_current_span is not linked to the get_current_span().
        # current_span WON'T have the id of the span created by start_span
        current_span: Span = span or trace_api.get_current_span()
        trace_data_singleton.trace_id = convert_int_id_to_hex_str(
            current_span.get_span_context().trace_id
        )
        if trace_data_singleton.project_id is None:
            trace_data_singleton.project_id = project_id
        if trace_data_singleton.rag_flow_type is None:
            trace_data_singleton.rag_flow_type = rag_flow_type

    if SHOW_DEBUG:
        trace_id_after = trace_data_singleton.trace_id
        print(f"{trace_id_after=}")


def convert_int_id_to_hex_str(int_id: int) -> str:
    """
    Helper function to convert an integer id to a hex string. This is
    needed because Jaeger does trace and span queries using hex strings
    instead of integer values.

    Ex: int_id = 123456789 -> hex value = 0x75BCD15 --> str = "75BCD15"

    @param int_id (int): The integer id to convert to a hex string

    @return str: The hex string representation of the integer id
    """
    hex_str = str(hex(int_id)).split("x")[1]
    # TraceId is 16-byte (32 characters), so if it's smaller
    # pad with leading 0s that got cut when extracting int
    # Source: https://opentelemetry.io/docs/specs/otel/trace/api/#spancontext
    while len(hex_str) < 32:
        hex_str = "0" + hex_str
    return hex_str


def _log_trace_rag_events(
    lastmile_api_token: str,
    # TODO: Allow user to specify the type of rag trace (Ingestion vs. Query)
) -> Optional[Response]:
    """
    Log the trace-level data to the relevant rag traces table (ingestion or
    query). This is for both structured and unstructured RAG events
    """
    # TODO: Add error handling for response
    trace_data_singleton = TraceDataSingleton()
    response = trace_data_singleton.log_to_rag_traces_table(lastmile_api_token)
    if response is None:
        return
    if SHOW_DEBUG:
        print("Results from rag traces create endpoint:")
        print(response.json())
    return response


def _log_span_rag_events(
    lastmile_api_token: str,
) -> None:
    """
    Log the span-level unstructured rag events
    """
    # TODO: Add error handling for response
    trace_data_singleton = TraceDataSingleton()
    trace_data_singleton.log_span_rag_events(lastmile_api_token)
    # TODO: move within internal function
    # if SHOW_DEBUG:
    #     print("Results from rag events create endpoint:")
    #     print(response.json())
    return None


def _export_log_data(lastmile_api_token: str) -> None:
    """
    Export the log data from .log() API calls to S3 and LastMile DB
    """
    trace_data_singleton = TraceDataSingleton()
    trace_data_singleton.upload_log_data(lastmile_api_token)
    return None
    # for path in self.logger_filepaths:
    #     print(path)


def log_all_trace_events_and_reset_trace_state(
    lastmile_api_token: str,
    # TODO: Allow user to specify the type of rag trace (Ingestion vs. Query)
) -> None:
    """
    Log all the event data for both the trace and span levels, as well as
    logged data that isn't specifically tied to traces.

    The trace data gets logged to the relevent trace table and can include both
    unstructured (RagEvent) and structured (RagIngestionTrace or RagQueryTrace)
    data formats, as well as non-trace specific data (EvaluationTraceLog).

    After this is finished, we reset the trace state
    """
    _log_trace_rag_events(lastmile_api_token)
    _log_span_rag_events(lastmile_api_token)
    _export_log_data(lastmile_api_token)

    # Reset current trace data so we can start a
    # new trace in a fresh state
    reset_trace_state()


def reset_trace_state() -> None:
    """
    Reset the trace state. Used to clear trace data and start new state
    """
    trace_data_singleton = TraceDataSingleton()
    trace_data_singleton.reset()


def convert_to_context(
    context: Union[SpanContext, Context, str, None]
) -> Union[Context, None]:
    """
    Converts a SpanContext or Context object into a Context object.

    @param context (Union[SpanContext, Context, str]): The context to normalize
    """
    if isinstance(context, str):
        try:
            span_context_dict = json.loads(context)
            span_context_dict["trace_state"] = TraceState.from_header(
                span_context_dict["trace_state"]
            )
            span_context_dict["trace_flags"] = TraceFlags(
                span_context_dict["trace_flags"]
            )
            span_context = SpanContext(**span_context_dict)
            context = span_context  # handle Span Context below
        except Exception as exc:
            raise ValueError(
                f"Malformed context string {context}. Please pass in a valid deserialized SpanContext object by calling `export_span()`"
            ) from exc

    if context is None:
        return None
    if isinstance(context, SpanContext):
        non_recording_span = trace_api.NonRecordingSpan(context)
        return trace_api.set_span_in_context(non_recording_span)
    return context
