import logging
from typing import Callable, Generator, Mapping, Optional, Sequence

import numpy as np
import pandas as pd
import result

from lastmile_eval.rag.debugger.common import core
from lastmile_eval.rag.debugger.common.types import (
    APIToken,
    BaseURL,
    CreatorID,
    OrganizationID,
    ProjectName,
    Res,
)
from lastmile_eval.rag.debugger.common.utils import (
    DEFAULT_PROJECT_NAME,
    get_project_id,
    load_project_name,
    WEBSITE_BASE_URL,
)

from ..offline_evaluation import evaluation_lib
from ..offline_evaluation.evaluation_lib import (
    BatchDownloadParams,
    BatchTraceDownloadParams,
    EvaluatorTuple,
    clean_rag_query_tracelike_df,
    wrap_with_tracer,
)

logger = logging.getLogger(__name__)
logging.basicConfig()


# TODO(b7r6): probably move these definitions to a common module
# that's accessible to both our code and user code
Evaluator = evaluation_lib.Evaluator
Aggregator = evaluation_lib.Aggregator
SaveOptions = evaluation_lib.SaveOptions


def get_traces(
    project_name: Optional[str] = None,
    trace_ids: Optional[str | list[str]] = None,
    take: Optional[int] = None,
    search_filter: Optional[str] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    lastmile_api_token: Optional[str] = None,
) -> Generator[pd.DataFrame, None, None]:
    """
    Download traces as a DataFrame.

    Args:
        project_name: The name of the project the traces were logged to. If not provided,
            will read from the LASTMILE_PROJECT_NAME environment variable. If that is not set,
            and no trace_ids are provided, will use the DEFAULT project.
        trace_ids: Optional filter by IDs
        take: Number of traces to download per request. The maximum is 50.
        search_filter: A substring search to match any property in the trace metadata.
        start_time: Start unix timestamp (GMT seconds) to filter traces >= start_time.
        end_time: End unix timestamp (GMT seconds) to filter traces <= end_time.
        lastmile_api_token: The API token for the LastMile API. If not provided,
            will try to get the token from the LASTMILE_API_TOKEN
            environment variable.
            You can create a token from the "API Tokens" section from this website:
            https://lastmileai.dev/settings?page=tokens

    Returns:
        A DataFrame containing the trace data.
    """
    base_url = WEBSITE_BASE_URL
    lastmile_api_token = core.token(lastmile_api_token)
    trace_project_name = (
        ProjectName(project_name)
        if project_name is not None
        else load_project_name()
    )

    project_id = get_project_id(
        project_name=trace_project_name or DEFAULT_PROJECT_NAME,
        lastmile_api_token=APIToken(lastmile_api_token),
        create_if_not_exists=False,
    )

    trace_ids_list = [trace_ids] if isinstance(trace_ids, str) else trace_ids
    if trace_ids_list is not None:
        trace_ids_list = [
            core.RAGQueryTraceID(trace_id) for trace_id in trace_ids_list
        ]

    download_params: Res[BatchTraceDownloadParams] = result.do(
        result.Ok(
            BatchTraceDownloadParams(
                project_id=project_id_ok,
                trace_ids=trace_ids_list,
                take=take,
                search_filter=search_filter,
                start_time=start_time,
                end_time=end_time,
            )
        )
        for project_id_ok in project_id
    )

    generator = result.do(
        evaluation_lib.download_rag_query_traces_helper(
            BaseURL(base_url),
            APIToken(lastmile_api_token),
            download_params_ok,
        )
        for download_params_ok in download_params
    )

    match (generator):
        case result.Ok(generator_ok):
            for batch in generator_ok:
                yield batch.map(clean_rag_query_tracelike_df).unwrap_or_raise(
                    ValueError
                )
        case result.Err(e):
            raise ValueError(e)


