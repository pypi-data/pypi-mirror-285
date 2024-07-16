"""
Really important TODOs (that affect the whole library)

* TODO(b7r6): We use the TestSet postgres table to represent both
QuerySet and ExampleSet. This is a disaster and needs fixing.

* TODO(b7r6): dont return np.nan (please grep for this)
"""

# pylint: disable=unsubscriptable-object

import logging
import random
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import (
    Any,
    Callable,
    Generator,
    Literal,
    Mapping,
    NewType,
    Optional,
    Sequence,
    cast,
)
from urllib.parse import urlencode

import lastmile_eval.text.metrics as text_metrics
import lastmile_utils.lib.core.api as core_utils
import pandas as pd
import requests
import result
from lastmile_eval.rag.debugger.common import core
from lastmile_eval.rag.debugger.common.general_functional_utils import (
    do_list,
    res_reduce_list_all_ok,
    unzip2,
)
from lastmile_eval.rag.debugger.common.utils import (
    DEFAULT_PROJECT_ID,
    get_auth_header,
    http_get,
    http_post_and_response_id_lookup,
    key_lookup,
)
from lastmile_eval.rag.debugger.common.types import (
    APIToken,
    BaseURL,
    CreatorID,
    OrganizationID,
    ProjectID,
    Res,
)
from result import Err, Ok

from ..api import LastMileTracer
from ..common.www_translation import (
    df_evaluation_metrics_to_records,
    to_records,
)
from ..tracing import get_lastmile_tracer
from ..tracing.utils import convert_int_id_to_hex_str
from .default_metrics import DEFAULT_METRICS_WITH_DESCRIPTIONS
from .utils.random_words import get_random_adjective, get_random_noun

for name, logger in logging.root.manager.loggerDict.items():
    try:
        if not name.startswith("lastmile"):
            logger.setLevel(logging.CRITICAL)  # type: ignore
    except Exception:
        # logger could be a PlaceHolder...
        pass

logger = logging.getLogger(__name__)
logging.basicConfig(format=core_utils.LOGGER_FMT)

# TODO(jll): control all the logging
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("filelock").setLevel(logging.CRITICAL)


DEFAULT_EXAMPLE_SET_NAME = "Example Set"
DEFAULT_PROJECT_NAME = None
DEFAULT_AGGREGATE_METRICS = ["mean"]


BatchOutputsWithOTELTraceIds = NewType(
    "BatchOutputsWithOTELTraceIds",
    tuple[list[str], list[core.OTelTraceID]],
)


class TestSetType(Enum):
    """
    Types represented by ExampleSet in Postgres. This is useful to keep track of internally
    because we want to distinguish (and want the user to distinguish) between QuerySet and ExampleSet.

    For now, both are stored in the TestSet table.
    """

    EXAMPLE_SET = "DFExampleSet"
    INPUT_SET = "DFInputSet"


@dataclass(frozen=True)
class RunTraceReturn:
    output: str
    otel_trace_id: core.OTelTraceID


class RunTraceFunction:
    def __call__(self, query: str) -> RunTraceReturn: ...


def wrap_with_tracer(
    run_fn: Callable[[str], str],
    project_name: Optional[str],
    lastmile_api_token: Optional[str],
) -> RunTraceFunction:
    class RunQueryFnImpl(RunTraceFunction):
        def __call__(self, query: str) -> RunTraceReturn:
            tracer: LastMileTracer = get_lastmile_tracer(
                "my-tracer",
                project_name=project_name,
                lastmile_api_token=lastmile_api_token,
            )
            with tracer.start_as_current_span(
                "evaluation_library_run_query_fn"
            ) as wrapper_span:
                trace_id_raw = wrapper_span.get_span_context().trace_id
                otel_trace_id = core.OTelTraceID(
                    convert_int_id_to_hex_str(trace_id_raw)
                )

                # TODO(jll): catch exceptions, timeout here
                # (as low as possible)
                output = run_fn(query)
                return RunTraceReturn(
                    output=output, otel_trace_id=otel_trace_id
                )

    return RunQueryFnImpl()


# User-facing Types

Evaluator = Callable[
    [pd.DataFrame],
    list[float],
]

# Given a list of metrics, aggregates them into a single metric (e.g. mean)
Aggregator = Callable[[pd.DataFrame], float]


@dataclass(frozen=True)
class EvaluatorTuple:
    evaluator: Evaluator
    aggregator: Aggregator


@dataclass(frozen=True)
class SaveOptions:
    # Save the results in the DB. If false, results will just be returned but not persisted anywhere.
    save: bool = True
    # Saves the evaluation result, as well as the Test Set (if provided as a dataframe instead of id), using this name
    name: Optional[str] = None


@dataclass
class EvaluationResult:
    evaluation_result_id: Optional[core.EvaluationResultId]
    test_dataset_id: Optional[core.InputSetID]
    evaluator_metrics_df: pd.DataFrame
    aggregated_metrics: Optional[
        pd.DataFrame
    ]  # TODO: Use this somehow? Optional[Mapping[str, float]]


@dataclass
class CreateExampleSetResponse:
    success: bool
    message: str
    id: core.ExampleSetID


@dataclass
class CreateInputSetResponse:
    success: bool
    message: str
    id: core.InputSetID


@dataclass
class BatchDownloadParams:
    batch_limit: int
    search: Optional[str] = None
    trace_id: Optional[core.RAGQueryTraceID] = None
    creator_id: Optional[CreatorID] = None
    project_id: Optional[ProjectID] = None
    organization_id: Optional[OrganizationID] = None
    start_timestamp: Optional[str] = None
    end_timestamp: Optional[str] = None
    event_name: Optional[str] = None


@dataclass
class BatchTraceDownloadParams:
    batch_limit: int = 50
    project_id: Optional[ProjectID] = None
    trace_ids: Optional[list[core.RAGQueryTraceID]] = None
    take: Optional[int] = None
    search_filter: Optional[str] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None


