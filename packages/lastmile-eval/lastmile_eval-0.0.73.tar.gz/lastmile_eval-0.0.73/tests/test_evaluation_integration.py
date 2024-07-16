"""
TODO: mock out the web endpoint so key is not needed to test.
"""

from functools import partial
import json
import logging
import os
import random
from types import NoneType
from typing import Optional, cast

import lastmile_utils.lib.core.api as core_utils
import pandas as pd
from lastmile_eval.rag.debugger.common.utils import load_dotenv_from_cwd

from lastmile_eval.rag.debugger.common.general_functional_utils import (
    do_list,
    exn_to_err,
)
from lastmile_eval.rag.debugger.offline_evaluation import (
    evaluation_lib as e_lib,
)
from lastmile_eval.rag.debugger.api import evaluation as e
from lastmile_eval.rag.debugger.common import core as core

from lastmile_eval.rag.debugger.common.types import (
    BaseURL,
    Res,
)

from lastmile_eval.rag.debugger.tracing import (
    get_lastmile_tracer,
    get_trace,
)

TEST_WEBSITE_BASE_URL = "https://lastmileai.dev"
N_DEFAULT_AGGREGATES = 1
N_EXPECTED_COLUMNS_EVALS_TRACE = 4
N_EXPECTED_COLUMNS_EVALS_DATASET = 3

logger = logging.getLogger(__name__)
logging.basicConfig(format=core_utils.LOGGER_FMT, level=logging.INFO)


load_dotenv_from_cwd()
token = os.getenv("LASTMILE_API_TOKEN")
assert token is not None, "Token not found"


def pdoptions(
    r: Optional[int] = 2,
    c: Optional[int] = 20,
    w: Optional[int] = 50,
    dw: Optional[int] = 50,
):
    pd.set_option("display.max_rows", r)
    pd.set_option("display.max_columns", c)
    pd.set_option("display.max_colwidth", w)
    pd.set_option("display.width", dw)


def abs_path(rel_path: str) -> str:
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, rel_path)


# Just for manual testing.
def _lookup_test_dataset_ids_by_name(name: str) -> list[core.ExampleSetID]:  # type: ignore
    return e_lib._get_example_set_ids_by_name(  # type: ignore
        BaseURL(TEST_WEBSITE_BASE_URL),
        name,
        None,  # project_name
        os.getenv("LASTMILE_API_TOKEN"),  # type: ignore
    ).unwrap_or_raise(ValueError)


@exn_to_err
def _get_trace(trace_id: core.OTelTraceID) -> core.JSONObject:
    return get_trace(trace_id)


def assert_evaluation_values(
    resp: e_lib.EvaluationResult,
    example_level_records: Optional[list[tuple[str, float | str]]] = None,
    aggregated_records: Optional[list[tuple[str, float | str]]] = None,
):
    df_metrics_aggregated = resp.aggregated_metrics
    assert len(set(df_metrics_aggregated.exampleSetId)) == 1  # type: ignore

    if example_level_records is not None:
        trace_metrics = resp.evaluator_metrics_df[["metricName", "value"]].fillna("None").to_records(index=False).tolist()  # type: ignore

        # TODO: this should be a bag check, not set
        assert set(trace_metrics) == set(example_level_records)  # type: ignore

    if aggregated_records is not None:
        df_metrics_aggregated = resp.aggregated_metrics
        dataset_metrics = df_metrics_aggregated[["metricName", "value"]].fillna("None").to_records(index=False).tolist()  # type: ignore

        # TODO: this should be a bag check, not set
        assert set(dataset_metrics) == set(aggregated_records)  # type: ignore


def assert_df_conditions(
    df: pd.DataFrame,
    cols_contain: Optional[set[str]] = None,
    rows: Optional[int] = None,
    cols: Optional[int] = None,
    nulls_axis0: Optional[list[int]] = None,
    nulls_axis1: Optional[list[int]] = None,
):
    if cols_contain is not None:
        diff = cols_contain - set(df.columns)
        assert (
            set(df.columns) >= cols_contain
        ), f"Missing columns: {diff}, Existing columns: {set(df.columns)}"
    if rows is not None:
        assert df.shape[0] == rows

    if cols is not None:
        assert df.shape[1] == cols

    if nulls_axis0 is not None:
        got_nulls_0 = df.isnull().astype(int).sum(axis=0).tolist()  # type: ignore[pandas]
        assert (
            got_nulls_0 == nulls_axis0
        ), f"Expected nulls_axis0: {nulls_axis0}, got {got_nulls_0}"
    if nulls_axis1 is not None:
        got_nulls1 = df.isnull().astype(int).sum(axis=1).tolist()  # type: ignore[pandas]
        assert (
            got_nulls1 == nulls_axis1
        ), f"Expected nulls_axis1: {nulls_axis1}, got {got_nulls1}"


