from typing import Sequence
import numpy as np
from openai import OpenAI
import pandas as pd

# API V0


def synthesize_questions_from_contexts(
    labeled_contexts: Sequence[str],
    questions: Sequence[str],
    unlabeled_contexts: Sequence[str],
    n_synthetic_questions: int,
    openai_model_name: str = "gpt-4",
):
    """
    Sample from unlabeled contexts and generate relevant synthetic questions.

    During generation, follows your (labeled_context, question) positive pairs
    in few-shot fashion.

    Tested with GPT4 8k context window (default).
    If unsure, try the default value.

    IN:

    labeled_contexts and questions are positive pairs from your corpus.
    unlabeled_contexts are contexts from your corpus for which you want to generate
    synthetic questions.

    n_synthetic_questions: Number of synthetic questions to generate.

    OUT: DataFrame with columns "question" and "context", containing sampled
    observed contexts and corresponding synthetic questions.
    """
    df_cq_positives = pd.DataFrame(
        {"context": labeled_contexts, "question": questions}
    )
    s_observed_contexts = pd.Series(unlabeled_contexts)

    # Sample from the input context so it fits in the 8192 token limit.
    # Larger context window models seem to work worse.
    def _shrink_text(text, output_len):
        full_len = len(text)
        largest_start_idx = max(0, full_len - output_len)
        random_start_idx = np.random.randint(0, 1 + largest_start_idx)
        return text[random_start_idx : random_start_idx + output_len]

    # This is in characters, not tokens. Used to make completion calls succeed
    # by keeping the input text within the 8192 token limit.
    output_len = 10000

    df_cq_positives = df_cq_positives.assign(
        context=df_cq_positives["context"].apply(
            lambda c: _shrink_text(c, output_len)
        ),
    )
    s_observed_contexts = s_observed_contexts.apply(
        lambda c: _shrink_text(c, output_len)
    )

    dfs = []
    for _ in range(n_synthetic_questions):
        # It seems to work better with just a single labeled pair at a time.
        df_cq_labeled = df_cq_positives.sample(1)

        df_observed = s_observed_contexts.to_frame("context")

        # It seems to work better with just a single context at a time.
        df_observed = df_observed.sample(1)

        df_new_pair = _make_synthetic_qc_pair(
            df_cq_labeled, df_observed, openai_model_name
        )

        dfs.append(df_new_pair)

    df_synthetic_question_pairs = pd.concat(dfs)
    return df_synthetic_question_pairs


def _make_synthetic_qc_pair(df_cq_labeled, df_observed, openai_model_name):
    synthetic_question = synthesize_helper(
        df_cq_labeled, df_observed, "question", openai_model_name
    )

    df_new_pair = df_observed.assign(question=synthetic_question)[
        ["question", "context"]
    ]

    return df_new_pair


def synthesize_one_from_full_user_message(
    user_message: str, openai_model_name: str
) -> str:
    client = OpenAI()
    response = client.chat.completions.create(
        model=openai_model_name,
        messages=[
            {
                "role": "system",
                "content": """
                    You will see some example text combinations, and will be asked
                    to output a prediction for a new example.
                    Example input:
                        
                        Question: What color is the sky?
                        Answer: Blue

                        New example: 
                        Question: What is the capital of France?
                        Answer: 

                    Expected output:
                            
                            Paris
                """,
            },
            {"role": "user", "content": user_message},
        ],
    )

    return response.choices[0].message.content


def synthesize_one_helper(
    df_labeled_examples, record_observed, column_to_predict, openai_model_name
):
    """
    Example input:
    df_labeled_examples: | Question | Answer |
                         |----------|--------|
                         | What is the capital of France? | Paris |
                         | What color is the sky? | Blue |

    record_observed: {"Answer": "Yellow}

    Example output: "What color is a banana?
    """

    columns = set(df_labeled_examples.columns)
    observed_columns = set(record_observed.keys())
    if observed_columns | {column_to_predict} != columns:
        raise ValueError(
            "union of observed and columns to predict must be the same"
            "as the columns in the labeled examples"
        )

    if len(observed_columns & {column_to_predict}) > 0:
        raise ValueError(
            "observed columns and column to predict must be disjoint"
        )

    def _few_shot_example(row: pd.Series):
        out = ""
        for k, v in row.items():
            out += "\t" + str(k) + ": " + str(v) + "\n"

        return out

    few_shot_str = "\n".join(
        df_labeled_examples.apply(_few_shot_example, axis=1)
    )

    observed_str = "\n".join(f"{k}: {v}" for k, v in record_observed.items())

    user_message = f"""
        {few_shot_str}
        
        New example:
        {observed_str}
        {column_to_predict}:
    """

    return synthesize_one_from_full_user_message(
        user_message, openai_model_name
    )


def synthesize_helper(
    df_labeled_examples, df_observed, column_to_predict, openai_model_name
):
    return [
        synthesize_one_helper(
            df_labeled_examples, record, column_to_predict, openai_model_name
        )
        for record in df_observed.to_dict(orient="records")
    ]
