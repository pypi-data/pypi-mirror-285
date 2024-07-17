"""
Example file showing how to use the SDK to create a tracer object and 
register parameters
"""

import json
import os
import logging
from typing import Any

from openinference.semconv.trace import (
    OpenInferenceSpanKindValues,
    SpanAttributes,
)
from opentelemetry import trace as trace_api
from opentelemetry.trace import StatusCode

from lastmile_eval.rag.debugger.api import (
    LastMileTracer,
    RetrievedChunk,
    RagFlowType,
)

# TODO: Add these both to the API library instead of relying on SDK
from lastmile_eval.rag.debugger.tracing import (
    get_lastmile_tracer,
    get_latest_ingestion_trace_id,
    get_trace,
    list_ingestion_trace_events,
)

# Define a LastMileTracer, which contains the same base functions as a regular
# OpenTelemetry object
OUTPUT_FILE_NAME = "span_data.txt"
OUTPUT_FILE_PATH = os.path.join(os.path.dirname(__file__), OUTPUT_FILE_NAME)

# Define a LastMileTracer, which contains the same API interface as an
# OpenTelemetry tracer as well as extra methods for logging RAG-specific events
tracer: LastMileTracer = get_lastmile_tracer(
    tracer_name="my-new-project",
    project_name="what's cooking homie?",
    # output_filepath=OUTPUT_FILE_PATH,
)

# We do not have an existing trace running so this parameter will be registered
# to all subsequent traces (unless we call tracer.clear_params())
tracer.register_param("prognosis", "My eyes are burning!")


## Creating another log file to test having multiple loggers
logger = logging.Logger = logging.getLogger("my-manual-logger")
log_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)-5.5s]  %(message)s"
)
logger_filepath = os.path.join(os.getcwd(), "logs", "my-manual-logger.log")
if not os.path.exists(os.path.dirname(logger_filepath)):
    os.mkdir(os.path.dirname(logger_filepath))
open(logger_filepath, "w", encoding="utf-8").close()
file_handler = logging.FileHandler(logger_filepath)
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)


ingestion_tracer: LastMileTracer = get_lastmile_tracer(
    tracer_name="my-ingestion-tracer",
    project_name="what's cooking homie?",
    pipeline_type=RagFlowType.INGESTION,
)


@ingestion_tracer.trace_function()
def ingestion_function(  # pylint: disable=missing-function-docstring
    my_chunk_size: int = 3,
) -> bool:
    print("Using chunk size: ", my_chunk_size)
    root_span = trace_api.get_current_span()
    root_span.set_attribute(
        SpanAttributes.OPENINFERENCE_SPAN_KIND,
        OpenInferenceSpanKindValues.EMBEDDING.value,
    )
    print("We are in the ingestion root span now ")
    ingestion_tracer.register_document_preprocess_params(
        chunk_size=my_chunk_size, chunk_strategy="Chunky Monkey"
    )
    ingestion_tracer.register_embedding_params(
        embedding_model="yo yo yo foshizzle",
        embedding_dimensions=6,
    )

    # Can also use embedded with-blocks instead of decorators around methods
    with ingestion_tracer.start_as_current_span(
        "ingestion-child-span"
    ) as ingestion_child_span:
        print("We are in the ingestion child span now ")
        ingestion_child_span.set_attribute(
            SpanAttributes.OPENINFERENCE_SPAN_KIND,
            OpenInferenceSpanKindValues.CHAIN.value,
        )

        # TODO: Example of logging a RAG ingestion event

        # This parameter has the same key as something that's already stored
        # at the tracer level (one level above current trace). We will
        # overwrite the K-V pair for the trace-specific params, but when we
        # create a new trace the old value will remain
        ingestion_tracer.register_param("chunk_size", 9000)

        ingestion_child_span.set_status(StatusCode.OK)

    return True


