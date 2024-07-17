import collections.abc
import logging
import os
import traceback as tb
from typing import (
    Any,
    Callable,
    NewType,
    Optional,
    Protocol,
    Sequence,
    TypeVar,
)

import lastmile_utils.lib.core.api as core_utils
import numpy as np
import pandas as pd
from result import Err, Ok, Result

from lastmile_eval.rag.debugger.common.utils import load_dotenv_from_cwd
from lastmile_eval.rag.debugger.common.types import APIToken, Res, T_Inv

# from lastmile_eval.rag.debugger.tracing.sdk import LastMileTracer

# Trace Data
OTelTraceID = NewType("OTelTraceID", str)

NamePrefix = NewType("NamePrefix", str)

ParamInfoKey = NewType("ParamInfoKey", str)
RAGQueryTraceID = NewType("RAGQueryTraceID", str)

ExampleSetID = NewType("ExampleSetID", str)
InputSetID = NewType("InputSetID", str)
TestSetID = NewType("TestSetID", str)
EvaluationResultId = NewType("EvaluationResultId", str)
MetricName = NewType("MetricName", str)

# specialized container types
DFRAGQueryTrace = NewType("DFRAGQueryTrace", pd.DataFrame)
DFRAGEvent = NewType("DFRAGEvent", pd.DataFrame)

DFRAGTracelike = DFRAGQueryTrace | DFRAGEvent
T_RAGTracelike = TypeVar(
    "T_RAGTracelike", bound=DFRAGTracelike, covariant=True
)

# TODO(b7r6) figure out why this alias doesn't work
# if put inside core_utils.
JSONObject = core_utils.JSONDict
JSON = Optional[core_utils.JSONValue]


"""


DFRAGQueryTrace must have
    
    | ragQueryTraceId | input | output | eventName | eventData | indexingTraceId (?) |


DFRagEvent: TODO(b7r6)

    | ragEventId | input | output | eventName | eventData | traceId | spanId | ragQueryTraceId (?) | ragIngestionTraceId (?) |

    
DFExampleSet must have:

    Either (input, output) pair must be provided, or eventData must be 
    provided. It is ok for both to be provided.
    | exampleSetId | exampleId | input | output | eventData (?) | groundTruth | ragQueryTraceId (?) | traceId (?) |

    
DFMinimalExampleSet must have:
    (this is the minimal schema from which an ExampleSet can be created.
    It is the same as DFExampleSet but without the stuff Postgres creates automatically;
    just the columns the user needs to provide).
    
    Either (input, output) pair must be provided, or eventData must be 
    provided. It is ok for both to be provided.

    | input (?) | output (?) | eventData (?) | groundTruth | ragQueryTraceId (?) | traceId (?) |


DFInputSet:

    | InputSetID | inputId | input | groundTruth |


Evaluator executes on (DFExampleSet) --> float
    that float becomes the `value` col in DFRAGQueryExampleEvaluations

DFRAGQueryExampleEvaluations must have:
    | exampleSetId | exampleId | metricName | value | ragQueryTraceId (?) |

DFRAGQueryDatasetEvaluations must have
        
    | exampleSetId | metricName | value |

"""

DFExampleSet = NewType("DFExampleSet", pd.DataFrame)
DFMinimalExampleSet = NewType("DFMinimalExampleSet", pd.DataFrame)
DFInputSet = NewType("DFInputSet", pd.DataFrame)
DFRAGQueryExampleEvaluations = NewType(
    "DFRAGQueryExampleEvaluations", pd.DataFrame
)
DFRAGQueryDatasetEvaluations = NewType(
    "DFRAGQueryDatasetEvaluations", pd.DataFrame
)


logger = logging.getLogger(__name__)

# TODO(jll): unhardcode format
logging.basicConfig(level=logging.DEBUG, format=core_utils.LOGGER_FMT)


class RAGQueryExampleLevelEvaluator(Protocol):
    def __call__(self, df: DFExampleSet) -> DFRAGQueryExampleEvaluations: ...


class DatasetLevelEvaluator(Protocol):
    def __call__(self, df: DFExampleSet) -> DFRAGQueryDatasetEvaluations: ...


def exception_info(e: Exception) -> str:
    traceback = tb.format_exception(e)
    return "\n".join(traceback)


