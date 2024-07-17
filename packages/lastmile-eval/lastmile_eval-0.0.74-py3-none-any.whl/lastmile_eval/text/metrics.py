from textwrap import dedent
from typing import Any, Sequence, cast

import pandas as pd

# Bleu
from evaluate import EvaluationModule, load  # type: ignore[fixme]

# phoenix arize
from phoenix.evals import (
    HUMAN_VS_AI_PROMPT_RAILS_MAP,
    HUMAN_VS_AI_PROMPT_TEMPLATE,
    QA_PROMPT_RAILS_MAP,
    QA_PROMPT_TEMPLATE,
    RAG_RELEVANCY_PROMPT_RAILS_MAP,
    RAG_RELEVANCY_PROMPT_TEMPLATE,
    TOXICITY_PROMPT_RAILS_MAP,
    TOXICITY_PROMPT_TEMPLATE,
    OpenAIModel,
    llm_classify,
)
from phoenix.evals.default_templates import (
    SUMMARIZATION_PROMPT_RAILS_MAP,
    SUMMARIZATION_PROMPT_TEMPLATE,
)

from lastmile_eval.text.metrics_lib import make_llm_score_function
from lastmile_eval.utils import RagEvalConfig, get_rag_eval_scores


def calculate_bleu_score(
    outputs: Sequence[str], ground_truth: Sequence[str]
) -> list[float]:
    """
    Calculate BLEU scores for a set of hypotheses against corresponding GT.


    Args:
        outputs (Sequence[str]): The generated outputs to evaluate.
        ground_truth (Sequence[Sequence[str]]):
        The reference outputs for evaluation.
        Each set of ground_truth corresponds to one text.

    Returns:
        list[float]: A list of BLEU scores for each text-reference pair.

    Raises:
        ValueError: If the number of outputs and the number of sets of ground_truth are not equal.
    """

    if len(outputs) != len(ground_truth):
        raise ValueError(
            f"Number of predictions ({len(outputs)}) and ground_truth ({len(ground_truth)}) must be equal."
        )

    bleu_metric: EvaluationModule = load("bleu")

    def _score_pair(text: str, reference: str) -> float:
        results: dict[Any, Any] = bleu_metric.compute(  # type: ignore[fixme]
            predictions=[text], references=[[reference]]
        )
        return results["bleu"]

    return [
        _score_pair(text, reference)
        for text, reference in zip(outputs, ground_truth)
    ]


def calculate_exact_match_score(
    outputs: Sequence[str], ground_truth: Sequence[str]
) -> list[float]:
    """
    Calculate Exact Match score for a set of hypotheses against corresponding sets of reference outputs.


    Args:
        outputs (Sequence[str]): The generated outputs to evaluate.
        ground_truth (Sequence[str]):
        The reference outputs for evaluation.
        Each set of ground_truth corresponds to one text.

    Returns:
        list[float]: A list of Exact Match scores for each text-reference pair.

    Raises:
        ValueError: If the number of outputs and the number of sets of ground_truth are not equal.
    """

    if len(outputs) != len(ground_truth):
        raise ValueError(
            f"Number of predictions ({len(outputs)}) and ground_truth ({len(ground_truth)}) must be equal."
        )

    def _score_pair(text: str, reference: str) -> float:
        name = "exact_match"
        metric = load(name)
        out = metric.compute(predictions=[text], references=[reference])  # type: ignore[no-untyped-call]
        return out[name]  # type: ignore[no-member]

    return [
        _score_pair(text, reference)
        for text, reference in zip(outputs, ground_truth)
    ]


def calculate_rouge1_score(
    outputs: Sequence[str], ground_truth: Sequence[Sequence[str]]
) -> list[float]:
    """
    Calculate Rouge-1 score for a set of hypotheses against corresponding sets of reference outputs.


    Args:
        outputs (Sequence[str]): The generated outputs to evaluate.
        ground_truth (Sequence[Sequence[str]]):
        The reference outputs for evaluation.
        Each set of ground_truth corresponds to one text.

    Returns:
        list[float]: A list of Rouge-1 scores for each text-reference pair.

    Raises:
        ValueError: If the number of outputs and the number of sets of ground_truth are not equal.
    """

    if len(outputs) != len(ground_truth):
        raise ValueError(
            f"Number of predictions ({len(outputs)}) and ground_truth ({len(ground_truth)}) must be equal."
        )

    bleu_metric: EvaluationModule = load("rouge")

    def _score_pair(text: str, reference: Sequence[str]) -> float:
        results: dict[Any, Any] = bleu_metric.compute(predictions=[text], references=[reference])  # type: ignore[no-untyped-call]
        return results["rouge1"]

    return [
        _score_pair(text, reference)
        for text, reference in zip(outputs, ground_truth)
    ]