def download_rag_events(
    project_name: Optional[str] = None,
    batch_limit: Optional[int] = None,
    substring_filter: Optional[str] = None,
    creator_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    event_name: Optional[str] = None,
    lastmile_api_token: Optional[str] = None,
) -> Generator[pd.DataFrame, None, None]:
    HARD_BATCH_LIMIT = 50
    if batch_limit is None:
        batch_limit = HARD_BATCH_LIMIT

    if batch_limit < 1 or batch_limit > HARD_BATCH_LIMIT:
        raise ValueError(
            f"batch_limit must be between 1 and {HARD_BATCH_LIMIT}"
        )
    base_url = WEBSITE_BASE_URL
    lastmile_api_token = core.token(lastmile_api_token)
    project_id = (
        get_project_id(
            project_name=ProjectName(project_name),
            lastmile_api_token=APIToken(lastmile_api_token),
            create_if_not_exists=False,
        )
        if project_name is not None
        else result.Ok(None)
    )

    download_params: Res[BatchDownloadParams] = result.do(
        result.Ok(
            BatchDownloadParams(
                batch_limit=batch_limit,
                search=substring_filter,
                creator_id=(
                    CreatorID(creator_id) if creator_id is not None else None
                ),
                project_id=project_id_ok,
                organization_id=(
                    OrganizationID(organization_id)
                    if organization_id is not None
                    else None
                ),
                start_timestamp=start_time,
                end_timestamp=end_time,
                event_name=event_name,
            )
        )
        for project_id_ok in project_id
    )

    generator = result.do(
        evaluation_lib.download_rag_events_helper(
            BaseURL(base_url),
            APIToken(lastmile_api_token),
            download_params_ok,
        )
        for download_params_ok in download_params
    )

    match (generator):
        case result.Ok(generator_ok):
            for batch in generator_ok:
                yield batch.unwrap_or_raise(ValueError)
        case result.Err(e):
            raise ValueError(e)


def create_test_dataset(
    name: str,
    data: pd.DataFrame,
    project_name: Optional[str] = None,
    lastmile_api_token: Optional[str] = None,
) -> core.TestSetID:
    """
    Create a Test Set from the given data.

    name: Name to save the Test Set as.
    data: A DataFrame that should contain up to three columns: 'input', 'output', 'groundTruth'. The input column is *required* for every TestSet.
    project_name: The name of the project to save TestSet in.  If not provided, will read from the LASTMILE_PROJECT_ID environment variable.
        If that is not set, will use the DEFAULT project.
    lastmile_api_token: The API token for the LastMile API. If not provided,
        will try to get the token from the LASTMILE_API_TOKEN
        environment variable.
        You can create a token from the "API Tokens" section from this website:
        https://lastmileai.dev/settings?page=tokens
    """
    # TODO: Add tags to categorize the TestSet as. This can be used for filtering.
    base_url = WEBSITE_BASE_URL
    lastmile_api_token = core.token(lastmile_api_token)

    project_name = (
        ProjectName(project_name)
        if project_name is not None
        else load_project_name()
    )

    project_id = get_project_id(
        project_name=project_name or DEFAULT_PROJECT_NAME,
        lastmile_api_token=APIToken(lastmile_api_token),
        create_if_not_exists=True,
    )

    outcome = result.do(
        evaluation_lib.create_example_set_helper(
            base_url=BaseURL(base_url),
            project_id=project_id_ok,
            df=data,
            example_set_name=name,
            ground_truths=None,
            lastmile_api_token=APIToken(lastmile_api_token),
        )
        for project_id_ok in project_id
    )

    response = outcome.unwrap_or_raise(ValueError)
    return core.TestSetID(response.id)


def create_test_from_trace_data(
    name: str,
    trace_ids: Optional[str | list[str]] = None,
    take: Optional[int] = None,
    sampling_rate: Optional[float] = None,
    search_filter: Optional[str] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    project_name: Optional[str] = None,
    lastmile_api_token: Optional[str] = None,
) -> core.TestSetID:
    """
    Create a Test Set from the given data.

    name: Name to save the Test Set as.
    trace_ids: Optional filter by IDs
    take: Number of traces to download per request. The maximum is 50.
    sampling_rate: Sampling rate (between 0 and 1) to take a random sampling of the traces that match the criteria.
        If unspecified, the first `take` traces matching the criteria will be returned.
    search_filter: A substring search to match any property in the trace metadata.
    start_time: Start unix timestamp (GMT seconds) to filter traces >= start_time.
    end_time: End unix timestamp (GMT seconds) to filter traces <= end_time.
    tags: Optional tags to categorize the TestSet as. This can be used for filtering.
    project_name: The name of the project to save the TestSet in.
        If not provided, will read from the LASTMILE_PROJECT_ID environment variable.
        If that is not set, will use the DEFAULT project.
    lastmile_api_token: The API token for the LastMile API. If not provided,
        will try to get the token from the LASTMILE_API_TOKEN
        environment variable.
        You can create a token from the "API Tokens" section from this website:
        https://lastmileai.dev/settings?page=tokens

    """
    lastmile_api_token = core.token(lastmile_api_token)

    trace_generator = get_traces(
        project_name=project_name,
        trace_ids=trace_ids,
        take=min(take or 50, 50),
        search_filter=search_filter,
        start_time=start_time,
        end_time=end_time,
    )

    all_traces_df = pd.concat(trace_generator, ignore_index=True)

    if sampling_rate is not None:
        all_traces_df = all_traces_df.sample(frac=sampling_rate)

    def _create_dataset(df: core.DFMinimalExampleSet):
        # TODO: Add tags to create_test_dataset
        return create_test_dataset(name, df, project_name, lastmile_api_token)

    return (
        core.df_as_df_minimal_example_set(
            all_traces_df[["input", "output", "traceId"]]
        )
        .map(_create_dataset)
        .unwrap_or_raise(ValueError)
    )


