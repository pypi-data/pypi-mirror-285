import asyncio

from lastmile_eval.rag.debugger.api.tracing import LastMileTracer
from lastmile_eval.rag.debugger.common.utils import load_dotenv_from_cwd
from lastmile_eval.rag.debugger.tracing.sdk import get_lastmile_tracer

load_dotenv_from_cwd()


tracer: LastMileTracer = get_lastmile_tracer(
    tracer_name="highly-motivated-tracer",
)


@tracer.atrace_function()
async def inner_hello(first, last):
    return f"Hello {first} {last}!"


@tracer.atrace_function()
async def hello(first, last):
    return await inner_hello(first, last)


@tracer.trace_function()
def goodbye(first, last):
    return f"Later, {first} {last}..."


async def main():
    greeting = await hello("Jian", "Yang")
    farewell = goodbye("Erlich", "Bachman")

    print(greeting)
    print(farewell)


asyncio.run(main())  # main loop
