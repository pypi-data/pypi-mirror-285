import logging
import mimetypes
import os
from copy import deepcopy
from datetime import datetime
from enum import Enum
from random import randint
import re
from typing import Any, Optional
import requests
from requests import Response
from result import Err, Ok


from ..common.core import (
    ParamInfoKey,
)
from ..common.types import RagFlowType
from ..common.utils import (
    get_auth_header,
    get_lastmile_api_token,
    http_get,
    http_post,
    SHOW_DEBUG,
    Singleton,
    log_for_status,
    WEBSITE_BASE_URL,
)


class TraceDataSingleton(Singleton):
    """
    Singleton object to store trace-level data. By delegating the state
    management to this class, we also ensure that it is not out of sync
    when shared across multiple classes.

    For example, this is used to reference the same data in
    LastMileOTLSpanExporter, LastMileTracer, and the SDK util files
    """

    _is_already_initialized = False

    def __init__(self):
        if self._is_already_initialized:
            return

        super().__init__()

        self.global_params: dict[str | ParamKey, Any] = {}

        self.trace_specific_params = deepcopy(self.global_params)
        self.rag_flow_type: Optional[RagFlowType] = None
        self.ingestion_trace_id: Optional[str] = None

        # TODO: Change type from dict to class with explicit field and schema
        self.rag_event_sequence: list[dict[str, Any]] = []
        self._added_spans: set[str] = set()
        self._rag_event_for_trace: Optional[dict[str, Any]] = None

        # To populate later when we first create a span using one of
        # these two methods:
        #   1) `lastmile_tracer.start_as_current_span()`
        #   2) `lastmile_tracer.start_span()`
        # See opentelemetry.sdk.trace for their SDK API
        self._trace_id: Optional[str] = None

        self.logger_filepaths: set[str] = set()

        self._is_already_initialized = True
        self.project_id: Optional[str] = None
        self.previous_trace_id: Optional[str] = None

        self._span_count: int = 0

    def add_rag_event_for_span(
        self,
        # TODO: Explicit schema for event_payload
        event_payload: dict[str, Any],
    ) -> None:
        """
        Add RagEvent to the trace-level data. Duplicate from
        add_rag_query_event for now just to get unblocked
        """
        span_id = event_payload.get("span_id")
        if span_id is None:
            logging.error(
                "Unable to add rag event for span: Could not extract span_id from event payload",
                stack_info=True,
            )
            return
        if span_id in self._added_spans:
            logging.error(  # pylint: disable=logging-fstring-interpolation
                f"Unable to add rag event for span:"
                f"You have already added an event for span id '{span_id}'. Please check for other calls to `add_rag_event_for_span()` within the same span and either remove them, or explicitly pass the `span_id` argument in `add_rag_event_for_span()`."
                "Unable to add rag event for span: Could not extract span_id from event payload",
                stack_info=True,
            )
            return
        if self.trace_id is None:
            logging.error(
                "Unable to add rag event for span:"
                "Unable to detect current trace_id. You must be inside of a trace in order to log a RagEvent"
                "Unable to add rag event for span: Could not extract span_id from event payload",
                stack_info=True,
            )
            return
        rag_flow_type = event_payload.get("rag_flow_type")
        if rag_flow_type is not None:
            if self.rag_flow_type is None:
                self.rag_flow_type = rag_flow_type
            elif self.rag_flow_type != rag_flow_type:
                logging.error(  # pylint: disable=logging-fstring-interpolation
                    f"Unable to add rag event for span:"
                    f"Trying to call `add_rag_event_for_span` with rag_flow_type arg as {rag_flow_type}, but you already set the rag flow type for this trace to {self.rag_flow_type}"
                    "Unable to add rag event for span: Could not extract span_id from event payload",
                    stack_info=True,
                )
                return
        # TODO (rossdan): Should have error if doing ingestion_trace_id but
        # the rag_flow_type is explicitly set to INGESTION
        ingestion_trace_id = event_payload.get("ingestion_trace_id")
        if ingestion_trace_id is not None and self.ingestion_trace_id is None:
            self.ingestion_trace_id = ingestion_trace_id

        self._added_spans.add(span_id)

        # Add the root span to the first index so that we can first try to extract
        # input/output from the root span
        # TODO (rossdan): To be very thorough, we should make `rag_event_sequence`
        # a tree instead of an array so that we can traverse it in proper span order
        parent_span_id = event_payload.get("parent_span_id")
        if parent_span_id is None:
            self.rag_event_sequence.insert(0, event_payload)
        else:
            self.rag_event_sequence.append(event_payload)

    def add_rag_event_for_trace(
        self,
        # TODO: Explicit schema for event_payload
        event_payload: dict[str, Any],
    ) -> None:
        """
        Add RagEvent to the trace-level data. Same functionality as
        `add_rag_event_for_span` except this is used for the overall
        trace-level data instead of at the span level.
        """
        if self.trace_id is None:
            logging.error(
                "Unable to add rag event for trace:"
                "Unable to detect current trace_id. You must be inside of a trace in order to log a RagEvent"
                "Unable to add rag event for span: Could not extract span_id from event payload",
                stack_info=True,
            )
            return
        if self._rag_event_for_trace is not None:
            logging.error(  # pylint: disable=logging-fstring-interpolation
                f"Unable to add rag event for trace:"
                f"You have already added an event for trace id '{self.trace_id}'. Please check for other calls to `log_trace_event()` within the same trace."
                "Unable to add rag event for span: Could not extract span_id from event payload",
                stack_info=True,
            )
            return
        rag_flow_type = event_payload.get("rag_flow_type")
        if rag_flow_type is not None:
            if self.rag_flow_type is None:
                self.rag_flow_type = rag_flow_type
            elif self.rag_flow_type != rag_flow_type:
                logging.error(  # pylint: disable=logging-fstring-interpolation
                    f"Unable to add rag event for trace:"
                    f"Trying to call `log_trace_event` with rag_flow_type arg as {rag_flow_type}, but you already set the rag flow type for this trace to {self.rag_flow_type}"
                    "Unable to add rag event for span: Could not extract span_id from event payload",
                    stack_info=True,
                )
                return

        # TODO (rossdan): Should have error if doing ingestion_trace_id but
        # the rag_flow_type is explicitly set to INGESTION
        ingestion_trace_id = event_payload.get("ingestion_trace_id")
        if ingestion_trace_id is not None and self.ingestion_trace_id is None:
            self.ingestion_trace_id = ingestion_trace_id

        self._rag_event_for_trace = event_payload

    def get_params(self) -> dict[str, Any]:
        """
        Get the parameters saved in the trace-level data (which is the same as
        global if no trace exists)
        """
        return {str(k): v for (k, v) in self.trace_specific_params.items()}

    def register_param(self, key: str, value: Any) -> None:
        """
        Register a parameter to the trace-level data (and global params if no
        trace is defined). If the key is already defined, create a new key
        which is "key-1", "key-2", etc.
        """
        # Use string literals instead of enums because if we have the same key
        # we want to be able to differentiate them more easily
        # (ex: "chunks" vs. "chunks-1") instead of comparing enums
        # (ex: "EventPayload.CHUNKS" vs. "chunks-1")
        if isinstance(key, Enum):
            key = key.value

        param_key = ParamInfoKey(key)
        should_write_to_global = False
        if self.trace_id is None:
            should_write_to_global = True

        # Even if trace_id is None (not in a trace), we still need to update
        # trace_specific_params so it's not out of sync with global_params

        # For auto-instrumentation, we have tons of events with the same
        # event_name so adding more specific parameters there
        if param_key in self.trace_specific_params:
            i = 1
            while param_key + "-" + str(i) in self.trace_specific_params:
                i += 1
            param_key = ParamInfoKey(param_key + "-" + str(i))
        self.trace_specific_params[param_key] = value

        if should_write_to_global:
            param_key = ParamInfoKey(key)
            if param_key in self.global_params:
                i = 1
                while param_key + "-" + str(i) in self.global_params:
                    i += 1
                param_key = ParamInfoKey(param_key + "-" + str(i))
            self.global_params[param_key] = value

    def clear_params(
        self,
        should_clear_global_params: bool = False,
    ) -> None:
        """
        Clear the parameters saved in the trace-level data, as well as
        global params if `should_clear_global_params` is true.
        """
        self.trace_specific_params.clear()
        if should_clear_global_params:
            self.global_params.clear()

    def log_to_rag_traces_table(
        self, lastmile_api_token: str
    ) -> Optional[Response]:
        """
        Log the trace-level data to the RagIngestionTraces or RagQueryTraces
        table via the respective LastMile endpoints. This logs data that
        was added to the singleton via one of these methods (checking in
        order):
            1. `add_rag_event_for_trace`
                - extract input/output and event_data directly
            2. `add_rag_event_for_span`
                - extract input/output based on earliest available input, and
                    latest available output
                    #TODO: Might want to change this to be tree traversal
                    based on post-order traversal (start with root) instead of
                    array
                - if not possible, extract event_data from root (1st) event
            3. if no calls to either method above was made, then just pass in
                empty trace-level data (can still have other stuff like
                paramSet)

        @param lastmile_api_token (str): Used for authentication.
            Create one from the "API Tokens" section from this website:
            https://lastmileai.dev/settings?page=tokens

        @return Response: The response from the LastMile endpoint
        """
        if self.trace_id is None:
            logging.error(
                "Unable to detect trace id. Please create a root span using `tracer.start_as_current_span()`\n stacktrace: \n:%s",
                stack_info=True,
            )
            return

        payload: dict[str, Any] = {
            "traceId": self.trace_id,
            "paramSet": self.get_params(),
            # TODO: Add fields below
            # metadata
            # orgId
            # visibility
        }
        if self.project_id is not None:
            payload["projectId"] = self.project_id

        if self._rag_event_for_trace is not None:
            # Process the trace-level data from `add_rag_event_for_trace()`
            event_input = self._rag_event_for_trace.get("input")
            if event_input is not None:
                payload["input"] = event_input

            event_output = self._rag_event_for_trace.get("output")
            if event_output is not None:
                payload["output"] = self._rag_event_for_trace.get("output")

            event_data = self._rag_event_for_trace.get("event_data")
            if event_data is not None:
                payload["eventData"] = event_data
        elif self.rag_event_sequence:
            # Try extracing the input/output from the root (first) span
            input_value = self.rag_event_sequence[0].get("input")
            output_value = self.rag_event_sequence[0].get("output")

            if not input_value or not output_value:
                # Try extracing the first possible input or last possible output
                start = 0
                end = len(self.rag_event_sequence) - 1
                while start <= end:
                    if not input_value:  # default is empty string
                        input_value = self.rag_event_sequence[start].get(
                            "input"
                        )
                        start += 1
                    if not output_value:  # default is empty string
                        output_value = self.rag_event_sequence[end].get(
                            "output"
                        )
                        end -= 1
                    if input_value and output_value:
                        break

            if input_value and output_value:
                payload["input"] = input_value
                payload["output"] = output_value
            else:
                root_event_data = self.rag_event_sequence[0].get("event_data")
                if root_event_data:
                    payload["eventData"] = root_event_data

        token = get_lastmile_api_token(lastmile_api_token)
        headers = get_auth_header(token)

        if self.rag_flow_type == RagFlowType.INGESTION:
            if SHOW_DEBUG:
                print(f"TraceDataSingleton.log_to_traces_table: {payload=}")

            endpoint = "rag_ingestion_traces/create"
            response = http_post(WEBSITE_BASE_URL, endpoint, headers, payload)

            def _create_resp(response: Response):
                return log_for_status(
                    response,
                    "Error creating rag ingestion trace",
                )

            create_resp = response.and_then(_create_resp)

            match create_resp:
                case Ok(create_resp_ok):
                    return create_resp_ok
                case Err(_error):
                    return

        # Default to RAGQueryTraces if RagFlowType is unspecified
        payload.update(
            # deprecated: add structured data required for RagQueryTrace DB
            {
                "query": {},
                "context": {},
                "fullyResolvedPrompt": {},
                "llmOutput": {},
            }
        )
        if self.ingestion_trace_id is not None:
            payload["ingestionTraceId"] = self.ingestion_trace_id

        if SHOW_DEBUG:
            print(f"TraceDataSingleton.log_to_rag_traces_table {payload=}")

        endpoint = "rag_query_traces/create"
        response = http_post(WEBSITE_BASE_URL, endpoint, headers, payload)

        def _create_resp(response: Response):
            return log_for_status(
                response,
                "Error creating rag query trace",
            )

        create_resp = response.and_then(_create_resp)

        match create_resp:
            case Ok(create_resp_ok):
                return create_resp_ok
            case Err(_error):
                return

    def log_span_rag_events(self, lastmile_api_token: str) -> None:
        if not self.rag_event_sequence:
            return

        if self.trace_id is None:
            logging.error(
                "Unable to log rag event:"
                "Unable to detect trace id. Please create a root span using `tracer.start_as_current_span()`"
                "Unable to add rag event for span: Could not extract span_id from event payload",
                stack_info=True,
            )
            return

        for event_payload in self.rag_event_sequence:
            # TODO: Schematize event data payload
            payload: dict[str, Any] = {
                # Required fields by user (or auto-instrumentation)
                "eventName": event_payload["event_name"] or "",
                "input": event_payload["input"] or {},
                "output": event_payload["output"] or {},
                "eventData": event_payload["event_data"] or {},
                "metadata": {} or "",  # TODO: Allow user to define metadata
                # Required but get this from our data when marking event
                "traceId": self.trace_id,
                "spanId": event_payload["span_id"],
                # TODO: Add fields below
                # orgId
                # visibility
            }
            if self.project_id is not None:
                payload["projectId"] = self.project_id
            if self.ingestion_trace_id is not None:
                payload["ingestionTraceId"] = self.ingestion_trace_id
            if SHOW_DEBUG:
                print(f"TraceDataSingleton.log_span_rag_events: {payload=}")

            token = get_lastmile_api_token(lastmile_api_token)
            headers = get_auth_header(token)
            endpoint = "rag_events/create"
            response = http_post(WEBSITE_BASE_URL, endpoint, headers, payload)

            match response:
                case Ok(response_ok):
                    log_for_status(response_ok, "Error creating rag event")
                case Err(err):
                    raise err
        return None

    def log_data(self, data: Any, logger: logging.Logger) -> None:
        """
        Log the data, save it to a file (if it doesn't exist) so that we can
        export it later
        """
        # TODO: Allow user to specify logger level instead of just info
        logger.info(repr(data))

        # TODO: Cache handlers so we don't have to check every time
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                filepath = handler.baseFilename
                self.logger_filepaths.add(filepath)
            else:
                # TODO: If file handler is not present, then create one
                # based on logger name and add it to logger
                # handler.get_name()
                pass

    def upload_log_data(self, lastmile_api_token: str) -> None:
        """
        1. Get all the data from logger files, run foreach on all
        2. S3 bucket upload file
        3. api/upload/create --> get upload Id
        4. evaluation_trace_log/create
        """
        for filepath in self.logger_filepaths:
            if SHOW_DEBUG:
                print(f"Uploading {filepath} log data to LastMile...")

            # Upload log file to S3
            s3_upload_obj = _upload_to_s3(filepath, lastmile_api_token)
            if s3_upload_obj is None:
                # TODO: Add true error handling to logger files
                print(f"Error: Failed to upload logger file {filepath} to S3")
                continue

            # Create upload object to LastMile DB
            # TODO update to http_post
            upload_response = requests.post(
                f"{WEBSITE_BASE_URL}/api/upload/create",
                headers={"Authorization": f"Bearer {lastmile_api_token}"},
                json={
                    "url": s3_upload_obj["url"],
                    "metadata": s3_upload_obj["metadata"],
                },
                timeout=60,  # TODO: Remove hardcoding
            )
            create_resp = log_for_status(
                upload_response,
                f"Error creating upload object with S3 url {s3_upload_obj['url']}",
            )
            match create_resp:
                case Ok(create_resp):
                    # Create evaluation trace log to LastMile DB
                    upload_id = upload_response.json()["id"]
                    payload = {"traceId": self.trace_id, "uploadId": upload_id}
                    if self.project_id is not None:
                        payload["projectId"] = self.project_id
                    # TODO: Update to http_post
                    log_response = requests.post(
                        f"{WEBSITE_BASE_URL}/api/evaluation_trace_log/create",
                        headers={
                            "Authorization": f"Bearer {lastmile_api_token}"
                        },
                        json=payload,
                        timeout=60,  # TODO: Remove hardcoding
                    )
                    log_for_status(
                        log_response,
                        f"Error creating evaluation trace log with payload: {payload}",
                    )
                    # TODO handle or return early
                case Err(create_resp):
                    return

    def reset(self) -> None:
        """
        Reset the trace-level data
        """
        # allows capture trace id after trace is completed.
        self.previous_trace_id = None
        self.previous_trace_id = self.trace_id

        self.trace_specific_params = deepcopy(self.global_params)
        self.trace_id = None
        self.rag_event_sequence = []
        self._added_spans.clear()
        self._rag_event_for_trace = None
        self.rag_flow_type = None
        self.ingestion_trace_id = None
        self.span_count = 0

        # TODO: Clear log files themselves too
        self.logger_filepaths.clear()

    @property
    def trace_id(  # pylint: disable=missing-function-docstring
        self,
    ) -> Optional[str]:
        return self._trace_id

    @trace_id.setter
    def trace_id(self, value: Optional[str]) -> None:
        self._trace_id = value

    @property
    def span_count(  # pylint: disable=missing-function-docstring
        self,
    ) -> int:
        return self._span_count

    @span_count.setter
    def span_count(self, value: int) -> None:
        self._span_count = value