def df_as_df_rag_query_trace(df: pd.DataFrame) -> Res[DFRAGQueryTrace]:
    if "ragQueryTraceId" not in df.columns:
        return Err(
            ValueError("DataFrame must have a 'ragQueryTraceId' column")
        )

    if "ragQueryTraceId" not in df.columns or (not df.set_index("ragQueryTraceId").index.is_unique):  # type: ignore
        return Err(
            ValueError(
                "ragQueryTraceId is a key column. All values for this column must be unique"
            )
        )
    return Ok(DFRAGQueryTrace(df))


def df_as_df_rag_events(df: pd.DataFrame) -> Res[DFRAGEvent]:
    # TODO(b7r6) check for required columns
    return Ok(DFRAGEvent(df))


def df_as_df_example_set(df: pd.DataFrame) -> Res[DFExampleSet]:
    if "exampleSetId" not in df.columns:
        return Err(ValueError("DataFrame must have a 'exampleSetId' column"))

    df_min = df_as_df_minimal_example_set(df)

    # This type conversion is safe because we checked all the conditions
    # earlier in this function.
    out = df_min.map(DFExampleSet)
    return out


def df_as_df_input_set(df: pd.DataFrame) -> Res[DFInputSet]:
    if "InputSetID" not in df.columns:
        return Err(ValueError("DataFrame must have a 'InputSetID' column"))

    if "inputId" not in df.columns or (not df.set_index("inputId").index.is_unique):  # type: ignore
        return Err(
            ValueError(
                "'inputId' is a key column. All values for this column must be unique"
            )
        )

    return Ok(DFInputSet(df))


def df_as_df_minimal_example_set(df: pd.DataFrame) -> Res[DFMinimalExampleSet]:
    required_to_is_nullable = {"input": False}
    for required_col, is_nullable in required_to_is_nullable.items():
        if required_col not in df.columns:
            return Err(
                ValueError(f"DataFrame must have a '{required_col}' column")
            )
        any_null = df[required_col].isnull().any().any()  # type: ignore
        if not is_nullable and any_null:
            return Err(
                ValueError(
                    f"'{required_col}' column must not have null values"
                )
            )

    if "exampleId" in df.columns:
        if df.set_index("exampleId").index.is_unique:  # type: ignore
            return Ok(DFMinimalExampleSet(df))
        return Err(
            ValueError(
                "'exampleId' is a key column. All values for this column must be unique"
            )
        )
    return Ok(DFMinimalExampleSet(df))


def df_as_df_trace_evaluations(
    df: pd.DataFrame,
) -> DFRAGQueryExampleEvaluations:
    if any(
        col not in df.columns
        for col in ["exampleSetId", "exampleId", "metricName", "value"]
    ):
        raise ValueError(
            "DataFrame must have 'exampleSetId', 'traceId', 'metricName', and 'value' columns"
        )
    if not df.set_index(["exampleSetId", "exampleId", "metricName"]).index.is_unique:  # type: ignore[fixme]
        raise ValueError(
            "DataFrame must have a composite key ('exampleSetId', 'traceId', 'metricName')"
        )
    return DFRAGQueryExampleEvaluations(df)


def df_as_df_dataset_evaluations(
    df: pd.DataFrame,
) -> DFRAGQueryDatasetEvaluations:
    if any(
        col not in df.columns
        for col in ["exampleSetId", "metricName", "value"]
    ):
        raise ValueError(
            "Dataset evaluations must have 'exampleSetId', 'metricName', and 'value' columns"
        )

    if any(col in df.columns for col in ["exampleId"]):
        raise ValueError("DataFrame must not have 'exampleId' column")

    if not df.set_index(["exampleSetId", "metricName"]).index.is_unique:  # type: ignore[fixme]
        raise ValueError(
            "DataFrame must have a composite key ('exampleSetId', 'metricName')"
        )
    return DFRAGQueryDatasetEvaluations(df)


def upcast_df_example_set(df: DFExampleSet) -> DFMinimalExampleSet:
    # If it's an example set, by definition it's also a minimal example set.
    # This is enforced at runtime inside `df_as_df_example_set()`.
    # TODO(b7r6) replace this type cast call with some mechanism
    # that pyright can treat as a super/subtype relationship automatically.
    return DFMinimalExampleSet(df)


