import re
from textwrap import dedent
from typing import Any, Iterable, Sequence, cast

import openai.types.chat as openai_types
import openai.types.chat as openai_chat_types
import openai.types.chat.chat_completion as openai_chat_completion_types
import openai.types.chat.chat_completion_message_tool_call as openai_tool_call_types
import openai.types.completion_usage as openai_chat_completion_usage_types

from lastmile_eval.text.metrics_lib import (
    _make_calculate_custom_llm_score_helper,  # type: ignore[private import ok for test]
)
from lastmile_eval.text.openai_batch_lib import MockOpenAIClientConfig


def find_all_substring_idxs(text: str, substr: str) -> list[int]:
    return [m.start() for m in re.finditer(substr, text)]


def _mock_create_fn_semantic_similarity_1(
    messages: Iterable[openai_types.ChatCompletionMessageParam],
    model: str,
    **kwargs: Any,  # TODO: fix this
):
    def _get_score(text: str):
        idxs_happy = find_all_substring_idxs(text, "happy")
        idxs_sad = find_all_substring_idxs(text, "sad")
        idxs_angry = find_all_substring_idxs(text, "angry")
        idxs_miserable = find_all_substring_idxs(text, "miserable")

        if len(idxs_happy) == 2 and all(
            len(idxs) == 0 for idxs in [idxs_sad, idxs_angry, idxs_miserable]
        ):
            return 1.0
        elif len(idxs_happy) == 1 and len(idxs_sad) == 1:
            return 0.2
        elif len(idxs_sad) == 1 and len(idxs_angry) == 1:
            return 0.5
        elif len(idxs_happy) == 1 and len(idxs_miserable) == 1:
            return 0.2
        else:
            raise ValueError(f"Invalid input: {text=}")

    # messages = kwargs["messages"]
    message1 = list(messages)[0]
    text = cast(str, message1["content"])  # type: ignore[fixme]

    score = _get_score(text)
    fn_args = '{"score":' + str(score) + "}"

    out = openai_chat_types.ChatCompletion(
        id="chatcmpl-98X7blliWJMpaf0IVgPSnufl6DCiC",
        choices=[
            openai_chat_completion_types.Choice(
                finish_reason="stop",
                index=0,
                logprobs=None,
                message=openai_chat_types.ChatCompletionMessage(
                    content=None,
                    role="assistant",
                    function_call=None,
                    tool_calls=[
                        openai_chat_types.ChatCompletionMessageToolCall(
                            id="call_6nh6pQUwOZBSFXL50L4yAxfn",
                            function=openai_tool_call_types.Function(
                                arguments=fn_args,
                                name="Score",
                            ),
                            type="function",
                        )
                    ],
                ),
            )
        ],
        created=1711820971,
        model="gpt-3.5-turbo-0125",
        object="chat.completion",
        system_fingerprint="fp_3bc1b5746c",
        usage=openai_chat_completion_usage_types.CompletionUsage(
            completion_tokens=7, prompt_tokens=97, total_tokens=104
        ),
    )
    return out


def _mock_calculate_custom_llm_metric_example_semantic_similarity(
    texts_to_evaluate: Sequence[str],
    references: Sequence[str],
    model_name: str = "gpt-3.5-turbo",
) -> list[float]:
    """

    Args:
        texts_to_evaluate (Sequence[str]): The generated texts to evaluate.
        references (Sequence[str]): The reference texts to evaluate against.
        model_name (str): The name of the evaluation model to use.

    Returns:
        list[float]: A list of custom similarity scores for each text.
    """

    prompt_template = dedent(
        """
        How similar is the following text to the reference on a scale of 0 to 1
        
        Text: {text_to_evaluate}         
        Reference: {reference}
        """
    )

    input_names = ["text_to_evaluate", "reference"]

    client_config = MockOpenAIClientConfig(
        _mock_create_fn_semantic_similarity_1
    )
    scorer = _make_calculate_custom_llm_score_helper(
        prompt_template, model_name, input_names, client_config
    )
    return scorer(texts_to_evaluate, references)


def test_mock_calculate_custom_llm_metric_example_semantic_similarity():
    tte = ["I am happy", "I am sad", "I will be happy"]
    refs = ["I am happy", "I am angry", "you were miserable"]

    output = _mock_calculate_custom_llm_metric_example_semantic_similarity(
        tte, refs
    )

    assert output == [1.0, 0.5, 0.2], f"{output=}"
