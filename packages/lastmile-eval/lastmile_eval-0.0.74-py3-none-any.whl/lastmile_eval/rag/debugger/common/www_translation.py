from typing import Sequence

import lastmile_utils.lib.core.api as core_utils
import pandas as pd


def to_records(df: pd.DataFrame) -> core_utils.JSONList:
    records: core_utils.JSONList = df.to_dict(orient="records")  # type: ignore[pandas]
    return records


def df_evaluation_metrics_to_records(
    df: pd.DataFrame,
) -> Sequence[core_utils.JSONValue]:
    renamed = df.rename(
        columns={
            "value": "metricValue",
            "exampleId": "testCaseId",
        }
    )

    dropped = renamed.drop(  # type: ignore[pandas]
        columns=["exampleSetId"]
    ).dropna()

    return to_records(dropped)
