import openai
from tracing_auto_instrumentation.openai import wrap_openai

from lastmile_eval.rag.debugger.api.tracing import LastMileTracer
from lastmile_eval.rag.debugger.common.utils import load_dotenv_from_cwd

from lastmile_eval.rag.debugger.tracing.sdk import get_lastmile_tracer

load_dotenv_from_cwd()


tracer: LastMileTracer = get_lastmile_tracer(
    tracer_name="my-tracer",
)


@tracer.trace_function()
def openai_function():  # pylint: disable=missing-function-docstring
    client = wrap_openai(openai.OpenAI(), tracer)

    @tracer.trace_function()
    def some_llm_function(body):
        result = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": body}],
            temperature=0.5,
        )
        content = result.choices[0].message.content
        return content

    question = "What is the meaning of life?"
    response = some_llm_function(question)
    print("RESPONSE:\n", response)


if __name__ == "__main__":
    openai_function()
