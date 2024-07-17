"""Interface for defining the methods for adding rag-specific events"""

import abc
import json
from dataclasses import asdict
from typing import Any, Optional, TYPE_CHECKING, Union
from enum import Enum

from opentelemetry.trace.span import Span

from ..common.types import (
    Chunk,
    RetrievedChunk,
    # TODO (delete)
    TextEmbedding,
)
from ..common import core

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


class RAGEventType(str, Enum):
    """
    Enum to define the type of RAG event that is being added.

    Subclassing as str is required for Enum to be JSON serialiazation compliant
    see: https://stackoverflow.com/questions/65339635/how-to-deserialise-enumeration-with-string-representation
    """

    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    MULTI_EMBEDDING = "multi_embedding"
    PROMPT_COMPOSITION = "prompt_composition"
    QUERY = "query"
    RERANKING = "reranking"
    RETRIEVAL = "retrieval"
    SUB_QUESTION = "sub_question"
    SYNTHESIZE = "synthesize"
    TEMPLATING = "templating"
    TOOL_CALL = "tool_call"
    CUSTOM = "custom"


# TODO: Add exception handling events
class AddRagEventInterface(abc.ABC):
    """
    Interface for defining the rag-specific events. Each rag-specific event calls
    into `log_span_event()` to add the event for a span.

    The method `log_span_event()` needs to be implemented by whichever
    class implements this interface (Python does not have interfaces so this
    is done through a child class inheriting AddRagEventInterface).
    """

    def log_query_event(
        self,
        query: str,
        response: str | list[str],
        system_prompt: Optional[str] = None,
        span: Optional[Span] = None,
        metadata: Optional[dict[str, Any]] = None,
        name: Optional[str] = None,
    ):
        """
        Log an event for querying an LLM.

        query: The input query
        response: Response from the LLM
        system_prompt: The system prompt defining the overall LLM behavior.
        span: The span to record the event for
            Defaults to opentelemetry.trace.get_current_span()
        metadata: Use metadata to store other information such as embedding model, etc.
        name: Optional name for the event.
        """
        if system_prompt is not None:
            if metadata is None:
                metadata = {}
            metadata["system_prompt"] = system_prompt
        self.log_span_event(
            name=name or RAGEventType.QUERY,
            input=query,
            output=response,  # TODO(rossdan): Make it str only to make everything else easier
            span=span,
            event_data=metadata,
            event_kind=RAGEventType.QUERY,
        )

    def log_chunking_event(
        self,
        output_chunks: list[Chunk],
        input_filepath: Optional[str] = None,
        span: Optional[Span] = None,
        metadata: Optional[dict[str, Any]] = None,
        name: Optional[str] = None,
    ):
        """
        Log an event for the chunking step of document ingestion.

        output_chunks: List of chunks produced, represented as a dictionary.
        input_filepath: The path to the file that was chunked
        span: The span to record the event for
            Defaults to opentelemetry.trace.get_current_span()
        metadata: Use metadata to store other information such as chunk size, mime type, file metadata, etc.
        name: Optional name for the event.
        """
        input_text: str = ""
        if input_filepath:
            input_text = input_filepath

        output_nodes_serialized = json.dumps(list(map(asdict, output_chunks)))
        self.log_span_event(
            name=name or RAGEventType.CHUNKING,
            input=input_text,
            output=output_nodes_serialized,
            span=span,
            event_data=metadata,
            event_kind=RAGEventType.CHUNKING,
        )

    def log_embedding_event(
        self,
        embeddings: list[TextEmbedding],
        rounding_decimal_places: int = 4,
        span: Optional[Span] = None,
        metadata: Optional[dict[str, Any]] = None,
        name: Optional[str] = None,
    ):
        """
        Log an event for embedding generation, either during document ingestion or query retrieval.

        embeddings: The list of embeddings created.
        rounding_decimal_places: The number of decimal places to round
            each float value in the embedding vectors to. We need to do this
            because OpenTelemetry doesn't support nested lists in span
            attributes, so we need to convert the nested list of embeddings
            to a json string. However, for floats with long decimal places,
            this can cause the string to be too large for OpenTelemetry to
            handle (floats are 64-bit, strings are 8-bit per char) and fail
            with a "413 Request Entity Too Large" error.
        span: The span to record the event for
            Defaults to opentelemetry.trace.get_current_span()
        metadata: Use metadata to store other information such as embedding model, etc.
        name: Optional name for the event.
        """
        if len(embeddings) == 0:
            print("No embeddings to log")
            return

        if len(embeddings) == 1:
            self.log_span_event(
                name=name or RAGEventType.EMBEDDING,
                input=embeddings[0].text,
                output=embeddings[0].vector,
                span=span,
                event_data=metadata,
                event_kind=RAGEventType.EMBEDDING,
            )
            return

        # Multi-embedding event
        clipped_vectors: list[list[float]] = [
            [round(j, rounding_decimal_places) for j in i.vector]
            for i in embeddings
        ]
        self.log_span_event(
            name=name or RAGEventType.MULTI_EMBEDDING,
            input=[embedding.text for embedding in embeddings],
            # Span attributes can only be primitives or lists of primitives
            # clipped_vectors are in list[list[float]] format so we need to
            # dump to str
            output=json.dumps(clipped_vectors),
            span=span,
            event_data=metadata,
            event_kind=RAGEventType.MULTI_EMBEDDING,
        )

    def log_prompt_composition_event(
        self,
        resolved_prompt: str,
        span: Optional[Span] = None,
        metadata: Optional[dict[str, Any]] = None,
        name: Optional[str] = None,
    ):
        """
        Log an event for creating a prompt.

        resolved_prompt: The final resolved query or prompt.
        span: The span to record the event for
            Defaults to opentelemetry.trace.get_current_span()
        metadata: Use metadata to store other information such as embedding model, etc.
        name: Optional name for the event.
        """
        self.log_span_event(
            name=name or RAGEventType.PROMPT_COMPOSITION,
            input="",
            output=resolved_prompt,
            span=span,
            event_data=metadata,
            event_kind=RAGEventType.PROMPT_COMPOSITION,
        )

    def log_query_rewrite_event(
        self,
        query: str,
        rewritten_query: list[str],
        span: Optional[Span] = None,
        metadata: Optional[dict[str, Any]] = None,
        name: Optional[str] = None,
    ):
        """
        Log an event for query rewriting, such as decomposing an incoming query into sub-queries.

        query: The input query
        rewritten_query: The rewritten query (or queries in some instances).
        span: The span to record the event for
            Defaults to opentelemetry.trace.get_current_span()
        metadata: Use metadata to store other information such as embedding model, etc.
        name: Optional name for the event.
        """
        self.log_span_event(
            name=name or RAGEventType.SUB_QUESTION,
            input=query,
            output=rewritten_query,
            span=span,
            event_data=metadata,
            event_kind=RAGEventType.SUB_QUESTION,
        )

    def log_retrieval_event(
        self,
        query: str,
        retrieved_data: list[RetrievedChunk],
        span: Optional[Span] = None,
        metadata: Optional[dict[str, Any]] = None,
        name: Optional[str] = None,
    ):
        """
        Log an event for the vector DB lookup for a query.

        query: The string used to retrieve data from the vector store.
        retrieved_data: The data retrieved from the DB.
        span: The span to record the event for
            Defaults to opentelemetry.trace.get_current_span()
        metadata: Use metadata to store other information such as reranker model, etc.
        name: Optional name for the event.
        """
        retrieved_nodes_serialized = json.dumps(
            list(map(asdict, retrieved_data))
        )
        self.log_span_event(
            name=name or RAGEventType.RETRIEVAL,
            input=query,
            output=retrieved_nodes_serialized,
            span=span,
            event_data=metadata,
            event_kind=RAGEventType.RETRIEVAL,
        )

    def log_rerank_event(
        self,
        retrieved: list[RetrievedChunk],
        reranked: list[RetrievedChunk],
        span: Optional[Span] = None,
        metadata: Optional[dict[str, Any]] = None,
        name: Optional[str] = None,
    ):
        """
        Log an event for the reranking of retrieved data.

        retrieved: The list of chunks that were retrieved.
        reranked: The reranked list of chunks (in order).
        span: The span to record the event for
            Defaults to opentelemetry.trace.get_current_span()
        metadata: Use metadata to store other information such as embedding model, etc.
        name: Optional name for the event.
        """
        retrieved_as_dict = list(map(lambda chunk: asdict(chunk), retrieved))
        rereanked_as_dict = list(map(lambda chunk: asdict(chunk), reranked))
        self.log_span_event(
            name=name or RAGEventType.RERANKING,
            # TODO: Fix dict issue with span events
            input=retrieved_as_dict,
            output=rereanked_as_dict,
            span=span,
            event_data=metadata,
            event_kind=RAGEventType.RERANKING,
        )

    def log_template_event(
        self,
        prompt_template: str,
        resolved_prompt: str,
        system_prompt: Optional[str] = None,
        span: Optional[Span] = None,
        metadata: Optional[dict[str, Any]] = None,
        name: Optional[str] = None,
    ):
        """
        Log an event for resolving a query or prompt template with dynamic string values.

        prompt_template: The prompt template without any of the resolved string values.
        resolved_prompt: The final resolved query or prompt.
        system_prompt: The system prompt defining the overall LLM behavior.
        span: The span to record the event for
            Defaults to opentelemetry.trace.get_current_span()
        metadata: Use metadata to store other information such as embedding model, etc.
        name: Optional name for the event.
        """
        if system_prompt is not None:
            if metadata is None:
                metadata = {}
            metadata["system_prompt"] = system_prompt
        self.log_span_event(
            name=name or RAGEventType.TEMPLATING,
            input=prompt_template,
            output=resolved_prompt,
            span=span,
            event_data=metadata,
            event_kind=RAGEventType.TEMPLATING,
        )

    def log_tool_call_event(
        self,
        query: str,
        tool_name: str,
        # TODO: Result and value of tool_arguments can't actually be Any,
        # it must be JSON-serializable
        tool_arguments: Optional[dict[str, Any]] = None,
        span: Optional[Span] = None,
        metadata: Optional[dict[str, Any]] = None,
        name: Optional[str] = None,
    ):
        """
        Use this to keep track of how the LLM chooses what tool to use based on user query.
        This does NOT include invoking the tool itself to get an answer
        to the query (use `log_query_event()` for that).

        query: The query used to determine with tool to use
        tool_name: The name of the tool.
        tool_arguments: The arguments for invoking the tool.
        span: The span to record the event for
            Defaults to opentelemetry.trace.get_current_span()
        metadata: Use metadata to store other information such as embedding model, etc.
        name: Optional name for the event.
        """
        tool_data = {"tool_name": tool_name}
        if tool_arguments:
            tool_data["tool_arguments"] = tool_arguments
        self.log_span_event(
            name=name or RAGEventType.TOOL_CALL,
            input=query,
            output=json.dumps(tool_data),
            span=span,
            event_data=metadata,
            event_kind=RAGEventType.TOOL_CALL,
        )

    def log_synthesize_event(
        self,
        input: Any,
        output: Any,
        span: Optional[Span] = None,
        metadata: Optional[dict[str, Any]] = None,
        name: Optional[str] = None,
    ):
        """
        Use this as a catch-all to summarize the input and output of several
        nested events.

        input: Input data of the entire sub-process
        output: Output data of the entire sub-process
        span: The span to record the event for
            Defaults to opentelemetry.trace.get_current_span()
        metadata: Use metadata to store other information such as embedding model, etc.
        name: Optional name for the event.
        """
        self.log_span_event(
            name=name or RAGEventType.SYNTHESIZE,
            # TODO: Fix dict issue for span data
            input=input,
            output=output,
            span=span,
            event_data=metadata,
            event_kind=RAGEventType.SYNTHESIZE,
        )

    @abc.abstractmethod
    def log_span_event(
        self,
        # TODO: Have better typing for JSON for input, output, event_data
        input: core.JSON = None,
        output: core.JSON = None,
        span: Optional[Span] = None,
        event_data: Optional[Union[core.JSON, "DataclassInstance"]] = None,
        event_kind: RAGEventType = RAGEventType.CUSTOM,
        name: Optional[str] = None,
    ) -> None:
        """
        Log an event tracking the input, output and JSON-serializable event data for an individual span.
        There can only be one RAG Event for the span, meant to capture the input and output of the span.

        You can use the data recorded in the event to generate test cases and run evaluations.

        input: The input to record.
        output: The output to record.
        span: The span to record the event for
            Defaults to opentelemetry.trace.get_current_span()
        event_data: JSON-serializable event data capturing any other metadata to save as part of the event.
        event_kind: The kind of event (e.g. "reranking", "tool_call", etc.).
            If this is a well-defined event kind, it will be rendered in an event-specific way in the UI.
        name: A name to give the event, if needed.
            Useful to disambiguate multiple of the same kind of event.
        """

    @abc.abstractmethod
    def log_trace_event(
        self,
        input: core.JSON = None,
        output: core.JSON = None,
        event_data: Optional[
            Union[core.JSONObject, "DataclassInstance"]
        ] = None,
    ) -> None:
        """
        Log an event tracking the input, output and JSON-serializable event data for the trace.
        There can only be one RAG Event at the trace level, meant to capture the input and output of the entire flow.

        You can use the data recorded in the event to generate test cases and run evaluations.

        Args:
            input (Optional[Dict[str, Any]]): The input to the RAG application. It should be a JSON-serializable dictionary.
                Defaults to None.
            output (Optional[Dict[str, Any]]): The output produced by the RAG application. It should be a JSON-serializable dictionary.
                Defaults to None.
            event_data (Optional[Dict[str, Any]]): Additional JSON-serializable event data capturing any other metadata to save as part of the event.
                Defaults to None.

        Returns:
            None
        """
