"""
Utils file for defining types used in the tracing SDK
"""

from dataclasses import dataclass
from typing import (
    Any,
    NewType,
    Optional,
    ParamSpec,
    TypeVar,
)
from enum import Enum
from result import Result


T_ParamSpec = ParamSpec("T_ParamSpec")

APIToken = NewType("APIToken", str)
BaseURL = NewType("BaseURL", str)
ProjectID = NewType("ProjectID", str)
ProjectName = NewType("ProjectName", str)
CreatorID = NewType("CreatorID", str)
OrganizationID = NewType("OrganizationID", str)

T_cov = TypeVar("T_cov", covariant=True)
T_Inv = TypeVar("T_Inv")

Res = Result[T_cov, Exception]

# FYI: kw_only is needed due to position args with default values
# being delcared before non-default args. This is only supported on
# python 3.10 and above


@dataclass(kw_only=True)
class Chunk:
    """Chunk metadata"""

    id: str
    title: Optional[str] = None
    content: str
    extras: Optional[dict[str, Any]] = None


@dataclass
class RetrievedChunk(Chunk):
    """Retrieved chunk"""

    retrieval_score: (
        float  # Similarity score (e.g. cosine) for the retrieved chunk
    )


@dataclass(frozen=True)
class ParsedHTTPResponse:
    returned_id: str
    status_code: int
    text: str


@dataclass(kw_only=True)
class TextEmbedding:
    """Object used for storing text embedding info"""

    vector: list[float]
    id: Optional[str] = None
    title: Optional[str] = None
    text: Optional[str] = None
    extras: Optional[dict[str, Any]] = None


class RagFlowType(Enum):
    """
    Enum to define the type of flow that the RAG debugger is in.
    """

    INGESTION = "ingestion"
    QUERY = "query"
