"""
File to define the LastMileTracer class that implements the LastMileTracerAPI.
This class should not be instantiated directly. Instead, use the the method
`get_lastmile_tracer()` from the `lastmile_eval.rag.debugger.tracing` module
"""

import inspect
import json
import logging
import os
from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from functools import wraps

from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterator,
    Optional,
    ParamSpecArgs,
    ParamSpecKwargs,
    Sequence,
    Union,
)

from urllib.parse import urlencode

import requests
from opentelemetry import context as context_api
from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.trace import SpanContext
from opentelemetry.trace.span import INVALID_SPAN, Span
from opentelemetry.util import types
from requests import Response
from requests.adapters import HTTPAdapter, Retry
from result import Err, Ok

# TODO: Don't use absolute imports when relative ones
# are available
import lastmile_eval.rag.debugger.common.core as core
from lastmile_eval.rag.debugger.api.tracing import (
    LastMileTracer as LastMileTracerAPI,
)
from lastmile_eval.rag.debugger.common.utils import get_website_base_url
from lastmile_eval.rag.debugger.tracing.decorators import (
    _try_log_input,
)  # type: ignore
from lastmile_eval.rag.debugger.tracing.decorators import (
    _try_log_output,
)  # type: ignore
from lastmile_eval.rag.debugger.tracing.manage_params_impl import (
    ManageParamsImpl,
)
from lastmile_eval.rag.debugger.api import ParamKey
from lastmile_eval.rag.debugger.api.add_rag_event_interface import RAGEventType

from ..common.types import RagFlowType, T_cov
from ..common.utils import (
    LASTMILE_SPAN_KIND_KEY_NAME,
    log_for_status,
    raise_for_status,
)
from .sdk_utils.endpoints import read_key_value_pair, store_key_value_pair
from .trace_data_singleton import TraceDataSingleton
from .utils import (
    convert_int_id_to_hex_str,
    convert_to_context,
    set_trace_data,
)

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

# default timeout for requests
TIMEOUT = 60