def _get_example_set_ids_by_name(
    base_url: BaseURL,
    example_set_name: str,
    project_id: Optional[ProjectID],
    lastmile_api_token: APIToken,
) -> Res[list[core.ExampleSetID]]:
    endpoint_without_args = "evaluation_test_sets/list"
    params = {"name": example_set_name}
    if project_id is not None:
        params["projectId"] = project_id
    encoded_params = urlencode(params)
    endpoint = f"{endpoint_without_args}?{encoded_params}"
    headers = get_auth_header(lastmile_api_token)
    response = http_get(base_url, endpoint, headers)

    def _parse_response(
        response: requests.Response,
    ) -> Res[list[core.ExampleSetID]]:
        if response.status_code != 200:
            return Err(
                ValueError(
                    f"LastMile website returned error:\n{response.text[:100]}..."
                )
            )

        if "evaluationTestSets" not in response.json():
            return Err(
                ValueError(f"Expected 'evaluationTestSets' in response.")
            )

        example_sets: list[core_utils.JSONDict] = response.json()[
            "evaluationTestSets"
        ]

        def _raw_example_set_to_id(
            raw: core_utils.JSONDict,
        ) -> Res[core.ExampleSetID]:
            id_raw = key_lookup("id", raw)
            out: Res[core.ExampleSetID] = result.do(
                Ok(core.ExampleSetID(str(id_ok))) for id_ok in id_raw
            )
            return out

        return res_reduce_list_all_ok(
            map(_raw_example_set_to_id, example_sets)
        )

    return response.and_then(_parse_response)


def _download_example_set(
    base_url: BaseURL,
    lastmile_api_token: APIToken,  # "Explicit is better than implicit." - The Zen of Python
    example_set_id: Optional[core.ExampleSetID] = None,
) -> Res[core.DFExampleSet]:
    # api/evaluation_test_sets/list doesn't return the underlying test cases

    query_args: dict[str, str] = {}
    if example_set_id is not None:
        query_args["testSetId"] = example_set_id
    endpoint = f"evaluation_test_cases/list?{urlencode(query_args)}"

    headers = get_auth_header(lastmile_api_token)
    response = http_get(base_url, endpoint, headers)

    def _process_response(
        response: requests.Response,
    ) -> Res[core.DFExampleSet]:
        raw_test_cases = response.json()["evaluationTestCases"]

        df_records = (
            pd.DataFrame.from_records(raw_test_cases)  # type: ignore
            .rename(
                columns={
                    "id": "exampleId",
                    "testSetId": "exampleSetId",
                    "testSetName": "exampleSetName",
                }
            )
            .reset_index()
        )

        if example_set_id is not None and "exampleSetId" in df_records.columns:
            df_records = df_records.query(f"exampleSetId == '{example_set_id}'")  # type: ignore[pandas]

        if len(df_records) == 0:
            return Err(
                ValueError(
                    f"No test cases found for {example_set_id=}.\n"
                    f"If you provided a example_set_id filter, "
                    "Please check whether the ID exists "
                    "and you have permission to view it.\n"
                    f"\nLastmile website returned {response.text[:100]}...."
                )
            )

        return core.df_as_df_example_set(df_records)

    return response.and_then(_process_response)


def download_example_set_helper(
    base_url: BaseURL,
    lastmile_api_token: APIToken,
    project_id: Optional[ProjectID],
    example_set_id: Optional[core.ExampleSetID] = None,
    example_set_name: Optional[str] = None,
) -> Res[core.DFExampleSet]:
    def _concat(res: list[core.DFExampleSet]) -> Res[core.DFExampleSet]:
        df_all = pd.concat(res)  # type: ignore
        return core.df_as_df_example_set(df_all)

    def _assign_name(
        df: core.DFExampleSet, example_set_name: Optional[str]
    ) -> Res[core.DFExampleSet]:
        if example_set_name is None:
            example_set_name = "<unknown>"
        out = df.assign(exampleSetName=example_set_name)  # type: ignore
        return core.df_as_df_example_set(out)

    def _get_ids_allowed(
        example_set_name: Optional[str],
        example_set_id: Optional[core.ExampleSetID],
    ) -> Res[list[core.ExampleSetID]]:
        # Supports 3 cases (at least input is not None).
        if example_set_id is None and example_set_name is not None:
            # Just example_set_name filter given. Simply look up the IDs.
            # (No other filtering)
            return _get_example_set_ids_by_name(
                base_url, example_set_name, project_id, lastmile_api_token
            )
        elif example_set_id is not None and example_set_name is None:
            # Just example_set_id filter given. Simply return it.
            # (No other filtering)
            return Ok([example_set_id])
        elif example_set_id is not None and example_set_name is not None:
            # TODO (rossdan): We should throw an error so the API is more clear that
            # only one of example_set_id or example_set_name should be provided.
            # Both filters given. Look up the IDs by name, then intersect them
            # with the given set ID.
            ids_by_name = _get_example_set_ids_by_name(
                base_url, example_set_name, project_id, lastmile_api_token
            )
            # Intersect the ID list corresponding to the name with the given ID
            # (If the ID list was looked up successfully).
            return result.do(
                Ok(list(set(ids_by_name_ok) & set({example_set_id})))
                for ids_by_name_ok in ids_by_name
            )
        else:
            # The only not-allowed case.
            return Err(
                ValueError(
                    "Either test_dataset_id or test_dataset must be provided."
                )
            )

    def _download_all_example_sets_by_id(
        ids: list[core.ExampleSetID],
        lastmile_api_token: APIToken,
        base_url: BaseURL,
    ) -> list[Res[core.DFExampleSet]]:
        # TODO(b7r6) use do_list for this
        return [
            _download_example_set(
                base_url,
                lastmile_api_token,
                example_set_id_,
            ).and_then(
                partial(_assign_name, example_set_name=example_set_name)
            )
            for example_set_id_ in ids
        ]

    list_dfs_downloaded = result.do(
        res_reduce_list_all_ok(
            _download_all_example_sets_by_id(
                ids_allowed_ok, lastmile_api_token, base_url
            )
        )
        for ids_allowed_ok in _get_ids_allowed(
            example_set_name, example_set_id
        )
    )

    df_all = list_dfs_downloaded.and_then(_concat)

    return df_all


def _run_evaluations_helper(
    df_test_cases: core.DFExampleSet,
    evaluators_example_level: list[core.RAGQueryExampleLevelEvaluator],
    evaluators_aggregated: list[core.DatasetLevelEvaluator],
) -> Res[
    tuple[
        core.DFRAGQueryExampleEvaluations,
        Optional[core.DFRAGQueryDatasetEvaluations],
    ]
]:
    example_sets = set(
        core.pd_series_as_optional_str_list(df_test_cases, "exampleSetId")
    )
    if len(example_sets) > 1:
        return Err(
            ValueError(
                "Dataset-level evaluators were given, but "
                f"multiple test sets were found: {','.join(map(str, example_sets))}"
                "\nCurrently, only one test set per dataframe "
                "is supported."
            )
        )

    if len(evaluators_example_level) == 0:
        return Err(
            ValueError(
                "No evaluators were provided. Please provide at least one valid evaluator in the `evaluators` argument."
            )
        )

    df_example_level = None
    df_aggregated = None

    dfs_evaluations_example_level: list[core.DFRAGQueryExampleEvaluations] = []
    for evaluator in evaluators_example_level:
        df_example_level_ = evaluator(df_test_cases)
        dfs_evaluations_example_level.append(df_example_level_)

    df_example_level = cast(
        core.DFRAGQueryExampleEvaluations, pd.concat(dfs_evaluations_example_level)  # type: ignore
    )

    dfs_aggregated: list[core.DFRAGQueryDatasetEvaluations] = []
    for evaluator in evaluators_aggregated:
        df_aggregated_ = evaluator(df_test_cases)

        dfs_aggregated.append(df_aggregated_)

        if len(dfs_aggregated) > 0:
            df_aggregated = cast(
                core.DFRAGQueryDatasetEvaluations, pd.concat(dfs_aggregated)  # type: ignore
            )

    return Ok((df_example_level, df_aggregated))


