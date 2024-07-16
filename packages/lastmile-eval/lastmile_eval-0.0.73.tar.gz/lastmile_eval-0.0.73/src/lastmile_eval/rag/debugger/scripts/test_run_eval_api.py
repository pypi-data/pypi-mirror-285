# ignore all type errors

import logging

from lastmile_eval.text.metrics import calculate_exact_match_score

numba_logger = logging.getLogger("numba")
numba_logger.setLevel(logging.WARNING)

from evaluate import EvaluationModule, load  # type: ignore[fixme]

import json

import pandas as pd

from lastmile_eval.rag.debugger.api import evaluation

project_id = "clv4clhdv009wqpl2xy6febdc"
evaluation_test_set_id = "clv4cnhek004yqyy92wsl320s"

import string

import numpy as np


def test_pytest_1():
    queries = [
        "what color is the quick fox?",
        "how many legs does a cat have?",
        "what is the capital of France?",
        "what is the capital of Germany?",
        "who is the president of the United States?",
    ]

    ground_truth = [
        complex_alter_string(q, seed=i) for i, q in enumerate(queries)
    ]

    print(f"{queries=}", f"{ground_truth=}")

    def _rag_query_fn(input: str) -> str:
        print(f"running {input=}")
        max_int = 2**31 - 1
        return complex_alter_string(input, seed=max_int)

    outputs = [_rag_query_fn(q) for q in queries]
    print(f"{outputs=}")

    def _bleu_wrapper(outputs, gt, queries):
        a = np.array(calculate_bleu_score(outputs, gt)) + 0.1
        return a.tolist()

    name = complex_alter_string(
        "Test Evaluation Set", seed=np.random.randint(2**31 - 1)
    )

    eval_res = evaluation.run_and_evaluate_outputs(
        project_id=project_id,
        trace_level_evaluators={
            "bleu": _bleu_wrapper,
        },
        rag_query_fn=_rag_query_fn,
        dataset_level_evaluators={},
        inputs=queries,
        ground_truth=ground_truth,
        lastmile_api_token=token_ankush,
        evaluation_set_name=name,
        n_trials=1,
    )
    print(f"{eval_res=}")
    df_metrics_agg = eval_res.df_metrics_dataset
    print(f"{df_metrics_agg=}")
    bleu_mean = (
        df_metrics_agg.set_index(["testSetId", "metricName"])
        .value.unstack("metricName")["bleu_mean"]
        .iloc[0]
    )
    print(f"{bleu_mean=}")
    # print(f"{eval_res=}")

    evaluation.assert_is_close(eval_res, "bleu_mean", 0.16311969)
    evaluation.assert_is_close(eval_res, "bleu_mean", 0.1)


def main():
    # test1()
    # test2()
    test3()
    # outputs = ["xA?what collor is the quick fo"]
    # gt = ["lr is the  quick fox?what co"]
    # bleu = calculate_bleu_score(outputs, gt)
    # print(f"{bleu=}")


def complex_alter_string(s: str, seed=1) -> str:
    # Define set of functions to apply
    def add_char(s, rng):
        idx = rng.integers(0, high=len(s) + 1)
        random_char = rng.choice(list(string.ascii_letters))
        return s[:idx] + random_char + s[idx:]

    def remove_char(s, rng):
        if len(s) > 0:
            idx = rng.integers(len(s))
            return s[:idx] + s[(idx + 1) :]
        else:
            return s

    def rotate(s, rng):
        if len(s) > 0:
            idx = rng.integers(len(s))
            return s[idx:] + s[:idx]
        else:
            return s

    def change_case(s, rng):
        idx = rng.integers(len(s))
        s_list = list(s)
        s_list[idx] = s_list[idx].swapcase()
        return "".join(s_list)

    def double_char(s, rng):
        if len(s) > 0:
            idx = rng.integers(len(s))
            return s[:idx] + s[idx] * 2 + s[idx + 1 :]
        else:
            return s

    # List of transformations
    transformations = [add_char, remove_char, rotate, change_case, double_char]

    # Create numpy random generator
    rng = np.random.default_rng(seed)

    # Determine number of transformations based on string length
    if len(s) < 10:
        n_transformations = 1
    elif 10 <= len(s) < 20:
        n_transformations = 2
    else:
        n_transformations = 3

    # Apply a random transformation n times
    for _ in range(n_transformations):
        transformation = rng.choice(transformations)
        s = transformation(s, rng)

    return s