class LastMileTracer(ManageParamsImpl, LastMileTracerAPI):
    """See `lastmile_eval.rag.debugger.api.tracing.LastMileTracer`"""

    def __init__(
        self,
        lastmile_api_token: str,
        tracer_implementor: trace_api.Tracer,
        tracer_name: str,
        # TODO: Propagate DEFAULT_PROJECT_NAME usage throughout
        project_name: Optional[str],
        rag_flow_type: Optional[RagFlowType] = None,
    ):
        self.lastmile_api_token = lastmile_api_token
        TraceDataSingleton()
        self.tracer_implementor: trace_api.Tracer = tracer_implementor

        self.project_name = project_name
        self.project_id: Optional[str] = None
        self.set_project()
        self.rag_flow_type = rag_flow_type
        self.ingestion_trace_id = None

        # TODO: Add ability to suppress printing to stdout in default logger
        # TODO: Put this logic in helper method
        logger_name = self.project_name or tracer_name
        self.logger: logging.Logger = logging.getLogger(logger_name)

        log_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)-5.5s]  %(message)s"
        )
        logger_filepath = os.path.join(
            os.getcwd(), "logs", f"{logger_name}.log"
        )
        if not os.path.exists(os.path.dirname(logger_filepath)):
            os.mkdir(os.path.dirname(logger_filepath))
        open(logger_filepath, "w", encoding="utf-8").close()
        file_handler = logging.FileHandler(logger_filepath)
        file_handler.setFormatter(log_formatter)
        self.logger.addHandler(file_handler)

    def get_last_rag_query_trace_id_written(
        self,
    ) -> Optional[str]:
        """This is used to connect run_and_evaluate() to the trace IDs
        written by the user.

        INVARIANT: return Ok(trace_id) if and only if it was successfully written to Postgres.
            This must be the Postgres ID, not the Jaeger one.
            Return Err(message) in all other cases.

        Usage intention:

        Assume the user has defined run_query_flow() which has access to this tracer
        and exports a trace.

        After running run_query_flow(), we want to download the associated trace.
        This method is intented to allow us to query for the trace the user has written.

        More specifically, run_query_flow returns a record containing
        (output, the_written_trace_id). The user will call this method to get the ID.

        When we call run_query_flow(), we can then download the associated trace data.

        At that point, run_and_evaluate can simply create an ExampleSet as usual,
        connected to the Trace IDs, and then run evaluations on it as usual.

        """
        try:
            trace_id = core.RAGQueryTraceID(
                "TODO get the last written trace id"
            )
            return trace_id
        except Exception as e:
            exn_info = core.exception_info(e)
            # TODO definitely need to log this here
            # stderr and/or elsewhere.
            return None

    def trace_function(
        self,
        name: Optional[str] = None,
        context: Optional[Union[context_api.Context, SpanContext, str]] = None,
        kind: trace_api.SpanKind = trace_api.SpanKind.INTERNAL,
        attributes: types.Attributes = None,
        links: Optional[Sequence[trace_api.Link]] = None,
        start_time: Optional[int] = None,
        record_exception: bool = True,
        set_status_on_exception: bool = True,
        end_on_exit: bool = True,
    ) -> Callable[[Callable[..., T_cov]], Callable[..., T_cov]]:
        """
        Function decorator that logs the wrapped function's input and output as attributes on a span.

        To specify custom metadata, use the `attributes` property. The function complies with
        the OpenTelemetry specification.
        """

        def decorator(func: Callable[..., T_cov]) -> Callable[..., T_cov]:
            f_sig = inspect.signature(func)

            @wraps(func)
            def _wrap(*f_args: ParamSpecArgs, **f_kwargs: ParamSpecKwargs):
                with self.start_as_current_span(
                    name if name is not None else func.__name__,
                    context,
                    kind,
                    attributes,
                    links,
                    start_time,
                    record_exception,
                    set_status_on_exception,
                    end_on_exit,
                ) as span:
                    _try_log_input(span, f_sig, f_args, f_kwargs)
                    return_value = func(*f_args, **f_kwargs)
                    _try_log_output(span, return_value)
                    return return_value

            return _wrap

        return decorator

    async def atrace_function(
        self,
        name: Optional[str] = None,
        context: Optional[Union[context_api.Context, SpanContext, str]] = None,
        kind: trace_api.SpanKind = trace_api.SpanKind.INTERNAL,
        attributes: types.Attributes = None,
        links: Optional[Sequence[trace_api.Link]] = None,
        start_time: Optional[int] = None,
        record_exception: bool = True,
        set_status_on_exception: bool = True,
        end_on_exit: bool = True,
    ) -> Callable[
        [Callable[..., Awaitable[T_cov]]], Callable[..., Awaitable[T_cov]]
    ]:
        """
        Async version of `trace_function`
        """

        def decorator(
            func: Callable[..., Awaitable[T_cov]]
        ) -> Callable[..., Awaitable[T_cov]]:
            f_sig = inspect.signature(func)

            @wraps(func)
            async def _wrap(
                *f_args: ParamSpecArgs, **f_kwargs: ParamSpecKwargs
            ):
                with self.start_as_current_span(
                    name if name is not None else func.__name__,
                    context,
                    kind,
                    attributes,
                    links,
                    start_time,
                    record_exception,
                    set_status_on_exception,
                    end_on_exit,
                ) as span:
                    _try_log_input(span, f_sig, f_args, f_kwargs)
                    return_value = await func(*f_args, **f_kwargs)
                    _try_log_output(span, return_value)
                    return return_value

            return _wrap

        return decorator

    @contextmanager
    # pylint: disable=too-many-arguments
    def start_as_current_span(
        self,
        name: str,
        context: Optional[Union[context_api.Context, SpanContext, str]] = None,
        kind: trace_api.SpanKind = trace_api.SpanKind.INTERNAL,
        attributes: types.Attributes = None,
        links: Optional[Sequence[trace_api.Link]] = None,
        start_time: Optional[int] = None,
        record_exception: bool = True,
        set_status_on_exception: bool = True,
        end_on_exit: bool = True,
    ) -> Iterator[Span]:
        """See `lastmile_eval.rag.debugger.api.tracing.LastMileTracer.start_as_current_span()`"""
        context = convert_to_context(context)
        with self.tracer_implementor.start_as_current_span(
            _get_name_with_span_count(name),
            context,
            kind,
            attributes,
            links,
            start_time,
            record_exception,
            set_status_on_exception,
            end_on_exit,
        ) as span:
            set_trace_data(
                project_id=self.project_id,
                rag_flow_type=self.rag_flow_type,
                span=span,
            )
            yield span

    # pylint: disable=too-many-arguments
    def start_span(
        self,
        name: str,
        context: Optional[Union[context_api.Context, SpanContext, str]] = None,
        kind: trace_api.SpanKind = trace_api.SpanKind.INTERNAL,
        attributes: types.Attributes = None,
        links: Sequence[trace_api.Link] = (),
        start_time: Optional[int] = None,
        record_exception: bool = True,
        set_status_on_exception: bool = True,
    ) -> Span:
        """See `lastmile_eval.rag.debugger.api.tracing.LastMileTracer.start_span()`"""
        context = convert_to_context(context)
        span = self.tracer_implementor.start_span(
            _get_name_with_span_count(name),
            context,
            kind,
            attributes,
            links,
            start_time,
            record_exception,
            set_status_on_exception,
        )
        set_trace_data(
            project_id=self.project_id,
            rag_flow_type=self.rag_flow_type,
            span=span,
        )
        return span

    def log_span_event(
        self,
        # TODO: Have better typing for JSON for input, output, event_data
        input: core.JSON = None,
        output: core.JSON = None,
        span: Optional[Span] = None,
        event_data: Optional[Union[core.JSON, "DataclassInstance"]] = None,
        event_kind: RAGEventType = RAGEventType.CUSTOM,
        name: Optional[str] = None,
    ) -> None:
        """See `lastmile_eval.rag.debugger.api.tracing.LastMileTracer.add_rag_event_for_span()`"""
        if input is not None and output is None:
            logging.error(
                "Unable to add rag event for span: "
                "If you pass in input, you must also define an output value for this event",
                stack_info=True,
            )
            return
        if input is None and output is not None:
            logging.error(
                "Unable to add rag event for span: "
                "If you pass in output, you must also define an input value for this event",
                stack_info=True,
            )
            return

        if input is None and output is None:
            if event_data is None:
                logging.error(
                    "Unable to add rag event for span: "
                    "If input and output are not set, you must pass in event_data",
                    stack_info=True,
                )
                return

        current_span: Span = span or trace_api.get_current_span()
        if current_span == INVALID_SPAN:
            logging.error(
                "Unable to add rag event for span: "
                "Could not find a valid span to connect a RAG event to. Either pass in a span argument directly or use the `LastMileTracer.start_as_current_span` method to ensure that `trace_api.get_current_span()` returns a valid span",
                stack_info=True,
            )
            return

        if is_dataclass(input) and not isinstance(input, type):
            input = asdict(input)
        if is_dataclass(output) and not isinstance(output, type):
            output = asdict(output)
        if is_dataclass(event_data) and not isinstance(event_data, type):
            event_data = asdict(event_data)

        # Use a default Name
        if name is None:
            name = event_kind.value

        current_span.set_attribute(LASTMILE_SPAN_KIND_KEY_NAME, event_kind)

        span_id = convert_int_id_to_hex_str(
            current_span.get_span_context().span_id
        )
        readable_span = ReadableSpan(current_span)
        parent_span = readable_span.parent
        parent_span_id = None
        if parent_span:
            parent_span_id = convert_int_id_to_hex_str(parent_span.span_id)

        trace_data_singleton = TraceDataSingleton()
        try:
            # Check if args are JSON serializable, otherwise won't be able to
            # export trace data in the collector
            json.dumps(input)
            json.dumps(output)
            json.dumps(event_data)
        except TypeError as e:
            raise TypeError(
                f"Error JSON serializing input, output and event_data arguments for (trace_id, span_id): ({trace_data_singleton.trace_id}, {span_id})"
            ) from e

        try:
            event_payload = {
                "event_name": name,
                "span_id": span_id,
                "input": input or "",
                "output": output or "",
                "event_data": event_data or {},
                "ingestion_trace_id": self.ingestion_trace_id,
                "rag_flow_type": self.rag_flow_type,
                "parent_span_id": parent_span_id,
            }
            trace_data_singleton.add_rag_event_for_span(event_payload)

            # Save in Span:
            if not isinstance(input, str):
                input = json.dumps(input)
            if not isinstance(output, str):
                output = json.dumps(output)
            event_payload_with_no_dict_values: types.Attributes = {
                # TODO: Check typings for input and output to make sure
                # they conform to types.Attributes (yikes!)
                "input": input or "",
                "output": output or "",
                # Dict type not supported for event values
                # See types.AttributeValue from OpenTelemetry SDK
                "event_data": json.dumps(event_data or {}),
                "ingestion_trace_id": self.ingestion_trace_id or "",
            }
            current_span.add_event(name, event_payload_with_no_dict_values)
        except Exception as e:
            raise RuntimeError(
                f"Error adding rag event for (trace_id, span_id): ({trace_data_singleton.trace_id}, {span_id})"
            ) from e

    def log_trace_event(
        self,
        input: core.JSON = None,
        output: core.JSON = None,
        event_data: Optional[
            Union[core.JSONObject, "DataclassInstance"]
        ] = None,
    ) -> None:
        """See `lastmile_eval.rag.debugger.api.tracing.LastMileTracer.log_trace_event()`"""
        if input is not None and output is None:
            logging.error(
                "Unable to add rag event for trace: "
                "If you pass in input, you must also define an output value for this event",
                stack_info=True,
            )
            return
        if input is None and output is not None:
            logging.error(
                "Unable to add rag event for trace: "
                "If you pass in output, you must also define an input value for this event",
                stack_info=True,
            )
            return

        if input is None and output is None:
            if event_data is None:
                logging.error(
                    "Unable to add rag event for trace: "
                    "If input and output are not set, you must pass in event_data",
                    stack_info=True,
                )
                return

        if is_dataclass(input) and not isinstance(input, type):
            input = asdict(input)
        if is_dataclass(output) and not isinstance(output, type):
            output = asdict(output)
        if is_dataclass(event_data) and not isinstance(event_data, type):
            event_data = asdict(event_data)

        trace_data_singleton = TraceDataSingleton()
        try:
            # Check if args are JSON serializable, otherwise won't be able to
            # export trace data in the collector
            json.dumps(event_data)
            json.dumps(input)
            json.dumps(output)
        except TypeError:
            logging.error(  # pylint: disable=logging-fstring-interpolation
                "Unable to add rag event for trace: "
                f"Error JSON serializing input, output and event_data arguments for trace_id: {trace_data_singleton.trace_id}",
                stack_info=True,
            )
            return

        try:
            event_payload = {
                # TODO (rossdan): Event_name isn't processed at trace-level
                # for RagQueryTrace or RagIngestionTrace
                "event_name": "",
                "input": input or "",
                "output": output or "",
                "event_data": event_data or {},
                "ingestion_trace_id": self.ingestion_trace_id,
                "rag_flow_type": self.rag_flow_type,
            }
            trace_data_singleton.add_rag_event_for_trace(event_payload)
        except Exception:
            logging.error(  # pylint: disable=logging-fstring-interpolation
                "Unable to add rag event for trace: "
                f"Error adding rag event for trace id: {trace_data_singleton.trace_id}",
                exc_info=True,
            )

    # TODO: Don't make params Any type
    def get_params(self) -> dict[str, Any]:
        """See `lastmile_eval.rag.debugger.api.tracing.LastMileTracer.get_params()`"""
        trace_data_singleton = TraceDataSingleton()
        return trace_data_singleton.get_params()

    def register_param(
        self,
        key: str | ParamKey,
        value: Any,
        span: Optional[Span] = None,
    ) -> None:
        """See `lastmile_eval.rag.debugger.api.tracing.LastMileTracer.register_param()`"""

        trace_data_singleton = TraceDataSingleton()
        try:
            # Check if value is JSON serializable, otherwise won't be able to
            # export trace data in the collector
            json.dumps(value)
        except TypeError:
            logging.error(  # pylint: disable=logging-fstring-interpolation
                "Unable to register param: "
                f"Error registering parameter to trace {trace_data_singleton.trace_id}",
                stack_info=True,
            )

        current_span: Span = span or trace_api.get_current_span()
        span_count: Optional[int] = None
        if current_span == INVALID_SPAN:
            span_count = trace_data_singleton.span_count
        elif isinstance(current_span, ReadableSpan):
            try:
                span_count = int(current_span.name.split(" - ")[0])
            except ValueError:
                # TODO: Handle error handling to stdout logger
                pass

        # Append the span's number to the param set key to make it easier to
        # tell which param key is associated with which span if there
        # already exists a param set key with the same name. This is common for
        # auto-instrumentation
        sanitized_key = key.value if isinstance(key, ParamKey) else key
        param_set_key = sanitized_key
        if span_count is not None:
            param_set_key = _update_param_key_if_needed(
                sanitized_key, span_count
            )
        trace_data_singleton.register_param(param_set_key, value)

        # Log this also in the current span to help with debugging if needed
        if current_span != INVALID_SPAN:
            if isinstance(value, (dict, Dict)):
                # Dict type not supported for span attribute value
                value = json.dumps(value)
            current_span.set_attribute(
                sanitized_key,
                value,
            )

    def register_params(
        self,
        params: dict[str | ParamKey, Any],
        should_overwrite: bool = False,
        span: Optional[Span] = None,
    ) -> None:
        """See `lastmile_eval.rag.debugger.api.tracing.LastMileTracer.register_params()`"""
        if should_overwrite:
            self.clear_params(should_clear_global_params=False)

        for k, v in params.items():
            self.register_param(
                k,
                v,
                span=span,
            )

    def clear_params(self, should_clear_global_params: bool = False) -> None:
        """See `lastmile_eval.rag.debugger.api.tracing.LastMileTracer.clear_params()`"""
        trace_data_singleton = TraceDataSingleton()
        trace_data_singleton.clear_params(should_clear_global_params)

    def log(self, data: Any, logger: Optional[logging.Logger] = None) -> None:
        """See `lastmile_eval.rag.debugger.api.tracing.LastMileTracer.log()`"""
        if logger is None:
            logger = self.logger
        TraceDataSingleton().log_data(data, logger)

    def log_feedback(
        self,
        feedback: str | dict[str, Any],
        trace_id: Optional[Union[str, int]] = None,
        span_id: Optional[Union[str, int]] = None,
    ) -> None:
        """
        Feedback is a string and optionally a free-form JSON serializable object that can be
        Specify a trace_id to link the feedback to a specific trace.
        Specify a span_id AND trace_id to link the feedback to a specific span.
        If neither are specified, the feedback is linked to the project.
        """
        lastmile_endpoint = (
            f"{get_website_base_url()}/api/evaluation_feedback/create"
        )

        payload: dict[str, Any] = {}
        if self.project_id is not None:
            payload["projectId"] = self.project_id

        if isinstance(feedback, str):
            payload["feedback"] = {"text": feedback, "type": "text"}
        else:  # type is dict
            payload["feedback"] = feedback

        if span_id is not None:
            if isinstance(span_id, str):
                span_id = int(span_id)
            if isinstance(trace_id, str):
                trace_id = int(trace_id)

            if trace_id is None:
                raise ValueError(
                    "If you specify a span_id, you must also specify a trace_id"
                )

            payload["traceId"] = convert_int_id_to_hex_str(trace_id)
            payload["spanId"] = convert_int_id_to_hex_str(span_id)
        elif trace_id is not None:
            if isinstance(trace_id, str):
                trace_id = int(trace_id)
            payload["traceId"] = convert_int_id_to_hex_str(trace_id)

        response: Response = requests.post(
            lastmile_endpoint,
            headers={"Authorization": f"Bearer {self.lastmile_api_token}"},
            json=payload,
            timeout=TIMEOUT,
        )
        raise_for_status(
            response,
            f"Error logging feedback for project {self.project_name} (payload={json.dumps(payload)})",
        )

        return response.json()

    def log_binary_feedback(self, value: bool, trace_id: str) -> None:
        """
        Log binary feedback (positive or negative) for a specific trace.

        Binary feedback represents a user's simple sentiment or reaction to the assistant's
        response. Examples include thumbs up/down, helpful/unhelpful, or any other
        binary sentiment indicator.

        Args:
            value (bool): The binary feedback value. True for positive feedback,
                False for negative feedback.
            trace_id (str): The ID of the trace associated with the feedback.
        """
        int_value = 1 if value else 0
        feedback: dict[str, Any] = {"type": "binary", "value": int_value}
        self.log_feedback(feedback, trace_id=trace_id)

    def log_numeric_feedback(self, value: float, trace_id: str) -> None:
        """
        Log numeric feedback for a specific trace.

        Numeric feedback represents a user's rating or score given to the assistant's
        response. It allows users to provide a more granular assessment of the response
        quality compared to binary feedback.

        Args:
            value (float): The numeric feedback value, typically in a defined range
                (e.g., 1 to 5).
            trace_id (str): The ID of the trace associated with the feedback.
        """
        feedback: dict[str, Any] = {"type": "score", "value": value}
        self.log_feedback(feedback, trace_id=trace_id)

    def log_categorical_feedback(
        self, value: str, categories: list[str], trace_id: str
    ) -> None:
        """
        Log categorical feedback for a specific trace.

        Categorical feedback allows users to select a category or label that best
        represents their assessment or sentiment regarding the assistant's response.
        The available categories are predefined and provided as a list.

        Args:
            value (str): The selected category or label for the feedback.
            categories (list[str]): The list of available categories or labels to
                choose from.
            trace_id (str): The ID of the trace associated with the feedback.
        """
        feedback: dict[str, Any] = {
            "type": "enum",
            "value": value,
            "enum": categories,
        }
        self.log_feedback(feedback, trace_id=trace_id)

    def log_text_feedback(self, value: str, trace_id: str) -> None:
        """
        Log text feedback for a specific trace.

        Text feedback allows users to provide open-ended and unstructured feedback
        about the assistant's response. It can capture more detailed and specific
        comments or suggestions from the user.

        Args:
            value (str): The text feedback provided by the user.
            trace_id (str): The ID of the trace associated with the feedback.
        """
        feedback: dict[str, str] = {"type": "text", "value": value}
        self.log_feedback(feedback, trace_id=trace_id)

    def set_project(self) -> None:
        """
        Gets the project or creates a new one if it doesn't exist.
        TODO: allow user to specify project visibility to allow personal project in an org
        """
        if self.project_name is None:
            return

        list_project_endpoint = f"{get_website_base_url()}/api/evaluation_projects/list?{urlencode({'name': self.project_name})}"
        response = requests.get(
            list_project_endpoint,
            headers={"Authorization": f"Bearer {self.lastmile_api_token}"},
            timeout=60,
        )
        list_resp = log_for_status(
            response,
            f"Unable to set project: Error fetching projects with name {self.project_name}",
        )
        match list_resp:
            case Ok(list_resp):
                evaluation_projects = response.json()["evaluationProjects"]
                project_exists = len(evaluation_projects) > 0

                if not project_exists:
                    # TODO: Make wrapper function to handle retries automatically
                    # in all our request calls
                    create_project_endpoint = f"{get_website_base_url()}/api/evaluation_projects/create"
                    request_session = requests.Session()
                    retries = Retry(
                        total=1,
                        backoff_factor=1,  # 0s, 2s, 4s, 8s, 16s
                        # status_forcelist=[ 502, 503, 504 ]
                    )
                    request_session.mount(
                        "https://", HTTPAdapter(max_retries=retries)
                    )
                    response = request_session.post(
                        create_project_endpoint,
                        headers={
                            "Authorization": f"Bearer {self.lastmile_api_token}"
                        },
                        json={
                            "name": self.project_name,
                        },
                        timeout=60,  # TODO: Remove hardcoding
                    )
                    create_resp = log_for_status(
                        response,
                        f"Unable to set project: Error creating project {self.project_name}",
                    )
                    match create_resp:
                        case Ok(create_resp):
                            self.project_id = response.json()["id"]
                        case Err(create_resp):
                            return
                else:
                    self.project_id = evaluation_projects[0]["id"]
            case Err(list_resp):
                return

    def set_rag_flow_type(
        self,
        rag_flow_type: RagFlowType | None,
        ingestion_trace_id: Optional[str] = None,
    ) -> None:
        self.rag_flow_type = rag_flow_type

        if (
            ingestion_trace_id is not None
            and rag_flow_type == RagFlowType.QUERY
        ):
            self.ingestion_trace_id = ingestion_trace_id

    def store_trace_id(
        self,
        key: str,
        trace_id: int,
        span_id: Optional[int] = None,
        metadata: Optional[dict[str, Any]] = None,
        value_override: Any = None,  # TODO: restrict or remove
    ) -> None:
        if self.project_id is None:  # type: ignore[has type]
            logging.error(
                "Unable to store trace id: "
                "Project ID must be set before storing key-value pairs. Try re-initializing the tracer object",
                stack_info=True,
            )
            return

        store_key_value_pair(
            self.project_id,
            key,
            span_id,
            trace_id,
            metadata,
            value_override,
        )

    def read_trace_id(
        self,
        key: str,
    ) -> tuple[str, str]:
        if self.project_id is None:  # type: ignore[has type]
            raise ValueError(
                "Project ID must be set before storing key-value pairs. Try re-initializing the tracer object"
            )
        return read_key_value_pair(self.project_id, key)


def _get_name_with_span_count(name: str):
    """
    Insert the span count at beginning of span name so that we can tell spans
    apart that have the same name. Also increment the span count in the trace
    data singleton to keep track of the number of spans created.
    """
    trace_data_singleton = TraceDataSingleton()
    trace_data_singleton.span_count += 1
    return f"{trace_data_singleton.span_count} - {name}"


def _update_param_key_if_needed(key: str, span_index: int) -> str:
    """
    If a parameter key already exists in the trace's param set, append a
    unique identifier to the key to avoid overwriting the existing value
    """
    if key in TraceDataSingleton().get_params():
        return f"{key}-{span_index}"
    return key