def _run_and_store_evaluations_helper(
    base_url: BaseURL,
    lastmile_api_token: APIToken,
    example_set_id: core.ExampleSetID,
    evaluation_set_name: Optional[str],
    project_id: Optional[ProjectID],
    example_level_evaluators: list[core.RAGQueryExampleLevelEvaluator],
    aggregated_evaluators: list[core.DatasetLevelEvaluator],
) -> Res[EvaluationResult]:
    base_url = BaseURL(base_url)
    df_test_cases = _download_example_set(
        base_url,
        lastmile_api_token,
        example_set_id,
    )

    dfs_metrics = result.do(
        _run_evaluations_helper(
            df_test_cases_ok,
            example_level_evaluators,
            aggregated_evaluators,
        )
        for df_test_cases_ok in df_test_cases
    )

    def _store_results(
        dfs_metrics: tuple[
            core.DFRAGQueryExampleEvaluations,
            Optional[core.DFRAGQueryDatasetEvaluations],
        ]
    ) -> Res[EvaluationResult]:
        df_metrics_example_level, df_metrics_aggregated = dfs_metrics

        return _store_evaluation_set_results_helper(
            base_url,
            lastmile_api_token,
            evaluation_set_name,
            project_id,
            example_set_id,
            df_metrics_example_level=df_metrics_example_level,
            df_metrics_aggregated=df_metrics_aggregated,
        )

    return dfs_metrics.and_then(_store_results)


def _store_evaluation_set_results_helper(
    base_url: BaseURL,
    lastmile_api_token: APIToken,
    evaluation_set_name: Optional[str],
    project_id: Optional[ProjectID],
    example_set_id: core.ExampleSetID,
    df_metrics_example_level: core.DFRAGQueryExampleEvaluations,
    df_metrics_aggregated: Optional[core.DFRAGQueryDatasetEvaluations] = None,
) -> Res[EvaluationResult]:
    """
    Upload evaluations results for persistence and analysis in UI.

    Metrics can be either trace-level or dataset-level.
    Both are optional, at least one is required.

    """

    def _get_example_set_id(
        df_metrics_example_level: core.DFRAGQueryExampleEvaluations,
        df_metrics_aggregated: Optional[core.DFRAGQueryDatasetEvaluations],
        example_set_id: core.ExampleSetID,
    ) -> Res[core.ExampleSetID]:
        example_set_ids_example_level: set[str] = (  # type: ignore
            set(df_metrics_example_level.exampleSetId.unique())  # type: ignore
        )
        example_set_ids_aggregated: set[str] = (  # type: ignore
            set(df_metrics_aggregated.exampleSetId.unique())  # type: ignore
            if df_metrics_aggregated is not None
            else set()
        )
        all_ids_for_metrics = set(example_set_ids_example_level) | set(
            example_set_ids_aggregated
        )
        if all_ids_for_metrics <= {example_set_id}:
            return Ok(example_set_id)
        else:
            return Err(
                ValueError(
                    "Mismatched test set IDs. Please make sure your metrics dataframes correspond to one test set."
                )
            )

    example_set_id_ = _get_example_set_id(
        df_metrics_example_level, df_metrics_aggregated, example_set_id
    )

    outcome: Res[EvaluationResult] = result.do(
        _store_evaluations_for_example_set(
            base_url,
            lastmile_api_token,
            evaluation_set_name,
            example_set_id_ok_,
            project_id,
            df_metrics_example_level,
            df_metrics_aggregated,
        )
        for example_set_id_ok_ in example_set_id_
    )

    return outcome


def _get_random_evaluation_set_name() -> str:
    word_1 = get_random_adjective()
    word_2 = get_random_noun()
    number = random.randint(100, 999)
    return f"{word_1}-{word_2}-{number}"


def _store_evaluations_for_example_set(
    base_url: BaseURL,
    lastmile_api_token: APIToken,
    evaluation_set_name: Optional[str],
    example_set_id: core.ExampleSetID,
    project_id: Optional[ProjectID],
    df_metrics_example_level: core.DFRAGQueryExampleEvaluations,
    df_metrics_aggregated: Optional[core.DFRAGQueryDatasetEvaluations],
) -> Res[EvaluationResult]:
    evaluation_result_name = (
        evaluation_set_name or _get_random_evaluation_set_name()
    )
    endpoint = "evaluation_sets/create"
    headers = get_auth_header(lastmile_api_token)

    df_trace = df_metrics_example_level.query(  # type: ignore[fixme]
        f"exampleSetId == '{example_set_id}'"
    )
    example_level_metrics = df_evaluation_metrics_to_records(df_trace)

    aggregated_metrics = []
    if df_metrics_aggregated is not None:
        df_dataset = df_metrics_aggregated.query(  # type: ignore[fixme]
            f"exampleSetId == '{example_set_id}'"
        )

        aggregated_metrics = df_evaluation_metrics_to_records(df_dataset)

    # TODO(b7r6) make a type-checked translation layer to/from www to convert names.
    data: dict[str, Any] = {
        "testSetId": example_set_id,
        "name": evaluation_result_name,
        "evaluationMetrics": example_level_metrics,
        "evaluationSetMetrics": aggregated_metrics,
        "projectId": project_id,
    }
    outcome: Res[EvaluationResult] = result.do(
        Ok(
            EvaluationResult(
                evaluation_result_id=core.EvaluationResultId(
                    response_ok.returned_id
                ),
                test_dataset_id=core.InputSetID(example_set_id),
                evaluator_metrics_df=df_metrics_example_level,
                aggregated_metrics=df_metrics_aggregated,
            )
        )
        for response_ok in http_post_and_response_id_lookup(
            base_url, endpoint, headers, data
        )
    )

    return outcome


