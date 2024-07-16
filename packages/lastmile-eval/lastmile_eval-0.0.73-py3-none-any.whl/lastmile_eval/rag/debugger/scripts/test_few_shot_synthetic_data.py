from typing import Sequence
import pandas as pd
from lastmile_eval.text.synthetic_data.few_shot import (
    synthesize_helper,
    synthesize_questions_from_contexts,
)


def main():
    # run_example_1()
    run_example_2()


def run_example_1():
    labeled_questions = ["What color is the sky?", "What color is the ocean?"]

    labeled_contexts = [
        "The sky is blue",
        "The sky is blue",
    ]

    answers = [
        "Blue",
        "I don't know",
    ]

    unlabeled_questions = [
        "Is it cloudy right now?",
        "What is the capital of France?",
    ]

    unlabeled_contexts = [
        "It's cloudy right now",
        "The capital of Australia is Canberra",
    ]

    synthetic_answers = generate_synthetic_answers(
        labeled_questions,
        labeled_contexts,
        answers,
        unlabeled_questions,
        unlabeled_contexts,
    )

    print("Labeled input data:")
    df_labeled = pd.DataFrame(
        {
            "Question": labeled_questions,
            "Context": labeled_contexts,
            "Answer": answers,
        }
    )

    print(df_labeled)

    df_synthesized = pd.DataFrame(
        {
            "Input Question": unlabeled_questions,
            "Input Context": unlabeled_contexts,
            "Synthesized Answer": synthetic_answers,
        }
    )

    print("\n\nExample synthetic data:")
    print(df_synthesized)


def run_example_2():
    pd.set_option("display.max_colwidth", None)

    # Step 1: Prepare unlabeled query, context data from RAG Query Traces
    PATH_DF_ALL_RQT = (
        "/Users/jonathan/Projects/experimentation/slackbot/df_all_rqt.xlsx"
    )

    df_all_rqt = pd.read_excel(PATH_DF_ALL_RQT)

    df_qc_unlabeled = (
        df_all_rqt.explode("context_extracted")[
            ["query_extracted", "context_extracted"]
        ]
        .dropna()
        .drop_duplicates()
    )

    # Step 2: Prepare any available labeled query, context positive pairs

    PATH_QC_POSITIVES = (
        "/Users/jonathan/Projects/experimentation/slackbot/qc_positives.xlsx"
    )
    df_cq_positives = pd.read_excel(PATH_QC_POSITIVES)

    print("Labeled positive query, context pairs:")
    print(df_cq_positives)

    # Step 3: set the number of synthetic (query, context) pairs to generate

    n_synthetic_questions = 1

    # Step 4: Extract the individual contexts from the traces.
    # These will be the unlabeled observed inputs used to generate
    # synthetic questions.
    observed_contexts = df_qc_unlabeled["context_extracted"].tolist()

    print("\n\nObserved contexts:")
    print(observed_contexts)

    # Step 5: Generate synthetic questions from the observed contexts
    df_synthetic_question_pairs = synthesize_questions_from_contexts(
        df_cq_positives["context"],
        df_cq_positives["question"],
        observed_contexts,
        n_synthetic_questions,
    )

    print("\n\nSynthetic question pairs:")

    # pd.set_option("display.max_colwidth", None)
    print(df_synthetic_question_pairs.question.values[0])
    print(df_synthetic_question_pairs.context.values[0])


# Example wrapper
def generate_synthetic_answers(
    labeled_questions: Sequence[str],
    labeled_contexts: Sequence[str],
    answers: Sequence[str],
    unlabeled_questions: Sequence[str],
    unlabeled_contexts: Sequence[str],
    openai_model_name: str = "gpt-4",
):
    df = pd.DataFrame(
        {
            "Question": labeled_questions,
            "Context": labeled_contexts,
            "Answer": answers,
        }
    )

    df_observed = pd.DataFrame(
        {"Question": unlabeled_questions, "Context": unlabeled_contexts}
    )

    return synthesize_helper(df, df_observed, "Answer", openai_model_name)


if __name__ == "__main__":
    main()