def _assert_evaluation_response_helper(
    resp: e_lib.EvaluationResult,
    df_trace_shape: tuple[int, int],
    df_dataset_shape: tuple[int, int],
    evaluation_result_id: type[str | None],
):
    assert evaluation_result_id is NoneType or isinstance(
        resp.evaluation_result_id, str
    )
    assert isinstance(resp.test_dataset_id, str)

    # At least one example row provided
    assert (
        df_trace_shape[0] != 0
    ), f"{df_trace_shape=}, {resp.evaluator_metrics_df=}"

    # (1 or more rows expected) -> (df is not None and rows eq)
    # (df is not None and rows eq)
    assert (
        df_trace_shape == resp.evaluator_metrics_df.shape
    ), f"{df_trace_shape=}, {resp.evaluator_metrics_df=}"

    assert (
        resp.aggregated_metrics is not None
        and df_dataset_shape == resp.aggregated_metrics.shape
    ) or (
        df_dataset_shape[0] == 0
    ), f"{df_dataset_shape=}, {resp.aggregated_metrics=}"


def assert_evaluation_response(
    resp: e_lib.EvaluationResult,
    n_inputs: int,
    n_evaluators: int,
    n_datasets: int = 1,
    n_trials: int = 1,
    expected_columns_evals_trace: int = N_EXPECTED_COLUMNS_EVALS_TRACE,
    expected_columns_evals_dataset: int = N_EXPECTED_COLUMNS_EVALS_DATASET,
    n_aggregated_evaluators: Optional[int] = None,
    evaluation_result_id: type[str | None] = str,
):
    n_aggregated_evaluators = (
        n_aggregated_evaluators or n_evaluators * N_DEFAULT_AGGREGATES
    )
    _assert_evaluation_response_helper(
        resp,
        (n_trials * n_inputs * n_evaluators, expected_columns_evals_trace),
        (n_datasets * n_aggregated_evaluators, expected_columns_evals_dataset),
        evaluation_result_id,
    )


# TODO (rossdan): Enable this test once pkl files are updated and we
# actually set up test data
# def test_evaluate_with_traces_general_case():
#     df_traces = _pickle_to_df("test_evaluate_with_traces_general_case.pkl")

#     # # TestSet does not allow this key, so ExampleSet must reject it.
#     # # Passing llmOutput would be a user error
#     # # (unless we automatically convert it to output which is probably a bad idea.)
#     # # We can use the allowed `output` key instead.
#     # df_traces = df_traces.rename(columns={"output": "output"})

#     def _my_funny_exact_match(df: pd.DataFrame) -> list[float]:
#         def _my_funny_exact_match_row(row: pd.Series) -> float:  # type: ignore
#             return float(row["input"] == row["output"])  # type: ignore

#         return df.apply(_my_funny_exact_match_row, axis=1).tolist()  # type: ignore

#     evaluators = {"my_exact_match": _my_funny_exact_match}

#     resp = e.evaluate(
#         project_name=None,
#         test_dataset=df_traces,
#         evaluators=evaluators,
#         save_options=e.SaveOptions(
#             name="Example set test30.1",
#         ),
#     )

#     assert_evaluation_response(resp, len(df_traces), len(evaluators))
#     assert_evaluation_values(
#         resp,
#         [("my_exact_match", 0.0), ("my_exact_match", 0.0)],
#         [
#             ("my_exact_match_mean", 0.0),
#         ],
#     )


