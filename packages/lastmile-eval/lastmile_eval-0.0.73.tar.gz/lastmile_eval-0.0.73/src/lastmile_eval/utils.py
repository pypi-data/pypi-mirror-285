"""
Simple utils wrapper for evaluation framework.
"""

import base64
import json
from dataclasses import dataclass, field
from typing import Any

import requests

MEM_30GB_ENDPOINT_ID = "1348328910118453248"  # Replace with enum next PR


@dataclass(frozen=True)
class RagEvalConfig:
    """
    The evaluation configuration to tell our endpoint how to evaluate
    the request
    """

    model_names: list[str] = field(default_factory=lambda: ["p-faithful-v0"])


@dataclass(frozen=True)
class _RealAuthenticationConfig:
    api_token: str


@dataclass(frozen=True)
class _MockAuthenticationConfig:
    post_fn: Any  # TODO type this


_AuthenticationConfig = _RealAuthenticationConfig | _MockAuthenticationConfig


def get_rag_eval_scores(
    queries: list[str],
    data: list[str],
    responses: list[str],
    api_token: str,
    config: RagEvalConfig | None = None,
    # TODO (rossdan): Add options for batch and retry policies
    # TODO: try to type this better than `Any`.
    # However, it's better to underpromise structure than overpromise, if we need to change it.
) -> dict[str, Any]:
    """
    Get faithfulness scores for a batch of N LLM's outputs in relation to the data
    provided as well as the queries. The queries, data, and responses
    must all be lists of length N.

    @param queries (list[str]): Queries that were passed to the LLM
    @param data (list[str]): Ground truth upon which we will evaluate the
        LLM's outputs (for example, you can use the data that was given to
        the LLM along with the queries)
    @param responses (list[str]): Output of the LLM when given the queries
    @param api_token (str): API key for the LastMile evaluation endpoint.
        Get it from here: https://lastmileai.dev/settings?page=tokens
    @param model_endpoint_id (str): enum for which model to use in the endpoint

    @return dict: JSON responses containing faithfulness scores and any relevant metadata.

    Example
    Input:
        queries = ["what color is the sky?", "what color is the sky?"]
        statement1 = "the sky is red"
        statement2 = "the sky is blue"
        data = [statement1, statement1]
        responses = [statement1, statement2]
        get_rag_eval_scores(queries, data, responses, api_token)
    Output:
        {'p_faithful': [0.9956, 6.857e-05]}
    """

    authentication_config = _RealAuthenticationConfig(api_token=api_token)

    return _get_rag_eval_scores_helper(
        queries, data, responses, authentication_config, config
    )


def _get_rag_eval_scores_helper(
    queries: list[str],
    data: list[str],
    responses: list[str],
    authentication_config: _AuthenticationConfig,
    config: RagEvalConfig | None = None,
) -> dict[str, list[float]]:
    if config is None:
        config = RagEvalConfig()

    # TODO: In the future, instead of this, we should probably set up endpoints
    # based on memory requirements, not specific models.
    # Any endpoint should be able to run any model.
    model_name_to_endpoint_id = {
        "p-faithful-v0": MEM_30GB_ENDPOINT_ID,
    }

    if len(config.model_names) != 1:
        raise ValueError(
            "Currently, exactly one model must be evaluated at a time."
        )
    model_endpoint_id = model_name_to_endpoint_id[config.model_names[0]]

    # TODO: Change this to an object type because it gets unwieldy to have 3
    # separate arrays and then also add metadata etc
    query_length = len(queries)
    if len(data) != query_length or len(responses) != query_length:
        raise ValueError(
            "Length of data, queries, and responses arrays must all be equal."
        )
    # TODO (rossdan): Add batch policies depending on premise + hypothesis sizes
    http_response = requests.Response = _call_eval_api(
        queries,
        data,
        responses,
        authentication_config,
        "https://lastmileai.dev/api/evaluation",
        model_endpoint_id,
    )
    if http_response.status_code != 200:
        # TODO (rossdan): Add retry policies
        raise ValueError(
            f"Error in evaluation http responses: {http_response.text}"
        )

    return json.loads(http_response.text)


def _call_eval_api(  # pylint: disable=too-many-arguments
    queries: list[str],
    data: list[str],
    responses: list[str],
    authentication_config: _AuthenticationConfig,
    endpoint_url: str,
    model_endpoint_id: str | None,
) -> requests.Response:
    """
    Call the LastMile endpoint to perform evaluation on a granular segment
    of data. This is a low-level function that is unaware on how the infra
    surrounding this call (ex: batch + retry policy) was handled.
    """
    premises = list(
        f"{data_item}. Query: {query}"
        for query, data_item in zip(queries, data)
    )
    hypotheses = responses
    encoded_premises = list(map(_encode_string, premises))
    encoded_hypotheses = list(map(_encode_string, hypotheses))

    # TODO: type the payload better
    payload: Any = {
        "premise": encoded_premises,
        "hypothesis": encoded_hypotheses,
    }

    if model_endpoint_id:
        payload["modelEndpointId"] = model_endpoint_id

    match authentication_config:
        case _RealAuthenticationConfig(api_token=api_token):
            return requests.post(
                endpoint_url,
                headers={"Authorization": f"Bearer {api_token}"},
                json=payload,
                # TODO (rossdan): Add timeout and retry policies
                timeout=60,
            )
        case _MockAuthenticationConfig(post_fn=post_fn):
            return post_fn(
                _data=payload,
            )


def _encode_string(s: str) -> str:
    """
    Returns base64 encoded string to make it URL-safe for passing over the wire.
    """
    encoded_bytes = base64.b64encode(s.encode("utf-8"))
    return encoded_bytes.decode("utf-8")
