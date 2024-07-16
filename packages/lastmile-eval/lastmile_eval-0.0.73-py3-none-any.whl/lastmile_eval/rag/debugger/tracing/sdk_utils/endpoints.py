from typing import Any, Optional
from urllib.parse import urlencode

import requests
from lastmile_eval.rag.debugger.common.utils import (
    get_lastmile_api_token,
    WEBSITE_BASE_URL,
)


def store_key_value_pair(
    project_id: str,
    key: str,
    span_id: Optional[int] = None,
    trace_id: Optional[int] = None,
    metadata: Optional[dict[str, Any]] = None,
    value_override: Any = None,  # TODO: restricted or remove
) -> None:
    """
    Store a key-value pair in remote storage. This is useful for retrieving
    a span or trace later on when performing online feedback or debugging.
    """
    endpoint = f"{WEBSITE_BASE_URL}/api/evaluation_key_value_store/create"

    if metadata is None:
        metadata = {}

    if span_id is not None and trace_id is None:
        raise ValueError(
            "If you specify a span_id, you must also specify a trace_id"
        )

    if value_override is not None and trace_id is not None:
        raise ValueError(
            "If you specify a value_override, you cannot specify a trace_id or a span_id"
        )

    # expect value to be span id, and metadata to contain traceID
    # TODO: update data model to have traceID and spanID as separate fields
    metadata["trace_id"] = str(trace_id)  # type: ignore

    payload = {
        "projectId": project_id,
        "metadata": metadata,
        "value": str(span_id) or value_override,
        "key": key,
    }

    api_token = get_lastmile_api_token()
    # TODO: Update to http_post
    response = requests.post(
        endpoint,
        json=payload,
        headers={"authorization": f"Bearer {api_token}"},
        timeout=60,  # TODO: remove hardcoded value
    )
    if not response.ok:
        raise ValueError(f"Error storing key-value pair: {response.json()}")
    return response.json()


def read_key_value_pair(
    project_id: str,
    key: str,
) -> tuple[str, str]:
    """
    Returns a pair of (TraceID, SpanID). If span_id is not found, span_id will be None

    Read a key-value pair from remote storage. This is useful for retrieving
    a span or trace later on when performing online feedback or debugging.
    """
    api_token = get_lastmile_api_token()

    query_params = {
        "projectId": project_id,
        "key": key,
    }
    endpoint = f"{WEBSITE_BASE_URL}/api/evaluation_key_value_store/read?{urlencode(query_params)}"
    # TODO: Update to http_get
    response = requests.get(
        endpoint,
        headers={"authorization": f"Bearer {api_token}"},
        timeout=60,  # TODO: remove hardcoded value
    )
    if not response.ok:
        raise ValueError(f"Error reading key-value pair: {response.text}")
    try:
        print(response.json())
        span_id = response.json().get("value")
        trace_id = response.json().get("metadata", {}).get("trace_id")
        return (trace_id, span_id)

    except Exception as e:
        raise KeyError("Could not find key in remote storage") from e
