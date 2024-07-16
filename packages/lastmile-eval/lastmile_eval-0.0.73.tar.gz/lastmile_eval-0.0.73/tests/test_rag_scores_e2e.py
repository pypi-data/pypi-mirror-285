"""
Automted tests for the lastmile_eval package.
"""

import json
from dataclasses import dataclass
from typing import Any

import numpy as np

from lastmile_eval.utils import (
    _get_rag_eval_scores_helper,  # type: ignore[Fine to import for test]
)
from lastmile_eval.utils import (
    _MockAuthenticationConfig,  # type: ignore[Fine to import for test]
)


@dataclass(frozen=True)
class _MockResponse:
    status_code: int
    text: str


def test_get_rag_eval_scores_single_value():
    """
    Basic unit test for testing the rag eval API success case.
    """
    queries = ["what color is the sky?"]
    statement1 = "the sky is red"
    data = [statement1]
    responses = [statement1]

    mock_response = _MockResponse(
        status_code=200,
        text=json.dumps({"p_faithful": [0.9956]}),
    )
    mock_auth = _MockAuthenticationConfig(
        post_fn=_post_fn_with_expected_response(mock_response)
    )

    #  TODO: dict values might have to be generalized later based on
    # metric criteria
    response_scores: dict[str, list[float]] = _get_rag_eval_scores_helper(
        queries, data, responses, mock_auth
    )
    assert isinstance(response_scores, dict), f"{type(response_scores)=}"
    assert "p_faithful" in response_scores, f"{response_scores=}"
    assert len(response_scores["p_faithful"]) == 1, f"{response_scores=}"
    a_resp = np.array(response_scores["p_faithful"])
    a_expected = np.array([0.9956])
    assert np.isclose(a_resp, a_expected).all()


def test_get_rag_eval_scores():
    """
    Basic unit test for testing the rag eval API success case.
    """
    queries = ["what color is the sky?", "what color is the sky?"]
    statement1 = "the sky is red"
    statement2 = "the sky is blue"
    data = [statement1, statement1]
    responses = [statement1, statement2]

    mock_response = _MockResponse(
        status_code=200,
        text=json.dumps({"p_faithful": [0.9956, 6.857e-05]}),
    )
    mock_auth = _MockAuthenticationConfig(
        post_fn=_post_fn_with_expected_response(mock_response)
    )

    #  TODO: dict values might have to be generalized later based on
    # metric criteria
    response_scores: dict[str, list[float]] = _get_rag_eval_scores_helper(
        queries, data, responses, mock_auth
    )
    assert isinstance(response_scores, dict), f"{type(response_scores)=}"
    assert "p_faithful" in response_scores, f"{response_scores=}"
    assert len(response_scores["p_faithful"]) == 2, f"{response_scores=}"
    a_resp = np.array(response_scores["p_faithful"])
    a_expected = np.array([0.9956, 6.857e-05])
    assert np.isclose(a_resp, a_expected).all()


def _post_fn_with_expected_response(
    mock_response: _MockResponse,
) -> Any:
    def _post_fn(
        _data: Any,  # TODO: type this better
        _endpoint_url: str | None = None,
        _headers: dict[str, str] | None = None,
        _timeout: int | None = None,
    ):
        # TODO: This is not a real response, so we'll have to
        # fix the typing stuff. It's an internl fn so it's OK.
        return mock_response

    return _post_fn