def _default_dataset_aggregators(
    example_level_evaluator: core.RAGQueryExampleLevelEvaluator,
) -> list[core.DatasetLevelEvaluator]:
    def _agg(
        df: core.DFExampleSet, stat: str
    ) -> core.DFRAGQueryDatasetEvaluations:
        trace_evals = example_level_evaluator(df)
        aggregated = (  # type: ignore
            trace_evals.groupby(["exampleSetId", "metricName"])[["value"]]  # type: ignore
            .agg(stat)
            .reset_index()
            .drop(
                columns=[
                    "ragQueryTraceId",
                ],
                errors="ignore",
            )
        )
        renamed = aggregated.assign(  # type: ignore
            metricName=lambda df: df.metricName + "_" + stat  # type: ignore
        )

        # vscode can infer more about pandas than cli pyright
        # vscode thinks cast is redundant
        # CLI needs the cast otherwise reports:
        # "Argument type is partially unknown..."
        renamed = cast(pd.DataFrame, renamed)  # type: ignore[fixme]

        return core.df_as_df_dataset_evaluations(renamed)

    # TODO: Only include mean as default, the others are annoying
    return [partial(_agg, stat=stat) for stat in DEFAULT_AGGREGATE_METRICS]


def user_provided_evaluators_to_all_typed_evaluators(
    example_level_evaluators: (
        Mapping[
            str,
            Evaluator
            | EvaluatorTuple,  # Tuple of Evaluator function and (optionally) Aggregator function,
        ]
        | set[str]
    ),
    lastmile_api_token: APIToken,
) -> Res[
    tuple[
        list[core.RAGQueryExampleLevelEvaluator],
        list[core.DatasetLevelEvaluator],
    ]
]:
    if isinstance(example_level_evaluators, set):
        example_level_evaluators = get_default_evaluators_helper(
            example_level_evaluators, lastmile_api_token=lastmile_api_token
        )

    if len(example_level_evaluators) == 0:
        return Err(
            ValueError(
                "No evaluators provided or inferred. Please provide at least one evaluator."
            )
        )

    trace_evaluators_typed: list[core.RAGQueryExampleLevelEvaluator] = []
    default_dataset_evaluators: list[core.DatasetLevelEvaluator] = []
    provided_dataset_evaluators: list[core.DatasetLevelEvaluator] = []

    for metric_name, evaluator in example_level_evaluators.items():
        if isinstance(
            evaluator, Callable
        ):  # Python sucks, can't do `isinstance(evaluator, Evaluator)` check directly
            trace_evaluator = core.callable_as_example_level_evaluator(
                metric_name, evaluator
            )
            trace_evaluators_typed.append(trace_evaluator)
            default_dataset_evaluators += _default_dataset_aggregators(
                trace_evaluator
            )
        else:
            trace_evaluators_typed.append(
                core.callable_as_example_level_evaluator(
                    metric_name, evaluator.evaluator
                )
            )
            provided_dataset_evaluators.append(
                core.callable_as_aggregated_evaluator(
                    metric_name, evaluator.aggregator
                )
            )

    all_dataset_evaluators_typed = (
        default_dataset_evaluators + provided_dataset_evaluators
    )
    return Ok((trace_evaluators_typed, all_dataset_evaluators_typed))


def _post_filter_rag_tracelike(
    df: core.T_RAGTracelike, params: BatchDownloadParams
) -> core.T_RAGTracelike:
    if params.trace_id is not None:
        df = df.query(f"traceId == '{params.trace_id}'")  # type: ignore[pandas]
    if params.creator_id is not None:
        df = df.query(f"creatorId == '{params.creator_id}'")  # type: ignore[pandas]
    if params.project_id is not None:
        df = df.query(f"projectId == '{params.project_id}'")  # type: ignore[pandas]
    if params.organization_id is not None:
        df = df.query(f"organizationId == '{params.organization_id}'")  # type: ignore[pandas]
    if params.event_name is not None and "eventName" in df.columns:
        df = df.query(f"eventName == '{params.event_name}'")  # type: ignore[pandas]

    start_timestamp = params.start_timestamp
    if start_timestamp is None:
        # 3 months ago
        start_timestamp = pd.Timestamp.now() - pd.DateOffset(months=3)

    df = df.query(f"createdAt >= '{start_timestamp}'")  # type: ignore
    if params.end_timestamp is not None:
        df = df.query(f"createdAt <= '{params.end_timestamp}'")  # type: ignore

    return df


def download_rag_query_traces_helper(
    base_url: BaseURL,
    lastmile_api_token: APIToken,
    batch_download_params: BatchTraceDownloadParams,
) -> Res[Generator[Res[core.DFRAGQueryTrace], None, None]]:
    def _generator():
        should_continue: bool = True
        cursor: Optional[str] = None
        res_count: int = 0

        while should_continue:

            batch_limit = batch_download_params.batch_limit
            if batch_download_params.take is not None:
                count_remaining = batch_download_params.take - res_count
                if count_remaining == 0:
                    should_continue = False
                    continue
                if count_remaining < batch_limit:
                    batch_limit = count_remaining

            batch = _download_rag_query_trace_batch(
                base_url,
                lastmile_api_token,
                batch_limit,
                cursor,  # type: ignore[fixme]
                batch_download_params.project_id,
                batch_download_params.trace_ids,
                batch_download_params.search_filter,
                batch_download_params.start_time,
                batch_download_params.end_time,
            )
            match batch:
                case Ok((df, new_cursor, has_more)):
                    cursor = new_cursor
                    should_continue = has_more
                    df_length = len(df)
                    res_count += df_length
                    if df_length == 0:
                        continue
                    yield Ok(df)
                case Err(e):
                    # ValueError is thrown if results are empty, which can happen if
                    # trying to load final page after the last cursor, since hasMore logic
                    # has false positives.
                    # TODO(LAS-478): Fix hasMore logic to prevent the need for this
                    if isinstance(e, ValueError):
                        should_continue = False
                        continue
                    yield Err(e)

    return Ok(_generator())


def download_rag_events_helper(
    base_url: BaseURL,
    lastmile_api_token: APIToken,
    batch_download_params: BatchDownloadParams,
) -> Res[Generator[Res[core.DFRAGEvent], None, None]]:
    def _generator():
        should_continue = True
        cursor: Optional[str] = None
        while should_continue:
            batch = _download_rag_event_batch(
                base_url,
                lastmile_api_token,
                batch_download_params.batch_limit,
                cursor,  # type: ignore[fixme]
                batch_download_params.search,
            )
            match batch:
                case Ok((df, cursor, has_more)):
                    df = _post_filter_rag_tracelike(df, batch_download_params)
                    cursor = cursor
                    should_continue = has_more
                    if len(df) == 0:
                        continue
                    yield Ok(df)
                case Err(e):
                    yield Err(e)

    return Ok(_generator())