def _upload_to_s3(
    filepath: str, lastmile_api_token: str
) -> Optional[
    dict[str, Any]  # TODO: Schematize return type for s3_upload_object
]:
    """
    Upload the logger file to S3 and return the URL

    @return S3 upload object if successful, None if not
        s3_upload_object = { "url": string, "metadata": dict }
    """
    token = get_lastmile_api_token(lastmile_api_token)
    endpoint = "upload/policy"
    policy_response = http_get(
        WEBSITE_BASE_URL,
        endpoint,
        headers={
            "content-type": "application/json",
            "Authorization": get_auth_header(token)["Authorization"],
        },
    )

    def _policy_response_result(response: Response):
        return log_for_status(
            response,
            "Error getting upload policy to load file to S3 bucket",
        )

    policy_response_result = policy_response.and_then(_policy_response_result)
    match policy_response_result:
        case Ok(policy_response_result_ok):
            url = "https://s3.amazonaws.com/files.uploads.lastmileai.com"
            policy = policy_response_result_ok.json()
            date_string = _get_date_time_string()
            filename: str = _sanitize_filename(os.path.basename(filepath))
            random_int: int = randint(0, 10001)
            upload_key: str = (
                f"uploads/{policy['userId']}/{date_string}/{random_int}/{filename}"
            )

            mime_type = mimetypes.guess_type(filepath)[0]
            form_data = {
                "key": upload_key,
                "acl": "public-read",
                "Content-Type": mime_type,
                "AWSAccessKeyId": policy["AWSAccessKeyId"],
                "success_action_status": "201",
                "Policy": policy["s3Policy"],
                "Signature": policy["s3Signature"],
                "file": open(filepath, "rb"),
            }

            s3_upload_response = requests.post(
                url,
                files=form_data,
                timeout=60,  # TODO: Remove hardcoding
            )
            s3_url = f"{url}/{upload_key}"
            create_success = log_for_status(
                s3_upload_response,
                f"Error uploading file to S3 url {s3_url}",
            )
            match create_success:
                case Ok(_ok):
                    pass
                case Err(_err):
                    return

            return {
                "url": s3_url,
                "metadata": {
                    "size": os.path.getsize(filepath),
                    "title": filename,
                    "type": mime_type,
                },
            }

        case Err(_error):
            return


def _sanitize_filename(filename: str) -> str:
    """
    Sanitize the filename to remove any characters that are not allowed in
    S3 filenames
    """
    return re.sub(r"[+?]", "_", filename)


def _get_date_time_string() -> str:
    now = datetime.now()
    return now.strftime("%Y_%m_%d_%H_%M_%S")