@tracer.start_as_current_span(
    "root-span"  # Span finishes automatically when retrieval_function ends
)
def retrieval_function():  # pylint: disable=missing-function-docstring
    root_span = trace_api.get_current_span()
    root_span.set_attribute(
        SpanAttributes.OPENINFERENCE_SPAN_KIND,
        OpenInferenceSpanKindValues.AGENT.value,
    )
    tracer.log(
        "I just want to log some extra data here to the default tracing logger"
    )
    tracer.log(
        "Alright now I'm adding another log statement in same logger file",
    )
    tracer.log("New logging statement in a different logger!", logger)

    tracer.register_retrieval_params(
        top_k=5, reranking_model="What's popppin mi hombres?"
    )
    tracer.register_query_processing_params(
        embedding_model="my name is travis scott and this is healthy mode, eat your vegetales kids",
        embedding_dimensions=5,
        decomposition_strategy="who put the coffee grounds in the coffee machine???",
    )
    # Can also use embedded with-blocks instead of decorators around methods
    with tracer.start_as_current_span("child-span") as child_span:
        child_span.set_attribute(
            SpanAttributes.OPENINFERENCE_SPAN_KIND,
            OpenInferenceSpanKindValues.CHAIN.value,
        )
        words_of_wisdom: str = (
            "Maybe you shouldn't stare directly into the sun after all"
        )

        # Example of logging a RAG query event
        ingestion_trace_id = None
        indexing_trace_data = list_ingestion_trace_events(take=1)
        if "ingestionTraces" in indexing_trace_data:
            ingestion_trace_id = indexing_trace_data["ingestionTraces"][0][
                "id"
            ]
            print(f"{ingestion_trace_id=}")

        # Example of logging rag event for a specific span
        tracer.log_retrieval_event(
            query="Is it healthy to stare at the sun?",
            retrieved_data=[
                RetrievedChunk(
                    id="1234",
                    title="Staring at the sun",
                    content="It is not healthy to stare at the sun",
                    retrieval_score=0.99,
                ),
                RetrievedChunk(
                    id="5678",
                    title="Staring at the sun",
                    content="""
                    It can injure your eyes to stare at the sun
                        Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.

The standard chunk of Lorem Ipsum used since the 1500s is reproduced below for those interested. Sections 1.10.32 and 1.10.33 from "de Finibus Bonorum et Malorum" by Cicero are also reproduced in their exact original form, accompanied by English versions from the 1914 translation by H. Rackham.

Where can I get some?
There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words which don't look even slightly believable. If you are going to use a passage of Lorem Ipsum, you need to be sure there isn't anything embarrassing hidden in the middle of text. All the Lorem Ipsum generators on the Internet tend to repeat predefined chunks as necessary, making this the first true generator on the Internet. It uses a dictionary of over 200 Latin words, combined with a handful of model sentence structures, to generate Lorem Ipsum which looks reasonable. The generated Lorem Ipsum is therefore always free from repetition, injected humour, or non-characteristic words etc.
                    """,
                    retrieval_score=0.85,
                ),
            ],
            span=child_span,
            metadata={"vector_db": "pinecone"},
        )

        # Try uncommenting the `tracer.add_rag_event_for_span()` call below
        # and you will see you get an error
        # tracer.add_rag_event_for_span(
        #     "new child span event",
        #     # If span argument is not passed in, it will default to the current
        #     # span which is the most recent span used under this API call:
        #     # `with tracer.start_as_current_span() as current_span:`
        #     span=child_span,
        #     input="Who is the coolest kid at LastMile and why is it Rossdan?",
        #     output="You are correct, Rossdan is the coolest kid on the team!",
        #     ingestion_trace_id=ingestion_trace_id,
        # )

        # Example of logging rag event for an entire trace
        # (can only be done once per trace)
        tracer.log_trace_event(
            # "retrieval function trace event",
            input="This is some arbitrary input that can be anywhere in the trace",
            output="This is some arbitrary output",
            # ingestion_trace_id=ingestion_trace_id,
            # rag_flow_type=RagFlowType.QUERY,
        )

        # Example of registering another param
        tracer.register_param("words_of_wisdom", words_of_wisdom)

        # This parameter has the same key as something that's already stored
        # at the tracer level (one level above current trace). We will
        # overwrite the K-V pair for the trace-specific params, but when we
        # create a new trace the old value will remain
        tracer.register_param(
            "prognosis", "My eyes are super cool and fresh, no problems here!"
        )

        child_span.set_status(StatusCode.OK)


if __name__ == "__main__":
    ingestion_function(my_chunk_size=3)
    retrieval_function()
    with tracer.start_as_current_span("new-root-span") as unconnected_span:
        manual_span_example = tracer.start_span("new-child-span")
        tracer.register_param(
            "new_param",
            "new_value",
            span=manual_span_example,
        )
        tracer.register_params(
            {"param1": "value1", "param2": "value2"},
            span=manual_span_example,
        )
        tracer.log_span_event(
            name="new child span event",
            span=manual_span_example,
            input="Who is the coolest kid at LastMile and why is it Rossdan?",
            output="You are correct, Rossdan is the coolest kid on the team!",
        )
        manual_span_example.end()
        unconnected_span.set_status(StatusCode.OK)

        print("This is the tracer.get_params() output:")
        print(json.dumps(tracer.get_params(), indent=4))

        tracer.register_params(
            {"param3": "value3", "param4": "value4"},
            should_overwrite=True,
            # Please note that even if you try to pass in a span into this
            # method, the span has already ended (which happens when we call
            # `manual_span_example.end()`) so we cannot write to it anymore.
            # We will however still be able to write to the trace-level params
            # that's associated with this trace that contains the span
            span=manual_span_example,
        )
        print(
            "This is the tracer.get_params() output after overwriting existing values:"
        )
        print(json.dumps(tracer.get_params(), indent=4))

        tracer.clear_params()
        print("This is the tracer.get_params() output after clearing params:")
        print(json.dumps(tracer.get_params(), indent=4))

    # # Example of getting ingestion trace data (reference traceId as a column)
    # ingestion_table_data = list_ingestion_trace_events(take=1)
    # print(json.dumps(ingestion_table_data, indent=4))

    # # Example of getting raw trace data
    # most_recent_ingestion_trace_id: str = get_latest_ingestion_trace_id()
    # ingestion_trace_event_data: core.JSONObject = get_trace(
    #     # TODO (optional): Add back context object for keep track of trace_ids
    #     # instead of hardcoding in this example
    #     trace_id=most_recent_ingestion_trace_id,
    # )
    # print(json.dumps(ingestion_trace_event_data, indent=4))