def test_evaluation_save_options_combinations():
    evaluators = {"exact_match"}

    queries = ["x", "y"]
    resp = e.evaluate(
        project_name=None,
        test_dataset=pd.DataFrame(
            {
                "input": queries,
                "groundTruth": [
                    "xgt",
                    "ygt",
                ],
            }
        ),
        evaluators=evaluators,
        save_options=e.SaveOptions(
            name="Evaluation Set 29.1",
        ),
    )

    assert_evaluation_response(resp, len(queries), len(evaluators))
    assert_evaluation_values(
        resp,
        [("exact_match", 0.0), ("exact_match", 0.0)],
        [
            ("exact_match_mean", 0.0),
        ],
    )

    def run_fn(query: str) -> str:
        return f"This is the output. The query was: {query}"

    queries = [
        "x",
        "y",
    ]

    resp = e.run_and_evaluate(
        project_name=None,
        run_fn=run_fn,
        inputs=queries,
        ground_truths=[
            "xgt",
            "ygt",
        ],
        evaluators=evaluators,
        # Rewrite with same name as one previously defined
        save_options=e.SaveOptions(
            name="Evaluation Set 29.1",
        ),
    )

    assert_evaluation_response(resp, len(queries), len(evaluators))
    assert_evaluation_values(
        resp,
        [("exact_match", 0.0), ("exact_match", 0.0)],
        [
            ("exact_match_mean", 0.0),
        ],
    )

    queries = [
        "x",
        "y",
    ]

    resp = e.evaluate(
        project_name=None,
        test_dataset=pd.DataFrame(
            {
                "input": queries,
                "groundTruth": [
                    "xgt",
                    "ygt",
                ],
            }
        ),
        evaluators=evaluators,
        save_options=e.SaveOptions(
            name="Evaluation Set 29.2",
        ),
    )

    assert_evaluation_response(resp, len(queries), len(evaluators))

    assert_evaluation_values(
        resp,
        [("exact_match", 0.0), ("exact_match", 0.0)],
        [
            ("exact_match_mean", 0.0),
        ],
    )

    queries = [
        "x",
        "y",
    ]

    resp = e.run_and_evaluate(
        project_name=None,
        run_fn=run_fn,
        inputs=queries,
        ground_truths=[
            "xgt",
            "ygt",
        ],
        evaluators=evaluators,
        save_options=e.SaveOptions(
            name="Evaluation Set 29.3",
        ),
    )

    assert_evaluation_response(resp, len(queries), len(evaluators))
    assert_evaluation_values(
        resp,
        [("exact_match", 0.0), ("exact_match", 0.0)],
        [
            ("exact_match_mean", 0.0),
        ],
    )


def test_run_and_evaluate_general_case_with_default_evaluators():
    def run_fn(query: str) -> str:
        return f"This is the output. The query was: {query}"

    evaluators = {
        # unary
        "toxicity",
        "sentiment",
        # binary - GT
        "bleu",
        "rouge1",
        "similarity",
        "exact_match",
        # binary - input
        "relevance",
        # ternary
        "qa",
        "human_vs_ai",
    }

    queries = ["x", "z"]

    resp = e.run_and_evaluate(
        project_name=None,
        run_fn=run_fn,
        inputs=queries,
        ground_truths=["x", "W"],
        evaluators=evaluators,
    )

    assert_evaluation_response(resp, len(queries), len(evaluators))

    trace_metrics_names = resp.evaluator_metrics_df[["metricName"]].fillna("None").to_records(index=False).tolist()  # type: ignore

    # TODO: this should be a bag check, not set
    assert set(trace_metrics_names) == {  # type: ignore
        ("relevance",),
        ("sentiment",),
        ("exact_match",),
        ("bleu",),
        ("toxicity",),
        ("similarity",),
        ("rouge1",),
        ("human_vs_ai",),
        ("qa",),
    }
    trace_metrics_values = resp.evaluator_metrics_df["value"]  # type: ignore[pandas]
    assert ((0 <= trace_metrics_values) & (trace_metrics_values <= float("inf"))).all(), f"{trace_metrics_values=}"  # type: ignore[pandas]

    df_metrics_aggregated = resp.aggregated_metrics

    assert len(set(df_metrics_aggregated.exampleSetId)) == 1  # type: ignore
    dataset_metrics_names = df_metrics_aggregated[["metricName"]].fillna("None").to_records(index=False).tolist()  # type: ignore

    # TODO: this should be a bag check, not set
    assert set(dataset_metrics_names) == {  # type: ignore
        ("sentiment_mean",),
        ("toxicity_mean",),
        ("qa_mean",),
        ("bleu_mean",),
        ("rouge1_mean",),
        ("relevance_mean",),
        ("similarity_mean",),
        ("exact_match_mean",),
        ("human_vs_ai_mean",),
    }

    df_metrics_aggregated = resp.aggregated_metrics
    dataset_metrics_values = df_metrics_aggregated["value"]  # type: ignore[pandas]
    assert ((0 <= dataset_metrics_values) & (dataset_metrics_values <= float("inf"))).all(), f"{dataset_metrics_values=}"  # type: ignore[pandas]