def get_test_dataset(
    test_set_id: Optional[str] = None,
    test_set_name: Optional[str] = None,
    project_name: Optional[str] = None,
    lastmile_api_token: Optional[str] = None,
) -> pd.DataFrame:
    """
    Downloads the Test Set data containing input, and optionally output and groundTruth.

    test_set_id: The id of the Test Set to download.
        Do not use this if you are providing `test_set_name`.
    test_set_name: Name of the Test Set to download.
        Do not use this if you are providing `test_set_id`.
    project_name: The name of the project that this Test Set
        belongs to. It acts as an additional filter since
        the same `test_set_name` can exist in multiple projects.
        Do not use this if you are providing `test_set_id`.
        If not provided, will read from the LASTMILE_PROJECT_NAME environment variable.
        If that is not set, will use the DEFAULT project.
    lastmile_api_token: The API token for the LastMile API. If not provided,
        will try to get the token from the LASTMILE_API_TOKEN
        environment variable.
        You can create a token from the "API Tokens" section from this website:
        https://lastmileai.dev/settings?page=tokens
    """
    base_url = WEBSITE_BASE_URL
    lastmile_api_token = core.token(lastmile_api_token)

    project_id = (
        get_project_id(
            project_name=ProjectName(project_name),
            lastmile_api_token=APIToken(lastmile_api_token),
            create_if_not_exists=False,
        )
        if project_name is not None
        else result.Ok(None)
    )

    outcome = result.do(
        evaluation_lib.get_test_dataset_helper(
            base_url=BaseURL(base_url),
            project_id=project_id_ok,
            test_set_id=(
                core.InputSetID(test_set_id)
                if test_set_id is not None
                else None
            ),
            test_set_name=test_set_name,
            lastmile_api_token=lastmile_api_token,
        )
        for project_id_ok in project_id
    )

    return outcome.unwrap_or_raise(ValueError)


def run(
    run_fn: Callable[[str], str],
    inputs: Sequence[str] | pd.DataFrame,
    project_name: Optional[str] = None,
    lastmile_api_token: Optional[str] = None,
) -> pd.DataFrame:
    """
    Runs the input data using the run_fn, and returns the results in an 'output' column in a DataFrame..
    Importantly, this function wraps the run in a trace, so it can be tracked and evaluated easily.

    run_fn: The callable to invoke the execution flow.
    inputs: A DataFrame with an 'input' column, or a list of strings.
    project_name: The name of the project the evaluation result is saved in.
        If not provided, will read from the LASTMILE_PROJECT_NAME environment variable.
        If that is not set, will use the DEFAULT project.
    lastmile_api_token: The API token for the LastMile API. If not provided,
        will try to get the token from the LASTMILE_API_TOKEN
        environment variable.
        You can create a token from the "API Tokens" section from this website:
        https://lastmileai.dev/settings?page=tokens
    """

    run_query_with_tracer_fn = wrap_with_tracer(
        run_fn,
        project_name=project_name,
        lastmile_api_token=lastmile_api_token,
    )

    outputs_with_trace_ids = evaluation_lib.run_rag_query_fn_helper(
        run_query_with_tracer_fn, inputs
    )

    if isinstance(inputs, Sequence):
        inputs = pd.DataFrame(
            {
                "input": inputs,
            }
        )

    output_df: Res[pd.DataFrame] = result.do(
        result.Ok(
            inputs.assign(  # type: ignore[pandas]
                output=outputs_with_trace_ids_ok[0],
                traceId=outputs_with_trace_ids_ok[1],
            )
        )
        for outputs_with_trace_ids_ok in outputs_with_trace_ids
    )
    return output_df.unwrap_or_raise(ValueError)