def calculate_relevance_score(
    outputs: Sequence[str],
    ground_truth: Sequence[str],
    model_name: str = "gpt-3.5-turbo",
) -> list[float]:
    """
    Evaluates the relevance of input strings against reference strings using a specific evaluation model,
    and returns a list of float scores representing the relevance of each input-reference pair.

    Args:
        inputs (Sequence[str]): A sequence of input strings to be evaluated.
        ground_truth (Sequence[str]): A sequence of reference strings to evaluate the inputs against.

    Returns:
        List[float]: A list of float scores indicating the relevance of each input-reference pair,
                     where 1.0 denotes 'relevant' and 0.0 denotes otherwise.
    """
    openai_model = OpenAIModel(
        model=model_name,
        temperature=0.0,
    )

    return _calculate_relevance_score_helper(
        outputs, ground_truth, model_name, openai_model
    )


def calculate_faithfulness_score(
    outputs: Sequence[str],
    ground_truth: Sequence[str],
    inputs: Sequence[str],
    lastmile_api_token: str,
) -> list[float]:
    config = RagEvalConfig()

    # TODO: instead  of converting to lists, should make get_rag_eval_scores()
    # accept sequences.
    raw_scores = get_rag_eval_scores(
        queries=list(inputs),
        data=list(ground_truth),
        responses=list(outputs),
        api_token=lastmile_api_token,
        config=config,
    )["p_faithful"]
    scores = cast(list[float], raw_scores)
    return scores


def _calculate_relevance_score_helper(
    outputs: Sequence[str],
    ground_truth: Sequence[str],
    model_name: str,
    openai_model: OpenAIModel,
):
    if len(outputs) != len(ground_truth):
        raise ValueError(
            f"Number of predictions ({len(outputs)}) and ground_truth ({len(ground_truth)}) must be equal."
        )

    if model_name not in ["gpt-3.5-turbo", "gpt-4"]:
        raise ValueError(
            f"Model name must be one of 'gpt-3.5-turbo' or 'gpt-4'."
        )
    # Create DataFrame
    df = pd.DataFrame({"input": outputs, "reference": ground_truth})

    guard_rails = list(RAG_RELEVANCY_PROMPT_RAILS_MAP.values())

    classification_results = llm_classify(
        df, openai_model, RAG_RELEVANCY_PROMPT_TEMPLATE, guard_rails
    )

    # Convert the classification results to a list of floats
    relevance_scores = [
        1.0 if label == "relevant" else 0.0
        for label in classification_results["label"].tolist()  # type: ignore[fixme]
    ]

    return relevance_scores


def calculate_toxicity_score(
    outputs: Sequence[str],
    model_name: str = "gpt-3.5-turbo",
) -> list[float]:
    """

    Args:
        outputs (Sequence[str]): A sequence of input strings to be evaluated.

    Returns:
        List[float]
    """
    openai_model = OpenAIModel(
        model=model_name,
        temperature=0.0,
    )

    return _calculate_toxicity_score_helper(outputs, model_name, openai_model)


def _calculate_toxicity_score_helper(
    outputs: Sequence[str],
    model_name: str,
    openai_model: OpenAIModel,
):
    if model_name not in ["gpt-3.5-turbo", "gpt-4"]:
        raise ValueError(
            f"Model name must be one of 'gpt-3.5-turbo' or 'gpt-4'."
        )
    # Create DataFrame
    df = pd.DataFrame({"input": outputs})

    guard_rails = list(TOXICITY_PROMPT_RAILS_MAP.values())

    classification_results = llm_classify(
        df, openai_model, TOXICITY_PROMPT_TEMPLATE, guard_rails
    )

    # Convert the classification results to a list of floats
    toxicity_scores = [
        1.0 if label == "toxic" else 0.0
        for label in classification_results["label"].tolist()  # type: ignore[fixme]
    ]

    return toxicity_scores


def calculate_qa_score(
    outputs: Sequence[str],
    ground_truth: Sequence[str],
    inputs: Sequence[str],
    model_name: str = "gpt-3.5-turbo",
) -> list[float]:
    """

    Args:
        outputs (Sequence[str]): A sequence of input strings to be evaluated.

    Returns:
        List[float]
    """
    openai_model = OpenAIModel(
        model=model_name,
        temperature=0.0,
    )

    return _calculate_qa_score_helper(
        outputs, ground_truth, inputs, model_name, openai_model
    )


def _calculate_qa_score_helper(
    outputs: Sequence[str],
    ground_truth: Sequence[str],
    inputs: Sequence[str],
    model_name: str,
    openai_model: OpenAIModel,
):
    if len(outputs) != len(ground_truth) or len(outputs) != len(inputs):
        raise ValueError(
            f"Number of outputs ({len(outputs)}), ground_truth ({len(ground_truth)}), and inputs ({len(inputs)}) must be equal."
        )

    if model_name not in ["gpt-3.5-turbo", "gpt-4"]:
        raise ValueError(
            f"Model name must be one of 'gpt-3.5-turbo' or 'gpt-4'."
        )
    # Create DataFrame
    df = pd.DataFrame(
        {
            "input": inputs,
            "reference": ground_truth,
            "output": outputs,
        }
    )

    guard_rails = list(QA_PROMPT_RAILS_MAP.values())

    classification_results = llm_classify(
        df, openai_model, QA_PROMPT_TEMPLATE, guard_rails
    )

    # Convert the classification results to a list of floats
    toxicity_scores = [
        1.0 if label == "correct" else 0.0
        for label in classification_results["label"].tolist()  # type: ignore[fixme]
    ]

    return toxicity_scores


