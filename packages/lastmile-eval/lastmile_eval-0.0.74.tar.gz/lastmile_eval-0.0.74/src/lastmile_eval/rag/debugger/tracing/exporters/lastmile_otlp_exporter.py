"""
LastMile implementation of OTLPSpanExporter, which sends trace data 
to the OTEL collector service, and also forwards specific RAG events to
the LastMile service.
"""

import logging
from typing import Callable, Dict, Optional, Sequence

from opentelemetry.exporter.otlp.proto.http import Compression
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExportResult
from requests import Session


class LastMileOTLPSpanExporter(OTLPSpanExporter):
    """
    LastMile implementation of OTLPSpanExporter, which sends trace data
    to the OTEL collector service, and also forwards specific RAG events to
    the LastMile service.
    """

    def __init__(
        self,
        log_rag_query_func: Optional[Callable[[], None]] = None,
        endpoint: Optional[str] = None,
        certificate_file: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        compression: Optional[Compression] = None,
        session: Optional[Session] = None,
    ):
        self.log_rag_query_func = log_rag_query_func
        super().__init__(
            endpoint, certificate_file, headers, timeout, compression, session
        )

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        try:
            # Forward trace data to OTEL collector
            res = super().export(spans)

            if res == SpanExportResult.SUCCESS:
                # Forward RAG events to LastMile service
                # We only do this if the span being exported includes the
                # root trace span (signaling the end of the trace event)
                is_root_span = False
                for span in spans:
                    if span.parent is None:
                        is_root_span = True
                        break

                # Forward the RAG events to LastMile service
                if is_root_span and self.log_rag_query_func:
                    self.log_rag_query_func()

            return res
        except Exception as e:
            logging.error(  # pylint: disable=logging-fstring-interpolation
                f"Error forwarding trace data to OTEL collector: {e}",
                stack_info=True,
            )

            return SpanExportResult.FAILURE