def test_run_and_evaluate_2_trials():
    def run_fn(query: str) -> str:
        return f"This is the output. The query was: {query}"

    evaluators = {"exact_match"}

    resp = e.run_and_evaluate(
        project_name=None,
        run_fn=run_fn,
        test_dataset_id="clwoenwjo0039qymx70nk09k6",
        evaluators=evaluators,
        n_trials=2,
    )
    assert_evaluation_response(resp, 2, len(evaluators), n_trials=2)

    assert_evaluation_values(
        resp,
        [("exact_match", 0.0), ("exact_match", 0.0)],
        [
            ("exact_match_mean", 0.0),
        ],
    )


def test_run_and_evaluate_with_test_dataset_id():
    def run_fn(query: str) -> str:
        return f"This is the output. The query was: {query}"

    evaluators = {"exact_match"}

    resp = e.run_and_evaluate(
        project_name=None,
        run_fn=run_fn,
        test_dataset_id="clwoenwjo0039qymx70nk09k6",
        evaluators=evaluators,
    )

    assert_evaluation_response(resp, 2, len(evaluators))

    assert_evaluation_values(
        resp,
        [("exact_match", 0.0), ("exact_match", 0.0)],
        [
            ("exact_match_mean", 0.0),
        ],
    )


def _extract_function_output_from_trace_data(
    trace_data: core_utils.JSONObject,
) -> Res[str]:
    try:
        outputs_found: list[str] = []
        for data_elt in trace_data["data"]:  # type: ignore
            spans = data_elt["spans"]  # type: ignore
            for span in spans:  # type: ignore
                for tag in span["tags"]:  # type: ignore
                    if tag["key"] == "output":  # type: ignore
                        if tag.get("type", None) != "string":  # type: ignore
                            return core.Err(
                                ValueError("Expected tag output type string")
                            )
                        outputs_found.append(tag["value"])  # type: ignore

        if len(outputs_found) == 0:
            return core.Err(ValueError("No output found in trace data"))
        if len(outputs_found) > 1:
            return core.Err(ValueError("Multiple outputs found in trace data"))
        else:
            return core.Ok(outputs_found[0])
    except Exception as exn:
        return core.Err(exn)


def test_run_and_evaluate_with_in_memory_inputs():
    tracer = get_lastmile_tracer("user-tracer")

    @tracer.trace_function()
    def run_fn(query: str) -> str:
        return f"This is the output. The query was: {query}"

    evaluators = {"exact_match"}

    resp = e.run_and_evaluate(
        project_name=None,
        run_fn=run_fn,
        inputs=["x", "y"],
        ground_truths=["xgt", "ygt"],
        evaluators=evaluators,
    )

    assert_evaluation_response(resp, 2, len(evaluators))

    assert_evaluation_values(
        resp,
        [("exact_match", 0.0), ("exact_match", 0.0)],
        [
            ("exact_match_mean", 0.0),
        ],
    )

    # Check all the linking business
    df_example_set = e.get_test_dataset(test_set_id=resp.test_dataset_id)
    rag_query_traces = df_example_set["ragQueryTrace"].tolist()  # type: ignore[pandas]

    rag_query_traces: list[core_utils.JSONObject] = cast(
        list[core_utils.JSONObject], rag_query_traces
    )  # type: ignore

    assert len(rag_query_traces) > 0 and "traceId" in rag_query_traces[0]
    trace_ids: list[core.OTelTraceID] = [elt["traceId"] for elt in rag_query_traces]  # type: ignore[intentional]
    trace_data = do_list(_get_trace, trace_ids)
    trace_data = trace_data.and_then(
        partial(do_list, _extract_function_output_from_trace_data)
    )

    assert trace_data.is_ok()
    trace_data_ok: list[str] = trace_data.ok_value  # type: ignore
    assert trace_data_ok == ['"This is the output. The query was: x"', '"This is the output. The query was: y"']  # type: ignore