def evaluate(
    evaluators: (
        Mapping[
            str,  # Name of the evaluation metric
            Evaluator
            | EvaluatorTuple,  # Tuple of Evaluator function and (optionally) Aggregator function
        ]
        | set[str]
    ),
    test_dataset_id: Optional[str] = None,
    test_dataset: Optional[pd.DataFrame] = None,
    project_name: Optional[str] = None,
    save_options: Optional[SaveOptions] = None,
    lastmile_api_token: Optional[str] = None,
) -> evaluation_lib.EvaluationResult:
    """
    Run evaluations on the provided data using chosen evaluation functions.

    evaluators: A mapping of evaluator names to evaluator functions. Each evaluator takes a DataFrame and produces one value per row.
        Example: {"exact_match": some_exact_match_checking_function}

    test_dataset_id: (Must be specified if `test_dataset` isn't provided)
        The id of the Test Set to run the evaluations on.
    test_dataset: (If `test_dataset_id` isn't specified)
        A DataFrame that should contain 'input', 'output' and optionally 'groundTruth' columns to run the evaluations on.
        NOTE: Some evaluators may need additional columns, such as 'context' (for hallucination eval, for example).
    project_name: The name of the project the evaluation result is saved in.
        If not provided, will read from the LASTMILE_PROJECT_NAME environment variable.
        If that is not set, will use the DEFAULT project.
    save_options: Controls options for storing the evaluation result in the DB.
        If a test_dataset is specified, by default that will also be saved as a Test Set.
    lastmile_api_token: The API token for the LastMile API. If not provided,
        will try to get the token from the LASTMILE_API_TOKEN
        environment variable.
        You can create a token from the "API Tokens" section from this website:
        https://lastmileai.dev/settings?page=tokens
    """

    base_url = BaseURL(WEBSITE_BASE_URL)
    lastmile_api_token = core.token(lastmile_api_token)

    project_id = (
        get_project_id(
            project_name=ProjectName(project_name),
            lastmile_api_token=APIToken(lastmile_api_token),
            create_if_not_exists=True,
        )
        if project_name is not None
        else result.Ok(None)
    )

    save_options_ = save_options or SaveOptions()

    all_typed_evaluators = (
        evaluation_lib.user_provided_evaluators_to_all_typed_evaluators(
            evaluators, lastmile_api_token
        )
    )

    outcome = result.do(
        evaluation_lib.evaluate_helper(
            base_url=base_url,
            project_id=project_id_ok,
            test_dataset_id=(
                core.ExampleSetID(test_dataset_id)
                if test_dataset_id is not None
                else None
            ),
            test_dataset=test_dataset,
            lastmile_api_token=lastmile_api_token,
            save_options=save_options_,
            all_typed_evaluators=all_typed_evaluators_ok,
        )
        for project_id_ok in project_id
        for all_typed_evaluators_ok in all_typed_evaluators
    )

    return outcome.unwrap_or_raise(ValueError)