def _download_rag_tracelike_batch(
    base_url: BaseURL,
    lastmile_api_token: APIToken,
    batch_limit: int,
    endpoint_without_args: str,
    parse_http_response_fn: Callable[
        [Res[requests.Response]], Res[core.T_RAGTracelike]
    ],
    cursor: Optional[str],
    filter_params: Optional[dict[str, Any]] = None,
) -> Res[tuple[core.T_RAGTracelike, str, bool]]:
    params = {
        "pageSize": batch_limit,
        "cursor": cursor,
    }
    if filter_params is not None:
        params.update(filter_params)
    params = {key: value for key, value in params.items() if value is not None}

    encoded_params = urlencode(params, True)
    endpoint = f"{endpoint_without_args}?{encoded_params}"
    headers = get_auth_header(lastmile_api_token)
    raw_response = http_get(base_url, endpoint, headers)
    response = raw_response

    df = parse_http_response_fn(response)

    def _get_cursor(response: dict[str, Any]) -> Res[str]:
        if "cursor" not in response:
            return Err(ValueError(f"Expected 'cursor' in response"))
        return Ok(response["cursor"])

    def _get_has_more(response: dict[str, Any]) -> Res[bool]:
        if "hasMore" not in response:
            return Err(ValueError(f"Expected 'hasMore' in response"))
        return Ok(response["hasMore"])

    out: Res[tuple[core.T_RAGTracelike, str, bool]] = result.do(
        Ok((df_ok, cursor_ok, has_more_ok))
        for df_ok in df
        for response_ok in response
        for cursor_ok in _get_cursor(response_ok.json())
        for has_more_ok in _get_has_more(response_ok.json())
    )

    return out


def _download_rag_query_trace_batch(
    base_url: BaseURL,
    lastmile_api_token: APIToken,
    batch_limit: int,
    cursor: Optional[str],
    project_id: Optional[ProjectID],
    trace_ids: Optional[list[core.RAGQueryTraceID]],
    search_filter: Optional[str] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
) -> Res[tuple[core.DFRAGQueryTrace, str, bool]]:
    endpoint_without_args = "rag_query_traces/list"

    def _parse_http_response(
        response: Res[requests.Response],
    ) -> Res[core.DFRAGQueryTrace]:
        match response:
            case Err(e):
                return Err(e)
            case Ok(response_ok):
                if (
                    "queryTraces" not in response_ok.json()
                    or len(response_ok.json()["queryTraces"]) == 0
                ):
                    return Err(
                        ValueError(f"No query traces found. {response=}")
                    )

        df = result.do(
            core.df_as_df_rag_query_trace(
                pd.DataFrame.from_records(  # type: ignore[pandas]
                    response_ok.json()["queryTraces"]
                ).rename(columns={"id": "ragQueryTraceId"})
            )
            for response_ok in response
        )
        return df

    filter_params = {
        "ids": trace_ids,
        "search": search_filter,
        "startTime": (
            start_time * 1000 if start_time is not None else None
        ),  # Convert to ms
        "endTime": (
            end_time * 1000 if end_time is not None else None
        ),  # Convert to ms
    }

    # If filtering on trace_ids and no specified project, don't filter on default project
    filter_project_id = project_id
    if project_id == DEFAULT_PROJECT_ID and trace_ids:
        filter_project_id = None

    filter_params["projectId"] = filter_project_id

    filter_params = {
        key: value for key, value in filter_params.items() if value is not None
    }

    return _download_rag_tracelike_batch(
        base_url,
        lastmile_api_token,
        batch_limit,
        endpoint_without_args,
        _parse_http_response,
        cursor,
        filter_params,
    )


def _download_rag_event_batch(
    base_url: BaseURL,
    lastmile_api_token: APIToken,
    batch_limit: int,
    cursor: Optional[str],
    search: Optional[str] = None,
) -> Res[tuple[core.DFRAGEvent, str, bool]]:
    endpoint_without_args = "rag_events/list"

    def _parse_http_response(
        response: Res[requests.Response],
    ) -> Res[core.DFRAGEvent]:
        match response:
            case Err(e):
                return Err(e)
            case Ok(response_ok):
                if (
                    "events" not in response_ok.json()
                    or len(response_ok.json()["events"]) == 0
                ):
                    return Err(
                        ValueError(f"No query traces found. {response=}")
                    )

        df = result.do(
            core.df_as_df_rag_events(
                pd.DataFrame.from_records(  # type: ignore[pandas]
                    response_ok.json()["events"]
                ).rename(columns={"id": "ragEventId"})
            )
            for response_ok in response
        )
        return df

    return _download_rag_tracelike_batch(
        base_url,
        lastmile_api_token,
        batch_limit,
        endpoint_without_args,
        _parse_http_response,
        cursor,
        {"search": search},
    )


def _create_example_set_from_inputs_and_outputs(
    base_url: BaseURL,
    project_id: Optional[ProjectID],
    lastmile_api_token: APIToken,
    inputs: Sequence[str],
    outputs_with_trace_ids: BatchOutputsWithOTELTraceIds,
    example_set_name: Optional[str],
    ground_truth: Optional[Sequence[str]] = None,
) -> Res[CreateExampleSetResponse]:
    outputs, otel_trace_ids = outputs_with_trace_ids

    df = core.df_as_df_minimal_example_set(
        pd.DataFrame(
            {
                "input": inputs,
                "output": outputs,
                "groundTruth": ground_truth,
                "traceId": otel_trace_ids,
            }
        )
    )

    return result.do(
        _create_example_set_from_df(
            base_url,
            project_id,
            lastmile_api_token,
            df_ok,
            TestSetType.EXAMPLE_SET,
            example_set_name,
        )
        for df_ok in df
    )


def _example_set_create_res_to_input_set_create_res(
    example_set_create_res: CreateExampleSetResponse,
) -> CreateInputSetResponse:
    return CreateInputSetResponse(
        success=example_set_create_res.success,
        message=example_set_create_res.message,
        id=core.InputSetID(example_set_create_res.id),
    )