def test_run_and_evaluate_bad_missing_queries():
    def run_fn(query: str) -> str:
        return f"This is the output. The query was: {query}"

    evaluators = {"exact_match"}
    try:
        resp = e.run_and_evaluate(
            project_name=None,
            run_fn=run_fn,
            ground_truths=["xgt", "ygt"],
            evaluators=evaluators,
        )

        assert False, f"Expected ValueError, got {resp}"

    except ValueError as exn:
        expected = "ground_truths given but no input queries given"
        assert expected in str(exn), f"{str(exn)=}"


def test_run_and_evaluate_bad_ground_truth_missing_queries():
    def run_fn(query: str) -> str:
        return f"This is the output. The query was: {query}"

    evaluators = {"exact_match"}

    try:
        resp = e.run_and_evaluate(
            project_name=None,
            run_fn=run_fn,
            test_dataset_id="clwoenwjo0039qymx70nk09k6",
            ground_truths=["xgt", "ygt"],
            evaluators=evaluators,
        )

        assert False, f"Expected ValueError, got {resp}"
    except ValueError as exn:
        expected = "ground_truths given but no input queries given"
        assert expected in str(exn), f"{str(exn)=}"


def test_run_and_evaluate_bad_duplicate_args():
    def run_fn(query: str) -> str:
        return f"This is the output. The query was: {query}"

    evaluators = {"exact_match"}

    try:
        resp = e.run_and_evaluate(
            project_name=None,
            run_fn=run_fn,
            test_dataset_id="clwoenwjo0039qymx70nk09k6",
            inputs=["x", "y"],
            ground_truths=["xgt", "ygt"],
            evaluators=evaluators,
        )

        assert False, f"Expected ValueError, got {resp}"
    except ValueError as exn:
        expected = "Exactly one of (test_dataset_id, inputs) must be provided."
        assert expected in str(exn), f"{str(exn)=}"


def test_evaluate_with_evaluator_names():
    evaluators = {"exact_match"}

    queries = ["x", "y"]

    resp = e.evaluate(
        project_name=None,
        test_dataset=pd.DataFrame(
            {"input": queries, "groundTruth": ["xgt", "ygt"]}
        ),
        evaluators=evaluators,
    )

    assert_evaluation_response(resp, len(queries), len(evaluators))

    assert_evaluation_values(
        resp,
        [("exact_match", 0.0), ("exact_match", 0.0)],
        [
            ("exact_match_mean", 0.0),
        ],
    )


def test_evaluate_with_save_options():
    evaluators = {"exact_match"}

    queries = ["x", "y"]

    resp = e.evaluate(
        project_name=None,
        test_dataset=pd.DataFrame(
            {"input": queries, "groundTruth": ["xgt", "ygt"]}
        ),
        evaluators=evaluators,
        save_options=e.SaveOptions(
            name="Evaluation Set 19",
        ),
    )

    assert_evaluation_response(resp, len(queries), len(evaluators))

    assert_evaluation_values(
        resp,
        [("exact_match", 0.0), ("exact_match", 0.0)],
        [
            ("exact_match_mean", 0.0),
        ],
    )


# TODO (rossdan): Enable this test again when adding Aggregator next PR
def test_evaluate_with_custom_exact_match_agg():
    def my_agg_evaluator(df_example_level_metrics: pd.DataFrame) -> float:
        return (
            df_example_level_metrics.apply(  # type: ignore[pandas]
                lambda r: r["input"] == r["output"],  # type: ignore[pandas]
                axis=1,
            )
            .astype(float)
            .max()
        )

    queries = ["x", "y"]
    evaluators = {
        "my_agg_v0": e_lib.EvaluatorTuple(
            evaluator=lambda _pd: [1.0, 0.0], aggregator=my_agg_evaluator
        )
    }  # type: ignore

    resp = e.evaluate(
        project_name=None,
        test_dataset=pd.DataFrame(
            {"input": queries, "output": ["x", "y_no_match"]}
        ),
        evaluators=evaluators,  # type: ignore
    )

    # # This assertion logic is so fucking hard to figure out wtf is going on and
    # # I'm not going to waste hours more of my time trying to understand it.
    # # Jonathan this is not intuitive at all, you at least need to have comments
    # # and make more intermediate values so people can figure out what's going on
    # assert_evaluation_response(
    #     resp, 0, 1, n_aggregated_evaluators=len(evaluators)
    # )

    assert_evaluation_values(resp, aggregated_records=[("my_agg_v0", 1.0)])