def test3():
    queries = [
        "what color is the quick fox?",
        # "how many legs does a cat have?",
        # "what is the capital of France?",
        # "what is the capital of Germany?",
        # "who is the president of the United States?",
    ]

    ground_truth = [
        complex_alter_string(q, seed=i) for i, q in enumerate(queries)
    ]

    print(f"{queries=}", f"{ground_truth=}")

    def _rag_query_fn(input: str) -> str:
        print(f"running {input=}")
        max_int = 2**31 - 1
        return complex_alter_string(input, seed=max_int)

    outputs = [_rag_query_fn(q) for q in queries]
    print(f"{outputs=}")

    name = complex_alter_string(
        "Test Evaluation Set", seed=np.random.randint(2**31 - 1)
    )

    metric_names = {
        "exact_match",
        "bleu",
        "rouge1",
        "relevance",
        "toxicity",
        "qa",
        "summarization",
        "human_vs_ai",
        "sentiment",
        "similarity",
        # "faithfulness",
    }

    eval_res = evaluation.run_and_evaluate_outputs(
        project_id=project_id,
        trace_level_evaluators=evaluation.get_default_rag_trace_level_metrics(
            metric_names, token_ankush
        ),
        rag_query_fn=_rag_query_fn,
        dataset_level_evaluators={},
        inputs=queries,
        ground_truth=ground_truth,
        lastmile_api_token=token_ankush,
        evaluation_set_name=name,
        n_trials=1,
    )

    print(f"{eval_res=}")


def test2():
    # project_id = "clv4clhdv009wqpl2xy6febdc"
    project_name = "Test"

    token = token_rd

    dfrqt = evaluation.get_traces(
        lastmile_api_token=token, project_name=project_name
    )

    dfrqt["input"] = [{"input": "what color is the quick fox?"}] * len(dfrqt)

    print("DFRQT")
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    print(
        dfrqt[
            [
                "ragQueryTraceId",
                "paramSet",
                "input",
                "output",
                "ragIngestionTraceId",
                "ragIngestionTrace",
            ]
        ]
    )

    create_res = evaluation.create_test_set_from_rag_query_traces(
        dfrqt,
        "Test Evaluation Set",
        lastmile_api_token=token,
        ground_truth=["xyz"] * len(dfrqt),
    )

    print(f"{create_res=}")

    downloaded = evaluation.download_test_set(
        create_res.ids[0],
        lastmile_api_token=token,
    )

    print(
        "Just created + downloaded:\n",
        json.dumps(downloaded.to_dict("records"), indent=2),
    )


def test1():
    token = prod_token
    # def pdoptions(r=2, c=20, w=50):
    #     pd.set_option("display.max_rows", r)
    #     pd.set_option("display.max_columns", c)
    #     pd.set_option("display.max_colwidth", w)

    dfts = evaluation.download_test_set(evaluation_test_set_id, prod_token)
    # pdoptions(r=None)
    print("DFTS")
    print(dfts.T)

    def eval1(df_test_cases):
        # print(f"eval1: {df_test_cases.T}")
        return (
            df_test_cases.apply(lambda r: r.groundTruth in r.output, axis=1)
            .to_frame("substr")
            .astype(float)
            .substr
        )

    trace_level_evaluators = {
        "substr": eval1,
    }
    dataset_level_evaluators = {}

    dfe_t, dfe_d = evaluation.run_evaluations(
        dfts,
        trace_level_evaluators=trace_level_evaluators,
        dataset_level_evaluators=dataset_level_evaluators,
    )

    print("DFE_T")
    print(dfe_t)
    print("DFE_D")
    print(dfe_d)

    upload_result = evaluation.store_evaluation_set_results(
        project_id, dfe_t, dfe_d, token_rd
    )
    print(f"Upload result:\n{upload_result}")

    result2 = evaluation.run_and_store_evaluations(
        evaluation_test_set_id,
        project_id,
        trace_level_evaluators,
        dataset_level_evaluators,
        token,
        evaluation_set_name="Test Evaluation Set",
    )

    print(f"Result2: {result2}")


if __name__ == "__main__":
    main()