def create_test_dataset_helper(
    base_url: BaseURL,
    project_id: Optional[ProjectID],
    queries: pd.DataFrame,
    lastmile_api_token: APIToken,
    input_set_name: Optional[str] = None,
):
    queries_and_gt = _get_input_and_ground_truth(queries)

    def _create_input_set_from_inputs_and_list(
        base_url: BaseURL,
        lastmile_api_token: APIToken,
        inputs: Sequence[str],
        ground_truth: Optional[Sequence[str]],
        input_set_name: Optional[str],
    ) -> Res[CreateInputSetResponse]:
        df = core.df_as_df_minimal_example_set(
            pd.DataFrame({"input": inputs, "groundTruth": ground_truth})
        )

        example_set_res = result.do(
            _create_example_set_from_df(
                base_url,
                project_id,
                lastmile_api_token,
                df_ok,
                TestSetType.INPUT_SET,
                input_set_name,
            )
            for df_ok in df
        )

        return example_set_res.map(
            _example_set_create_res_to_input_set_create_res
        )

    outcome = result.do(
        _create_input_set_from_inputs_and_list(
            base_url,
            lastmile_api_token,
            queries_and_gt_ok[0],
            queries_and_gt_ok[1],
            input_set_name,
        )
        for queries_and_gt_ok in queries_and_gt
    )

    return outcome


def _create_example_set_from_df(
    base_url: BaseURL,
    project_id: Optional[ProjectID],
    lastmile_api_token: APIToken,
    df: core.DFExampleSet | core.DFMinimalExampleSet,
    test_set_type: TestSetType,
    example_set_name: Optional[str],
) -> Res[CreateExampleSetResponse]:
    default_name = {
        TestSetType.EXAMPLE_SET: "Example Set",
        TestSetType.INPUT_SET: "Input Set",
    }[test_set_type]
    example_set_name = example_set_name or default_name
    endpoint = "evaluation_test_sets/create"
    headers = get_auth_header(lastmile_api_token)

    allowed_columns = [
        "input",
        "output",
        "eventData",
        "groundTruth",
        # TODO (rossdan): Remove `ragQueryTraceId` and just use `traceId` only
        "ragQueryTraceId",
        "traceId",
    ]
    # These are legacy columns that are not needed for the ExampleSet
    ok_to_drop_columns = [
        "query",
        "context",
        "fullyResolvedPrompt",
        "llmOutput",
    ]

    all_columns_without_legacy_ones = set(df.columns) - set(ok_to_drop_columns)  # type: ignore
    excluded_columns = cast(list[str], list(all_columns_without_legacy_ones - set(allowed_columns)))  # type: ignore
    if len(excluded_columns) > 0:
        logger.warning(
            f"Must drop given columns to create Example set: {excluded_columns}"
        )

    df_allowed: pd.DataFrame = df.drop(columns=excluded_columns)  # type: ignore[pandas]

    data: core_utils.JSONDict = {
        "name": example_set_name,
        "testCases": to_records(df_allowed),
    }
    if project_id is not None and project_id != DEFAULT_PROJECT_ID:
        data["projectId"] = project_id

    outcome: Res[CreateExampleSetResponse] = result.do(
        Ok(
            CreateExampleSetResponse(
                success=response_ok.status_code == 200,
                message=response_ok.text,
                id=core.ExampleSetID(response_ok.returned_id),
            )
        )
        for response_ok in http_post_and_response_id_lookup(
            base_url, endpoint, headers, data
        )
    )
    return outcome


def clean_rag_query_tracelike_df(df: pd.DataFrame) -> pd.DataFrame:
    def _unpack_all(df: pd.DataFrame) -> pd.DataFrame:
        def _value_to_series(x: Any) -> pd.Series | Any:  # type: ignore
            try:
                return pd.Series(x)  # type: ignore
            except Exception:
                return x

        def _add_nested_cols_to_df(df: pd.DataFrame, col: str) -> pd.DataFrame:
            df_col_exploded = None
            try:
                df_col_exploded = df[col].apply(_value_to_series)  # type: ignore
            except Exception:
                pass

            if df_col_exploded is not None:
                for c in df_col_exploded:  # type: ignore[fixme]
                    if c not in df:
                        df[c] = df_col_exploded  # type: ignore[fixme]
            return df

        # TODO (rossdan): Instead of extracting nested keys or arrays,
        # just ensure that input and output
        # can only be text format in the tracing SDK, this will remove the
        # need to unpack the columns and have this cleanup method at all
        df = _add_nested_cols_to_df(df, "input")
        df = _add_nested_cols_to_df(df, "output")

        # TODO (rossdan): Drop index
        df = df.drop(  # type: ignore
            columns=["index"],
            errors="ignore",
        )

        return df

    try:
        return _unpack_all(df)
    except Exception:
        return df


def run_rag_query_fn_helper(
    rag_query_fn: RunTraceFunction,
    inputs: Sequence[str] | pd.DataFrame,
) -> Res[BatchOutputsWithOTELTraceIds]:
    """
    Out: (outputs, rag_query_trace_ids)
    """

    def _get_seq(
        inputs: Sequence[str] | pd.DataFrame,
    ) -> Res[list[str]]:
        if isinstance(inputs, pd.DataFrame):
            if "input" not in inputs.columns:
                return Err(ValueError("Input set must have an 'input' column"))
            return Ok(inputs["input"].tolist())  # type: ignore[pandas]
        return Ok(list(inputs))

    inputs_seq = _get_seq(inputs)

    def _safe_run(input_query: str) -> Res[RunTraceReturn]:
        # TODO(jll): timeout
        try:
            return Ok(rag_query_fn(input_query))
        except Exception as e:
            return Err(e)

    def _extract_str_values(
        output: RunTraceReturn,
    ) -> tuple[str, core.OTelTraceID]:
        return output.output, output.otel_trace_id

    def _run_and_process_output(
        input_query: str,
    ) -> Res[tuple[str, core.OTelTraceID]]:
        return _safe_run(input_query).map(_extract_str_values)

    def _run_and_process_all(
        inputs: list[str],
    ) -> Res[BatchOutputsWithOTELTraceIds]:
        out = (
            do_list(_run_and_process_output, inputs)
            .map(unzip2)
            .map(BatchOutputsWithOTELTraceIds)
        )
        return out

    return inputs_seq.and_then(_run_and_process_all)


def _get_input_and_ground_truth(
    df: pd.DataFrame,
) -> Res[tuple[list[str], Optional[list[str]]]]:
    """Out: (queries, ground_truth)"""
    # TODO (rossdan): Allow user to specify their input values from eventData column
    # Will need to create some helper method to extract after we call run()
    if "input" not in df.columns:
        return Err(ValueError("The input set must contain an 'input' column."))

    inputs = core.pd_series_as_str_list(df, "input", fillna="None")
    ground_truth: Optional[list[str]] = None
    if "groundTruth" in df.columns:
        ground_truth = core.pd_series_as_str_list(
            df, "groundTruth", fillna="None"
        )
    return Ok((inputs, ground_truth))