def test_evaluate_with_basic_agg_eval():
    def my_agg_evaluator(_df_example_level_metrics: pd.DataFrame) -> float:
        return 0.0

    evaluators = {
        "my_agg_v0": e_lib.EvaluatorTuple(
            evaluator=lambda _pd: [1.0, 0.0], aggregator=my_agg_evaluator
        )
    }  # type: ignore

    resp = e.evaluate(
        project_name=None,
        test_dataset=pd.DataFrame(
            {"input": ["x", "y"], "groundTruth": ["xgt", "ygt"]}
        ),
        evaluators=evaluators,
    )

    # # This assertion logic is so fucking hard to figure out wtf is going on and
    # # I'm not going to waste hours more of my time trying to understand it.
    # # Jonathan this is not intuitive at all, you at least need to have comments
    # # and make more intermediate values so people can figure out what's going on
    # assert_evaluation_response(
    #     resp, 0, 1, n_aggregated_evaluators=len(evaluators)
    # )

    assert_evaluation_values(
        resp,
        aggregated_records=[("my_agg_v0", 0.0)],
    )


def test_evaluate_with_df_and_ground_truth():
    queries = ["x", "y"]
    evaluators = {"exact_match"}
    resp = e.evaluate(
        project_name=None,
        test_dataset=pd.DataFrame(
            {"input": queries, "groundTruth": ["xgt", "ygt"]}
        ),
        evaluators=evaluators,
    )

    assert_evaluation_response(resp, len(queries), len(evaluators))

    assert_evaluation_values(
        resp,
        [("exact_match", 0.0), ("exact_match", 0.0)],
        [
            ("exact_match_mean", 0.0),
        ],
    )


def test_evaluate_with_bad_df():
    try:
        resp = e.evaluate(
            project_name=None,
            test_dataset=pd.DataFrame({"some_col": ["x", "y"]}),
            evaluators={"exact_match"},
        )

        assert False, f"Expected ValueError, got {resp}"
    except ValueError as exn:
        assert "DataFrame must have a 'input' column" in str(exn)


def test_evaluate_with_df():
    queries = ["x", "y"]
    evaluators = {"exact_match"}
    resp = e.evaluate(
        project_name=None,
        test_dataset=pd.DataFrame({"input": queries}),
        evaluators=evaluators,
    )

    assert_evaluation_response(resp, len(queries), len(evaluators))

    assert_evaluation_values(
        resp,
        [("exact_match", 1.0), ("exact_match", 1.0)],
        [
            ("exact_match_mean", 1.0),
        ],
    )


def test_evaluate_with_test_dataset_id():
    queries = ["x", "y"]
    evaluators = {"exact_match"}
    resp = e.evaluate(
        project_name=None,
        test_dataset_id="clwofniu5002uqprxtz5q4j6m",
        evaluators=evaluators,
    )

    assert_evaluation_response(resp, len(queries), len(evaluators))

    assert_evaluation_values(
        resp,
        [("exact_match", 1.0), ("exact_match", 1.0)],
        [
            ("exact_match_mean", 1.0),
        ],
    )


def test_run_user_rag_query_function_with_bad_df():
    def rqfn(x: str) -> str:
        return f"This is the output. The query was: {x}"

    df_inputs = pd.DataFrame({"some_col": ["x", "y"]})

    try:
        out_df = e.run(
            rqfn,
            df_inputs,
        )

        assert False, f"Expected ValueError, got {out_df}"
    except ValueError as exn:
        expected = "Input set must have an 'input' column"
        assert expected in str(exn), f"{str(exn)=}"


