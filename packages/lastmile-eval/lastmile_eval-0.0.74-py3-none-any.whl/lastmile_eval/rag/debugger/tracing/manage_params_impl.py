"""
Implementation of the manage_params_interface for defining the RAG-specific params.
"""

from typing import Any, Optional
from copy import deepcopy

from opentelemetry.trace import Span

from lastmile_eval.rag.debugger.api.tracing import LastMileTracer
from lastmile_eval.rag.debugger.api import ParamKey


class ManageParamsImpl(LastMileTracer):
    """
    Implementation of the OpinionatedParams interface for defining the RAG-specific events.
    """

    def register_document_preprocess_params(
        self,
        chunk_size: Optional[int] = None,
        chunk_strategy: Optional[str] = None,
        extras: Optional[dict[str | ParamKey, Any]] = None,
        span: Optional[Span] = None,
    ) -> None:
        """
        See `lastmile_eval.rag.debugger.api.ManageParamsInterface.register_document_preprocess_params()`
        """
        params: dict[str | ParamKey, Any] = {
            ParamKey.CHUNK_SIZE.value: chunk_size,
            ParamKey.CHUNK_STRATEGY.value: chunk_strategy,
        }
        params.update(extras or {})
        filtered_params = {k: v for k, v in params.items() if v is not None}
        self.register_params(
            params=filtered_params,
            span=span,
        )

    def register_embedding_params(
        self,
        embedding_model: Optional[str] = None,
        embedding_dimensions: Optional[int] = None,
        extras: Optional[dict[str | ParamKey, Any]] = None,
        span: Optional[Span] = None,
    ) -> None:
        """
        See `lastmile_eval.rag.debugger.api.ManageParamsInterface.register_embedding_params()`
        """
        params: dict[str | ParamKey, Any] = {
            ParamKey.EMBEDDING_MODEL.value: embedding_model,
            ParamKey.EMBEDDING_DIMENSIONS.value: embedding_dimensions,
        }
        params.update(extras or {})
        filtered_params = {k: v for k, v in params.items() if v is not None}
        self.register_params(
            params=filtered_params,
            span=span,
        )

    def register_query_processing_params(
        self,
        embedding_model: Optional[str] = None,
        embedding_dimensions: Optional[int] = None,
        decomposition_strategy: Optional[str] = None,
        extras: Optional[dict[str | ParamKey, Any]] = None,
        span: Optional[Span] = None,
    ) -> None:
        """
        See `lastmile_eval.rag.debugger.api.ManageParamsInterface.register_query_processing_params()`
        """
        params: dict[str | ParamKey, Any] = {
            ParamKey.EMBEDDING_MODEL.value: embedding_model,
            ParamKey.EMBEDDING_DIMENSIONS.value: embedding_dimensions,
            ParamKey.DECOMPOSITION_STRATEGY.value: decomposition_strategy,
        }
        params.update(extras or {})
        filtered_params = {k: v for k, v in params.items() if v is not None}
        self.register_params(
            params=filtered_params,
            span=span,
        )

    def register_retrieval_params(
        self,
        top_k: Optional[int] = None,
        reranking_model: Optional[str] = None,
        extras: Optional[dict[str | ParamKey, Any]] = None,
        span: Optional[Span] = None,
    ) -> None:
        """
        See `lastmile_eval.rag.debugger.api.ManageParamsInterface.register_retrieval_params()`
        """
        params: dict[str | ParamKey, Any] = {
            ParamKey.TOP_K.value: top_k,
            ParamKey.RERANKING_MODEL.value: reranking_model,
        }
        params.update(extras or {})
        filtered_params = {k: v for k, v in params.items() if v is not None}
        self.register_params(
            params=filtered_params,
            span=span,
        )

    def register_generation_params(
        self,
        model_params: dict[str | ParamKey, Any],
        extras: Optional[dict[str | ParamKey, Any]] = None,
        span: Optional[Span] = None,
    ) -> None:
        """
        See `lastmile_eval.rag.debugger.api.ManageParamsInterface.register_generation_params()`
        """
        params = deepcopy(model_params)
        # TODO (rossdan): Test that this actually removes messages from openAI API
        params.pop("messages", None)
        params.update(extras or {})
        filtered_params = {k: v for k, v in params.items() if v is not None}
        self.register_params(
            params=filtered_params,
            span=span,
        )
