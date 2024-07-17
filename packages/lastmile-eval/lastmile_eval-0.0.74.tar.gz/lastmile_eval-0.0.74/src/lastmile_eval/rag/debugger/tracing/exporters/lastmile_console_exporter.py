"""
LastMile implementation of ConsoleSpanExporter, which prints out trace data
to console (or output file if specified). 
"""

import logging
import sys
from typing import Callable, Optional, Sequence, IO

from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
)

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExportResult


class LastMileConsoleSpanExporter(ConsoleSpanExporter):
    """
    LastMile implementation of ConsoleSpanExporter, which sends trace data
    to specific output (defaults to sys.out but can also be a file).

    Use this as a "dry-run" instead of using LastMileOTLPSpanExporter, which
    sends data to the LastMile service and OTEL collector.
    """

    def __init__(
        self,
        reset_trace_data_func: Optional[Callable[[], None]] = None,
        out: IO = sys.stdout,  # type: ignore
    ):
        self.reset_trace_data_func = reset_trace_data_func
        super().__init__(out=out)  # type: ignore

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

                # Reset the trace data after exporting
                if is_root_span and self.reset_trace_data_func:
                    self.reset_trace_data_func()

            return res
        except Exception as e:
            logging.error(  # pylint: disable=logging-fstring-interpolation
                f"Error exporting trace data: {e}",
                stack_info=True,
            )

            return SpanExportResult.FAILURE