def test_run_user_rag_query_function_with_df():

    def rqfn(x: str) -> str:
        return f"This is the output. The query was: {x}"

    df_inputs = pd.DataFrame({"input": ["x", "y"]})

    out_df = e.run(
        rqfn,
        df_inputs,
    )

    assert_df_conditions(
        out_df, cols_contain={"input", "output", "traceId"}, rows=2
    )
    outputs = core.pd_series_as_str_list(out_df, "output", fillna="None")
    assert outputs == [
        "This is the output. The query was: x",
        "This is the output. The query was: y",
    ], f"Got {outputs=}"


def test_run_user_rag_query_function():
    def rqfn(x: str) -> str:
        return f"This is the output. The query was: {x}"

    queries = ["x", "y"]

    out_df = e.run(
        rqfn,
        queries,
    )

    assert_df_conditions(
        out_df, cols_contain={"input", "output", "traceId"}, rows=2
    )
    outputs = core.pd_series_as_str_list(out_df, "output", fillna="None")
    assert outputs == [
        "This is the output. The query was: x",
        "This is the output. The query was: y",
    ], f"Got {outputs=}"


# TODO (rossdan): Don't use static screenshot tests by preserving
# old state inside of a pickle file, create the actual test data
# def _pickle_to_df(rel_path: str) -> pd.DataFrame:
#     return cast(pd.DataFrame, pd.read_pickle(abs_path(rel_path)))


# TODO (rossdan): We should be setting up the data ourselves and then
# checking it. Don't use existing data
# from long time again that could be outdated
# def test_get_test_dataset_by_name():
#     # TODO: check stuff like name
#     sets_with_gt = {"set1", "set3"}
#     for setname in ["set1", "set2", "set3"]:
#         logger.warning(f"Downloading setname={setname}")
#         resp = e.get_test_dataset(test_set_name=setname)
#         pdoptions(r=5, c=10, w=10, dw=None)

#         n_cols_base = (
#             9  # No idea what this means or where this number comes from but ok
#         )
#         gt_cols: set[str] = (
#             {"groundTruth"} if setname in sets_with_gt else set()
#         )
#         n_cols = n_cols_base + len(gt_cols)
#         assert_df_conditions(
#             resp,
#             cols_contain={
#                 "inputId",
#                 "updatedAt",
#                 "input",
#                 "InputSetID",
#                 "createdAt",
#                 "querySetName",
#             }
#             | gt_cols,
#             rows=20,
#             cols=n_cols,
#             nulls_axis0=[0] * n_cols,
#             nulls_axis1=[
#                 0,
#                 0,
#                 0,
#                 0,
#                 0,
#                 0,
#                 0,
#                 0,
#                 0,
#                 0,
#                 0,
#                 0,
#                 0,
#                 0,
#                 0,
#                 0,
#                 0,
#                 0,
#                 0,
#                 0,
#             ],
#         )


# def test_get_test_dataset_by_id():
#     # TODO: check stuff like name
#     # TODO (rossdan): We should never use hardcoded IDs in tests
#     # instead, build them and upload them and then test

#     sets_with_gt = {
#         "clwoenwjo0039qymx70nk09k6",
#         "clwoe4b4n003dpeijuzema4kb",
#         "clwoegce1002qqymx26vndd0e",
#     }
#     for setid in [
#         "clwoenwjo0039qymx70nk09k6",
#         "clwoe4b4n003dpeijuzema4kb",
#         "clwoe5rmf003apbpxyo3z2zss",
#         "clwoegce1002qqymx26vndd0e",
#     ]:
#         logger.warning(f"Downloading setid={setid}")
#         resp = e.get_test_dataset(test_set_id=setid)

#         n_cols_base = 9 # No idea what this means or where this number comes from but ok
#         gt_cols: set[str] = {"groundTruth"} if setid in sets_with_gt else set()
#         n_cols = n_cols_base + len(gt_cols)
#         assert_df_conditions(
#             resp,
#             cols_contain={
#                 "inputId",
#                 "updatedAt",
#                 "input",
#                 "InputSetID",
#                 "createdAt",
#                 # Jonathan can I delete `querySetName`? It's not used anywhere:
#                 # eval repo: https://github.com/search?q=repo%3Alastmile-ai%2Feval+queryId&type=code
#                 # lastmile repo: https://github.com/search?q=repo%3Alastmile-ai%2Flastmile%20querySetName&type=code
#                 "querySetName",
#             },
#             rows=2,
#             cols=n_cols,
#             nulls_axis0=[0] * n_cols,
#         )