# TODO: Figure out how to specify we want to inputs and outputs from eventData
# for evaluators instead of default "input" and "output" columns
# We can also for now just say we don't support running eval on eventData and
# we must have defined inputs. I think this is reasonable
def run_and_evaluate(
    run_fn: Callable[[str], str],
    evaluators: (
        Mapping[
            str,  # Name of the evaluation metric
            Evaluator
            | EvaluatorTuple,  # Tuple of Evaluator function and (optionally) Aggregator function
        ]
        | set[str]
    ),
    test_dataset_id: Optional[str] = None,
    # TODO (rossdan): Change inputs to test_dataset
    inputs: Optional[list[str]] = None,
    project_name: Optional[str] = None,
    save_options: Optional[SaveOptions] = None,
    n_trials: int = 1,
    lastmile_api_token: Optional[str] = None,
    # TODO (rossdan): Change ground_truths to test_dataset
    ground_truths: Optional[list[str]] = None,
) -> evaluation_lib.EvaluationResult:
    """
    Similar to evaluate, except this function runs the flow on the inputs defined in `test_dataset`
    and evaluates the result using the chosen evaluation functions.

    By default, each run saves a new Test Set in the DB that can be used to run future evaluations.

    run_fn: The callable to invoke the execution flow.
    evaluators: A mapping of evaluator names to evaluator functions. Each evaluator takes a DataFrame and produces one value per row.
        Example: {"exact_match": some_exact_match_checking_function}
    test_dataset_id: (Must be specified if `test_dataset` isn't provided)
        The id of the Test Set to run the evaluations on.
        NOTE: Even if the test cases contain outputs already, they will be re-run using the `run_fn` to generate new outputs.
    test_dataset: (If `test_dataset_id` isn't specified)
        A DataFrame that must contain 'input' column and optionally 'groundTruth' columns to run the evaluations on.
        NOTE: Even DataFrame contain an 'output' column already, any existing outputs will be re-run using the `run_fn` to generate new outputs.
        NOTE: Some evaluators may need additional columns, such as 'context' (for hallucination eval, for example).
    project_name: The name of the project the evaluation result is saved in.
        If not provided, will read from the LASTMILE_PROJECT_NAME environment variable.
        If that is not set, will use the DEFAULT project.
    save_options: Controls options for storing the evaluation result in the DB.
        If a test_dataset is specified, by default that will also be saved as a Test Set.
    lastmile_api_token: The API token for the LastMile API. If not provided,
        will try to get the token from the LASTMILE_API_TOKEN
        environment variable.
        You can create a token from the "API Tokens" section from this website:
        https://lastmileai.dev/settings?page=tokens
    """

    base_url = BaseURL(WEBSITE_BASE_URL)
    lastmile_api_token = core.token(lastmile_api_token)

    project_id = (
        get_project_id(
            project_name=ProjectName(project_name),
            lastmile_api_token=APIToken(lastmile_api_token),
            create_if_not_exists=True,
        )
        if project_name is not None
        else result.Ok(None)
    )

    save_options_ = save_options or SaveOptions()

    if not save_options_.save:
        raise ValueError(
            "save==False is currently not supported for `run_and_evaluate()`."
        )

    all_typed_evaluators = (
        evaluation_lib.user_provided_evaluators_to_all_typed_evaluators(
            evaluators, lastmile_api_token
        )
    )

    run_query_with_tracer_fn = wrap_with_tracer(
        run_fn,
        project_name=project_name,
        lastmile_api_token=lastmile_api_token,
    )

    outcome = result.do(
        evaluation_lib.run_and_evaluate_helper(
            base_url=base_url,
            project_id=project_id_ok,
            run_query_with_tracer_fn=run_query_with_tracer_fn,
            all_typed_evaluators=all_typed_evaluators_ok,
            save_options=save_options_,
            n_trials=n_trials,
            lastmile_api_token=lastmile_api_token,
            test_dataset_id=(
                core.InputSetID(test_dataset_id)
                if test_dataset_id is not None
                else None
            ),
            inputs=inputs,
            ground_truths=ground_truths,
        )
        for project_id_ok in project_id
        for all_typed_evaluators_ok in all_typed_evaluators
    )

    return outcome.unwrap_or_raise(ValueError)


def assert_is_close(
    evaluation_result: evaluation_lib.EvaluationResult,
    metric_name: str,
    value: float,
) -> None:
    df_metrics_agg = evaluation_result.aggregated_metrics
    metric = df_metrics_agg.set_index(["testSetId", "metricName"]).value.unstack("metricName")[metric_name].iloc[0]  # type: ignore[pandas]
    assert np.isclose(metric, value), f"Expected: {value}, Got: {metric}"  # type: ignore[fixme]


def get_default_evaluators() -> dict[
    str,
    str,
]:
    """
    Gets predefined evaluator names that come built in with the LastMile Eval SDK.
    You can choose whichever ones you want and define them as a set when
    using the `evaluate()` and `run_and_evaluate()` methods.

    Example:
    ```python
    from lastmile_eval.rag.debugger.api import evaluate

    def evaluate(
        ...
        evaluators={"toxicity", "exact_match", "bleu"},
        ...
    )
    ```
    """

    return evaluation_lib.get_default_evaluators_with_descriptions()
