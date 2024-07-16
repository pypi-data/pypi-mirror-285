import asyncio
import json
import sys
import traceback as tb
from dataclasses import dataclass

from aiconfig import AIConfigRuntime, InferenceOptions, Prompt
from aiconfig.schema import ExecuteResult

from lastmile_eval.rag.debugger.app_utils import AIConfigPromptContainer
from lastmile_eval.rag.debugger.common.utils import load_dotenv_from_cwd


def create_error_payload(message: str, code: int):
    # aiconfig_json = (
    #     aiconfig_deep_copy.model_dump(exclude=EXCLUDE_OPTIONS)
    #     if aiconfig_deep_copy is not None
    #     else None
    # )
    aiconfig_json = None
    return json.dumps(
        {
            "error": {
                "message": message,
                "code": code,
                "data": aiconfig_json,
            }
        }
    )


def print_and_flush(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()


def serialize_chunk_and_get_new_acc_output(data, accumulated_output_text):
    text = data
    if isinstance(text, Exception):
        return create_error_payload(message=f"Exception: {text}", code=500)
    elif isinstance(text, str):
        accumulated_output_text += text
    elif isinstance(text, dict) and "content" in text:
        # TODO: Fix streaming output format so that it returns text
        accumulated_output_text += text["content"]
    elif isinstance(text, dict) and "generated_text" in text:
        # TODO: Fix streaming output format so that it returns text
        accumulated_output_text += text["generated_text"]

    execute_result = ExecuteResult(
        **{
            "output_type": "execute_result",
            "data": accumulated_output_text,
            # Assume streaming only supports single output
            # I think this actually may be wrong for PaLM or OpenAI
            # TODO: Need to sync with Ankush but can fix forward
            "execution_count": 0,
            "metadata": {},
        }  # type: ignore
    )
    output = [{"output_chunk": execute_result.to_json()}]
    output_serialized = json.dumps(output)
    return output_serialized, accumulated_output_text


async def main(prompt_container: AIConfigPromptContainer):
    try:
        load_dotenv_from_cwd()
        aiconfig = AIConfigRuntime.create()
        model_name = prompt_container.model_name
        inference_kwargs = prompt_container.inference_kwargs

        system_prompt = None
        input = None
        # TODO: Handle dynamic number of messages
        for message in prompt_container.messages:
            if system_prompt is not None and input is not None:
                break
            if message.role == "system" and system_prompt is None:
                system_prompt = message.content
            elif message.role == "user" and input is None:
                input = message.content

        new_prompt = Prompt(
            name="prompt1",
            input=input or "",
            metadata={
                "model": {
                    "name": model_name,
                    "settings": {
                        "system_prompt": system_prompt or "",
                        **inference_kwargs,
                    },
                },
            },
        )

        aiconfig.add_prompt("prompt1", new_prompt)

        @dataclass
        class AccumulatedOutput:
            accumulated_output_text: str

        accumulated_output_text_wrapper = AccumulatedOutput("")

        def stream_callback(data, _, __):
            if data:
                (
                    output_serialized,
                    new_accumulated_output_text,
                ) = serialize_chunk_and_get_new_acc_output(
                    data,
                    accumulated_output_text_wrapper.accumulated_output_text,
                )
                accumulated_output_text_wrapper.accumulated_output_text = (
                    new_accumulated_output_text
                )
                print_and_flush(output_serialized)

        inference_options = InferenceOptions(
            stream=True,
            stream_callback=stream_callback,
        )

        out = await aiconfig.run(new_prompt.name, options=inference_options)
        out_serializable = [elt.model_dump() for elt in out]
        print_and_flush(json.dumps({"response": out_serializable}))
    except Exception as e:
        tb.print_exc()
        print_and_flush(
            create_error_payload(message=f"Exception: {e}", code=500)
        )

    print_and_flush(json.dumps([{"stop_streaming": None}]))


if __name__ == "__main__":
    try:
        prompt_container = AIConfigPromptContainer.model_validate_json(
            sys.stdin.read().strip()
        )
        asyncio.run(main(prompt_container))
    except Exception as e:
        tb.print_exc()
        print_and_flush(
            create_error_payload(message=f"Exception: {e}", code=500)
        )