def test_create_test_dataset_from_df_with_ground_truth():
    try:
        e.create_test_dataset(
            data=pd.DataFrame(
                {"some_col": ["x", "y"], "groundTruth": ["xgt", "ygt"]}
            ),
            name="set3",
        )

        assert False, f"Expected ValueError, but TestSet was created"
    except ValueError as exn:
        expected = "DataFrame must have a 'input' column"
        assert expected in str(exn), f"{str(exn)=}"


def test_create_test_dataset_with_ground_truth():
    test_dataset_id = e.create_test_dataset(
        data=pd.DataFrame(
            {"input": ["x", "y"], "groundTruth": ["xgt", "ygt"]}
        ),
        name="set1",
    )

    test_dataset = e.get_test_dataset(test_dataset_id)

    assert test_dataset.shape[0] == 2
    assert test_dataset["input"].tolist() == ["x", "y"]
    assert test_dataset["groundTruth"].tolist() == ["xgt", "ygt"]


def test_evaluate_no_save_general():
    queries = ["x", "y"]
    evaluators = {"exact_match"}
    resp = e.evaluate(
        project_name=None,
        test_dataset_id="clwofniu5002uqprxtz5q4j6m",
        evaluators=evaluators,
        save_options=e.SaveOptions(save=False),
    )

    # evaluation_result_id=NoneType indicates that no evaluation result entity was created in the DB.
    assert_evaluation_response(
        resp, len(queries), len(evaluators), evaluation_result_id=NoneType
    )

    assert_evaluation_values(
        resp,
        [("exact_match", 1.0), ("exact_match", 1.0)],
        [
            ("exact_match_mean", 1.0),
        ],
    )


def test_evaluate_no_save_bad_df():
    """In the case of save==False, we're stricter about input df.
    It has to have the set Ids so we can download it, because we aren't storing any new
    entities in this case.
    """
    evaluators = {"exact_match"}

    try:
        resp = e.evaluate(
            project_name=None,
            test_dataset=pd.DataFrame({"input": ["x"]}),
            evaluators=evaluators,
            save_options=e.SaveOptions(save=False),
        )

        assert False, f"Expected ValueError, got {resp}"
    except ValueError as exn:
        expected = "DataFrame must have a 'exampleSetId' column"
        assert expected in str(exn), f"{str(exn)=}"


def test_create_test_from_trace_data():
    # Create traces for this run in new project
    project_name = f"test_create_test_from_trace_data{random.randint(0, 1000)}"

    _tracer = get_lastmile_tracer(
        "create_test_from_trace_data",
        project_name=project_name,
    )

    @_tracer.trace_function()
    def _create_trace(input: str, output: str):
        with _tracer.start_span("test_trace"):
            _tracer.log_trace_event(input, output)

    create_count = 10
    for i in range(create_count):
        _create_trace(f"input_{i}", f"output_{i}")

    # Create test set from traces
    test_set_all_traces_id = e.create_test_from_trace_data(
        project_name=project_name,
        name="Test set all traces",
    )
    test_set_all_traces = e.get_test_dataset(test_set_all_traces_id)

    assert test_set_all_traces.shape[0] == create_count
    for i in range(create_count):
        assert (
            test_set_all_traces["input"][i] == f"input_{create_count - i - 1}"
        )
        assert (
            test_set_all_traces["output"][i]
            == f"output_{create_count - i - 1}"
        )

    test_set_sample_traces_id = e.create_test_from_trace_data(
        project_name=project_name,
        name="Test set sample traces",
        sampling_rate=0.5,
    )
    test_set_sample_traces = e.get_test_dataset(test_set_sample_traces_id)
    assert test_set_sample_traces.shape[0] == create_count // 2

    test_set_take_traces_id = e.create_test_from_trace_data(
        project_name=project_name, name="Test set take traces", take=4
    )
    test_set_take_traces = e.get_test_dataset(test_set_take_traces_id)
    assert test_set_take_traces.shape[0] == 4