def api_token_from_dot_env(key: str) -> str:
    load_dotenv_from_cwd()
    value = os.getenv(key)
    if value is None:
        raise ValueError(
            f"Environment variable '{key}' not found. Check your .env file."
        )

    return value


def token(lastmile_api_token: Optional[str]) -> APIToken:
    return (
        APIToken(lastmile_api_token)
        if lastmile_api_token is not None
        else APIToken(api_token_from_dot_env("LASTMILE_API_TOKEN"))
    )


def _coerce_list_like(data: T_Inv) -> Result[list[float], str]:  # type: ignore[fixme]
    # TODO(jll) do this function better
    # ignoring T_inv error deliberately; see safe_run_function_as_trace_evaluator()
    # for more info.
    if isinstance(data, collections.abc.Sequence):
        if all(isinstance(x, (int, float)) for x in data):  # type: ignore
            return Ok(list(data))  # type: ignore
    elif isinstance(data, pd.Series):
        if data.dtype in [int, float]:  # type: ignore
            return Ok(data.tolist())  # type: ignore

    return Err("Data must be list-like")


def safe_run_function_as_trace_evaluator(
    # Using T to make pyright warn us that the user might return something wrong.
    f: Callable[..., Any],  # deliberate `Any` for maximum compatibility.
    df: DFExampleSet,
) -> Sequence[float]:
    # TODO(jll): timeout, parallelize
    N = len(df)
    try:
        out = f(df)
        match _coerce_list_like(out):
            case Ok(values):
                return values
            case Err(e):
                logger.error(
                    f"Error running trace-level evaluator: {out}, {e}"
                )
                return [np.nan] * N

    except Exception as e:
        logger.error(
            f"Error running trace-level evaluator: {exception_info(e)}"
        )
        return [np.nan] * N


def safe_run_function_as_dataset_evaluator(
    f: Callable[..., Any],  # deliberate `Any` for maximum compatibility.
    df: DFExampleSet,
) -> float:
    # TODO(jll): timeout
    try:
        out = float(f(df))
        return out
    except Exception as e:
        logger.error(
            f"Error running dataset-level evaluator: {exception_info(e)}"
        )
        return np.nan


def callable_as_example_level_evaluator(
    metric_name: str,
    f: Callable[..., Any],  # deliberate `Any` for maximum compatibility.
) -> RAGQueryExampleLevelEvaluator:
    def _wrap(df: DFExampleSet) -> DFRAGQueryExampleEvaluations:
        values = safe_run_function_as_trace_evaluator(f, df)
        N = len(values)
        df_out = pd.DataFrame(
            {
                "exampleSetId": df["exampleSetId"],
                "exampleId": df["exampleId"],
                "metricName": [metric_name] * N,
                "value": values,
            }
        )
        return df_as_df_trace_evaluations(df_out)

    return _wrap


def callable_as_aggregated_evaluator(
    metric_name: str,
    f: Callable[..., Any],  # deliberate `Any` for maximum compatibility.
) -> DatasetLevelEvaluator:
    def _wrap(df: DFExampleSet) -> DFRAGQueryDatasetEvaluations:
        value = safe_run_function_as_dataset_evaluator(f, df)

        # Currently, we stipulate that len(values) == 1,
        # i.e. only one exampleSetId can be evaluated at a time.
        example_set_ids = {
            s
            for s in pd_series_as_optional_str_list(df, "exampleSetId")
            if s is not None
        }
        if len(example_set_ids) > 1:  # type: ignore
            raise ValueError(
                "Dataset-level evaluators must return a single value per exampleSetId. "
                "Currently, only one test set can be evaluated at a time."
            )

        return df_as_df_dataset_evaluations(
            pd.DataFrame(
                {
                    "exampleSetId": list(example_set_ids),
                    # TODO (rossdan): Allow user to define optional name value for Aggregator (ex: "accuracy_mean", not just "accuracy")
                    "metricName": [metric_name],
                    "value": [value],
                }
            )
        )

    return _wrap


def pd_series_as_optional_str_list(
    df: pd.DataFrame, col: str
) -> list[Optional[str]]:
    series = df[col]  # type: ignore
    return series.astype(str).tolist()  # type: ignore[pandas]


def pd_series_as_str_list(
    df: pd.DataFrame, col: str, fillna: str
) -> list[str]:
    series = df[col]  # type: ignore
    return series.astype(str).fillna(fillna).tolist()  # type: ignore[pandas]