def _create_or_get_example_set(
    test_dataset_id: Optional[core.ExampleSetID],
    test_dataset: Optional[pd.DataFrame],
    base_url: BaseURL,
    project_id: Optional[ProjectID],
    lastmile_api_token: APIToken,
    example_set_name: Optional[str],
) -> Res[str]:
    if test_dataset_id is not None and test_dataset is None:
        return Ok(test_dataset_id)

    if test_dataset_id is None and test_dataset is not None:
        return result.do(
            Ok(example_set_ok.id)
            for df_example_set_ok in core.df_as_df_minimal_example_set(
                test_dataset
            )
            for example_set_ok in _create_example_set_from_df(
                base_url,
                project_id,
                lastmile_api_token,
                df_example_set_ok,
                TestSetType.EXAMPLE_SET,
                example_set_name,
            )
        )

    return Err(
        ValueError(
            "Exactly one of test_dataset_id, test_dataset must be provided."
        )
    )


# TODO: Use DefaultMetric enum instead of str value
def get_default_evaluators_with_descriptions() -> dict[str, str]:
    return DEFAULT_METRICS_WITH_DESCRIPTIONS


def get_default_evaluators_helper(
    names: set[str], lastmile_api_token: APIToken
) -> dict[str, Evaluator]:
    def _wrap1(
        df: pd.DataFrame,
        base_metric: Callable[[Sequence[str]], Sequence[float]],
    ):
        if df[["output"]].isnull().any().any():  # type: ignore[union-attr]
            logger.warning(
                "None values found in the input data. Check your 'output' column. Coercing to string."
            )
        output = core.pd_series_as_str_list(df, "output", fillna="None")
        return list(base_metric(output))

    def _wrap2(
        df: pd.DataFrame,
        base_metric: Callable[[Sequence[str], Sequence[str]], Sequence[float]],
        reference_col: (
            Literal["groundTruth"] | Literal["input"]
        ) = "groundTruth",
    ):
        if df[["output", reference_col]].isnull().any().any():  # type: ignore[pandas]
            logger.warning(
                f"None values found in the input data. Check your 'output' and '{reference_col}' columns. Coercing to string."
            )

        output = core.pd_series_as_str_list(df, "output", fillna="None")
        ref = core.pd_series_as_str_list(df, reference_col, fillna="None")

        return list(base_metric(output, ref))

    def _wrap3(
        df: pd.DataFrame,
        base_metric: Callable[
            [Sequence[str], Sequence[str], Sequence[str]], Sequence[float]
        ],
    ):
        if df[["output", "groundTruth", "input"]].isnull().any().any():  # type: ignore[pandas]
            logger.warning(
                "None values found in the input data. Check your 'output', 'groundTruth', and 'input' columns. Coercing to string."
            )
        output = core.pd_series_as_str_list(df, "output", fillna="None")
        ground_truth = core.pd_series_as_str_list(
            df, "groundTruth", fillna="None"
        )
        inputs = core.pd_series_as_str_list(df, "input", fillna="None")
        return list(base_metric(output, ground_truth, inputs))

    unary_metrics = {
        "toxicity": text_metrics.calculate_toxicity_score,
        "sentiment": text_metrics.calculate_custom_llm_metric_example_sentiment,
    }

    binary_metrics_gt = {
        "bleu": text_metrics.calculate_bleu_score,
        "rouge1": text_metrics.calculate_rouge1_score,
        # TODO(b7r6): summarization is probably not useful for RAG, remove it for now.
        # It's also not easy to fit into the (output, GT, input) framework.
        # "summarization": text_metrics.calculate_summarization_score,
        "similarity": text_metrics.calculate_custom_llm_metric_example_semantic_similarity,
        "exact_match": text_metrics.calculate_exact_match_score,
    }
    binary_metrics_input = {
        "relevance": text_metrics.calculate_relevance_score,
    }
    ternary_metrics = {
        "faithfulness": partial(
            text_metrics.calculate_faithfulness_score,
            lastmile_api_token=lastmile_api_token,
        ),
        "qa": text_metrics.calculate_qa_score,
        "human_vs_ai": text_metrics.calculate_human_vs_ai_score,
    }

    wrap_unary: dict[str, Evaluator] = {
        name: partial(_wrap1, base_metric=base_metric)
        for name, base_metric in unary_metrics.items()
    }

    wrap_binary_gt: dict[str, Evaluator] = {
        name: partial(_wrap2, base_metric=base_metric)
        for name, base_metric in binary_metrics_gt.items()
    }

    wrap_binary_input: dict[str, Evaluator] = {
        name: partial(_wrap2, base_metric=base_metric, reference_col="input")
        for name, base_metric in binary_metrics_input.items()
    }

    wrap_ternary: dict[str, Evaluator] = {
        name: partial(_wrap3, base_metric=base_metric)
        for name, base_metric in ternary_metrics.items()
    }

    all_wrappers = {
        **wrap_unary,
        **wrap_binary_gt,
        **wrap_binary_input,
        **wrap_ternary,
    }
    return {name: all_wrappers[name] for name in names}


def _convert_df_example_set_to_input_set(
    df: core.DFExampleSet,
) -> Res[core.DFInputSet]:
    renamed = df.dropna(axis=1, how="all").rename(  # type: ignore[pandas]
        columns={
            "exampleId": "inputId",
            "exampleSetId": "InputSetID",
            "exampleSetName": "querySetName",
        }
    )

    return core.df_as_df_input_set(renamed)