def calculate_summarization_score(
    outputs: Sequence[str],
    ground_truth: Sequence[str],
    model_name: str = "gpt-3.5-turbo",
) -> list[float]:
    """
    Args:
        inputs (Sequence[str]): A sequence of input strings to be evaluated.
        ground_truth (Sequence[str]): A sequence of reference strings to evaluate the inputs against.

    Returns:
        List[float]: A list of float scores indicating the summary quality of each input-reference pair,
                     where 1.0 denotes 'good' and 0.0 denotes otherwise.
    """
    openai_model = OpenAIModel(
        model=model_name,
        temperature=0.0,
    )

    return _calculate_summarization_score_helper(
        outputs, ground_truth, model_name, openai_model
    )


def _calculate_summarization_score_helper(
    outputs: Sequence[str],
    ground_truth: Sequence[str],
    model_name: str,
    openai_model: OpenAIModel,
):
    if len(outputs) != len(ground_truth):
        raise ValueError(
            f"Number of outputs ({len(outputs)}) and ground_truth ({len(ground_truth)}) must be equal."
        )

    if model_name not in ["gpt-3.5-turbo", "gpt-4"]:
        raise ValueError(
            f"Model name must be one of 'gpt-3.5-turbo' or 'gpt-4'."
        )
    # Create DataFrame
    df = pd.DataFrame({"input": outputs, "output": ground_truth})

    guard_rails = list(SUMMARIZATION_PROMPT_RAILS_MAP.values())

    classification_results = llm_classify(
        df, openai_model, SUMMARIZATION_PROMPT_TEMPLATE, guard_rails
    )

    # Convert the classification results to a list of floats
    relevance_scores = [
        1.0 if label == "good" else 0.0
        for label in classification_results["label"].tolist()  # type: ignore[fixme]
    ]

    return relevance_scores


def calculate_human_vs_ai_score(
    outputs: Sequence[str],
    ground_truth: Sequence[str],
    inputs: Sequence[str],
    model_name: str = "gpt-3.5-turbo",
) -> list[float]:
    """
    Args:
        inputs (Sequence[str]): A sequence of input strings to be evaluated.
        ground_truth (Sequence[str]): A sequence of reference strings to evaluate the inputs against.

    Returns:
        List[float]: A list of float scores indicating the summary quality of each input-reference pair,
                     where 1.0 denotes 'good' and 0.0 denotes otherwise.
    """
    openai_model = OpenAIModel(
        model=model_name,
        temperature=0.0,
    )

    return _calculate_human_vs_ai_score_helper(
        outputs, ground_truth, inputs, model_name, openai_model
    )


def _calculate_human_vs_ai_score_helper(
    outputs: Sequence[str],
    ground_truth: Sequence[str],
    inputs: Sequence[str],
    model_name: str,
    openai_model: OpenAIModel,
):
    if len(outputs) != len(ground_truth):
        raise ValueError(
            f"Number of predictions ({len(outputs)}) and ground_truth ({len(ground_truth)}) must be equal."
        )

    if model_name not in ["gpt-3.5-turbo", "gpt-4"]:
        raise ValueError(
            f"Model name must be one of 'gpt-3.5-turbo' or 'gpt-4'."
        )
    # Create DataFrame
    df = pd.DataFrame(
        {
            "ai_generated_answer": outputs,
            "correct_answer": ground_truth,
            "question": inputs,
        }
    )

    guard_rails = list(HUMAN_VS_AI_PROMPT_RAILS_MAP.values())

    classification_results = llm_classify(
        df, openai_model, HUMAN_VS_AI_PROMPT_TEMPLATE, guard_rails
    )

    # Convert the classification results to a list of floats
    relevance_scores = [
        1.0 if label == "correct" else 0.0
        for label in classification_results["label"].tolist()  # type: ignore[fixme]
    ]

    return relevance_scores


def calculate_custom_llm_metric_example_sentiment(
    outputs: Sequence[str],
    model_name: str = "gpt-3.5-turbo",
) -> list[float]:
    """

    Args:
        outputs (Sequence[str]): The generated texts to evaluate.
        model_name (str): The name of the evaluation model to use.

    Returns:
        list[float]: A list of custom sentiment scores for each text.
    """

    prompt_template = dedent(
        """
        How happy is the following text on a scale of 0 to 1?
        {text_to_evaluate}
        """
    )

    input_names = ["text_to_evaluate"]
    scorer = make_llm_score_function(prompt_template, model_name, input_names)
    return scorer(outputs)


def calculate_custom_llm_metric_example_semantic_similarity(
    outputs: Sequence[str],
    ground_truth: Sequence[str],
    model_name: str = "gpt-3.5-turbo",
) -> list[float]:
    """

    Args:
        outputs (Sequence[str]): The generated texts to evaluate.
        ground_truth (Sequence[str]): The reference texts to evaluate against.
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
    scorer = make_llm_score_function(prompt_template, model_name, input_names)
    return scorer(outputs, ground_truth)