def run_and_evaluate_helper(
    base_url: BaseURL,
    project_id: Optional[ProjectID],
    run_query_with_tracer_fn: RunTraceFunction,
    all_typed_evaluators: tuple[
        list[core.RAGQueryExampleLevelEvaluator],
        list[core.DatasetLevelEvaluator],
    ],
    save_options: SaveOptions,
    n_trials: int,
    lastmile_api_token: APIToken,
    test_dataset_id: Optional[core.InputSetID] = None,
    inputs: Optional[list[str]] = None,
    ground_truths: Optional[list[str]] = None,
) -> Res[EvaluationResult]:
    # TODO: Idk whether we want to use input or query set, whatever is more convenient
    def _get_input_set_as_lists(
        test_dataset_id: Optional[core.InputSetID],
        input_list: Optional[list[str]],
        ground_truth_list: Optional[list[str]],
    ) -> Res[tuple[list[str], Optional[list[str]]]]:
        """OUT: (input_list, ground_truth_list)"""
        if input_list is None and ground_truth_list is not None:
            return Err(
                ValueError("ground_truths given but no input queries given.")
            )

        # Now, if input list is None, so is ground_truth_list
        if input_list is None and test_dataset_id is not None:
            # This conversion is deliberate. Since we're representing both
            # with example sets (which are actually test sets in the backend),
            # we can treat a test_dataset_id as an example_set_id for
            # downloading purposes.
            example_set_id = core.ExampleSetID(test_dataset_id)

            df_input_set_downloaded = download_example_set_helper(
                BaseURL(base_url),
                APIToken(lastmile_api_token),
                project_id,
                example_set_id,
            )
            return df_input_set_downloaded.and_then(
                _get_input_and_ground_truth
            )

        if test_dataset_id is None and input_list is not None:
            return Ok((input_list, ground_truth_list))

        return Err(
            ValueError(
                "Exactly one of (test_dataset_id, inputs) must be provided."
            )
        )

    def _replicate_input_and_gt_lists(
        input_and_gt_lists: tuple[list[str], Optional[list[str]]],
        n_trials: int,
    ) -> tuple[list[str], Optional[list[str]]]:
        inputs, gt = input_and_gt_lists
        if gt is None:
            return inputs * n_trials, None
        return inputs * n_trials, gt * n_trials

    input_and_gt_lists = _get_input_set_as_lists(
        test_dataset_id, inputs, ground_truths
    ).map(partial(_replicate_input_and_gt_lists, n_trials=n_trials))

    outputs = result.do(
        run_rag_query_fn_helper(
            run_query_with_tracer_fn, input_and_gt_lists_ok[0]
        )
        for input_and_gt_lists_ok in input_and_gt_lists
    )

    create_example_set_result = result.do(
        _create_example_set_from_inputs_and_outputs(
            base_url,
            project_id,
            lastmile_api_token,
            inputs=input_and_gt_lists_ok[0],
            outputs_with_trace_ids=outputs_ok,
            example_set_name=save_options.name,
            ground_truth=input_and_gt_lists_ok[1],
        )
        for input_and_gt_lists_ok in input_and_gt_lists
        for outputs_ok in outputs
    )

    outcome = result.do(
        _run_and_store_evaluations_helper(
            base_url,
            APIToken(lastmile_api_token),
            core.ExampleSetID(create_example_set_result_ok.id),
            save_options.name,
            project_id,
            all_typed_evaluators[0],
            all_typed_evaluators[1],
        )
        for create_example_set_result_ok in create_example_set_result
    )

    return outcome


def get_test_dataset_helper(
    base_url: BaseURL,
    project_id: Optional[ProjectID],
    test_set_id: Optional[core.InputSetID],
    test_set_name: Optional[str],
    lastmile_api_token: str,
) -> Res[core.DFInputSet]:
    example_set_id = (
        core.ExampleSetID(test_set_id) if test_set_id is not None else None
    )

    raw = download_example_set_helper(
        BaseURL(base_url),
        APIToken(lastmile_api_token),
        project_id,
        example_set_id,
        test_set_name,
    )

    def _clean_and_cast_to_input_set(df: core.DFInputSet) -> core.DFInputSet:
        return cast(core.DFInputSet, clean_rag_query_tracelike_df(df))

    return raw.and_then(_convert_df_example_set_to_input_set).map(
        _clean_and_cast_to_input_set
    )


def create_example_set_helper(
    base_url: BaseURL,
    project_id: Optional[ProjectID],
    df: pd.DataFrame,
    example_set_name: Optional[str],
    ground_truths: Optional[list[str]],
    lastmile_api_token: APIToken,
) -> Res[CreateExampleSetResponse]:
    if ground_truths is not None:
        if "groundTruth" in df.columns:
            raise ValueError(
                "`ground_truth` column was given, but the groundTruth column is already present in the DataFrame."
            )
        df["groundTruth"] = ground_truths
    outcome = result.do(
        _create_example_set_from_df(
            base_url,
            project_id,
            lastmile_api_token,
            df_ok,
            TestSetType.EXAMPLE_SET,
            example_set_name,
        )
        for df_ok in core.df_as_df_minimal_example_set(df)
    )
    return outcome


def _download_or_convert_to_example_set(
    example_set_id: Optional[core.ExampleSetID],
    examples_dataframe: Optional[pd.DataFrame],
    project_id: Optional[ProjectID],
    base_url: BaseURL,
    lastmile_api_token: APIToken,
) -> Res[core.DFExampleSet]:
    if example_set_id is not None and examples_dataframe is None:
        return download_example_set_helper(
            base_url,
            lastmile_api_token,
            project_id,
            example_set_id,
        )

    if example_set_id is None and examples_dataframe is not None:
        return core.df_as_df_example_set(examples_dataframe)

    return Err(
        ValueError(
            "Exactly one of example_set_id, examples_dataframe must be provided."
        )
    )


def evaluate_helper(
    base_url: BaseURL,
    project_id: Optional[ProjectID],
    test_dataset_id: Optional[core.ExampleSetID],
    test_dataset: Optional[pd.DataFrame],
    lastmile_api_token: APIToken,
    save_options: SaveOptions,
    all_typed_evaluators: tuple[
        list[core.RAGQueryExampleLevelEvaluator],
        list[core.DatasetLevelEvaluator],
    ],
) -> Res[EvaluationResult]:
    if save_options.save:
        example_set_id_ = _create_or_get_example_set(
            test_dataset_id,
            test_dataset,
            base_url,
            project_id,
            lastmile_api_token,
            save_options.name,
        )

        outcome = result.do(
            _run_and_store_evaluations_helper(
                base_url,
                APIToken(lastmile_api_token),
                core.ExampleSetID(example_set_id_ok_),
                save_options.name,
                project_id,
                all_typed_evaluators[0],
                all_typed_evaluators[1],
            )
            for example_set_id_ok_ in example_set_id_
        )

        return outcome

    # save_options.save is False
    df_examples = _download_or_convert_to_example_set(
        test_dataset_id,
        test_dataset,
        project_id,
        base_url,
        lastmile_api_token,
    )

    dfs_metrics = result.do(
        _run_evaluations_helper(
            df_examples_ok,
            all_typed_evaluators[0],
            all_typed_evaluators[1],
        )
        for df_examples_ok in df_examples
    )

    return result.do(
        Ok(
            EvaluationResult(
                evaluation_result_id=None,
                test_dataset_id=(
                    core.InputSetID(test_dataset_id)
                    if test_dataset_id is not None
                    else None
                ),
                evaluator_metrics_df=dfs_metrics_ok[0],
                aggregated_metrics=dfs_metrics_ok[1],
            )
        )
        for dfs_metrics_ok in dfs_metrics
    )
