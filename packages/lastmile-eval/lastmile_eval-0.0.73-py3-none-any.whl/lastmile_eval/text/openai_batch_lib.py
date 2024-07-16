import traceback as tb
from abc import abstractmethod
from dataclasses import dataclass
from functools import partial
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    ParamSpec,
    Protocol,
    Type,
    cast,
)

import instructor
import openai.types.chat as openai_types
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel

from .batch_lib import ppe_map, retry_with_exponential_backoff

T_ParamSpec = ParamSpec("T_ParamSpec")

# TODO: type these properly
InputAdapter = Any
OutputAdapter = Any
CompletionFunction = Any


class OpenAIChatCompletionCreate(Protocol[T_ParamSpec]):
    @abstractmethod
    def __call__(
        self,
        messages: Iterable[openai_types.ChatCompletionMessageParam],
        model: str,
        *args: T_ParamSpec.args,
        **kwargs: T_ParamSpec.kwargs,
    ) -> openai_types.ChatCompletion:
        pass


class MockChatCompletions(Generic[T_ParamSpec]):
    def __init__(self, create_fn: OpenAIChatCompletionCreate[T_ParamSpec]):
        self.create_fn = create_fn

    def create(
        self,
        messages: Iterable[openai_types.ChatCompletionMessageParam],
        model: str,
        *args: T_ParamSpec.args,
        **kwargs: T_ParamSpec.kwargs,
    ):
        return self.create_fn(messages, model, *args, **kwargs)


class MockChat(Generic[T_ParamSpec]):
    def __init__(self, create_fn: OpenAIChatCompletionCreate[T_ParamSpec]):
        self.completions = MockChatCompletions(create_fn)


class MockOpenAI(Generic[T_ParamSpec]):
    def __init__(self, create_fn: OpenAIChatCompletionCreate[T_ParamSpec]):
        self.chat = MockChat(create_fn)


@dataclass(frozen=True)
class MockOpenAIClientConfig:
    create_fn: Any  # TODO type this


@dataclass(frozen=True)
class RealOpenAIClientConfig:
    # can put the API key here
    # for now this is empty, we read API key from env.
    pass


OpenAIClientConfig = RealOpenAIClientConfig | MockOpenAIClientConfig


def batch_run_df_to_structured(
    df: pd.DataFrame,
    # TODO: replace Any
    record_to_record: Callable[[dict[Any, Any]], dict[Any, Any]],
):
    inputs = df.to_dict("records")  # type: ignore[pandas]
    out = ppe_map(record_to_record, inputs)  # type: ignore[fixme]

    df_out = pd.DataFrame.from_records(out)  # type: ignore[pandas]
    df_out.index = df.index  # type: ignore[pandas]
    return df_out


def input_adapter_openai_text_to_structured(
    input_text: str,
    model_name: str,
    **kwargs: Any,  # TODO: fix this
):
    return _input_adapter_openai_text_to_structured_helper(
        input_text, model_name, **kwargs
    )


def _input_adapter_openai_text_to_structured_helper(
    input_text: str,
    model_name: str,
    **kwargs: Any,  # TODO: fix this
):
    response_model = kwargs.pop("response_model_type")
    return dict(
        messages=[
            {
                "role": "user",
                "content": input_text,
            }
        ],
        model=model_name,
        response_model=response_model,
        **kwargs,
    )


def make_openai_default_text_to_structured(client_config: OpenAIClientConfig):
    return partial(
        _openai_default_text_to_structured_helper,
        client_config,
    )


def _openai_default_text_to_structured_helper(
    client_config: OpenAIClientConfig,
    input_text: str,
    model_name: str,
    response_model_type: Type[BaseModel],
    **kwargs: Any,  # TODO: fix this
) -> dict[Any, Any]:
    def _dump_output_adapter(value: BaseModel) -> dict[Any, Any]:
        return value.model_dump()

    text_to_structured = make_openai_text_to_structured_instructor(
        client_config,
        input_adapter_openai_text_to_structured,
        _dump_output_adapter,
    )
    return text_to_structured(  # type: ignore[fixme]
        input_text,
        model_name,
        response_model_type=response_model_type,
        **kwargs,
    )


def make_adapted_completion_fn(
    completion_fn: CompletionFunction,
    input_adapter: InputAdapter,
    output_adapter: OutputAdapter,
):
    def _adapted_completion_fn(
        input_text: str,
        model_name: str,
        memoization_version: int = 8,
        **kwargs: Any,  # TODO: fix this
    ):
        try:
            # print(
            #     f"Actually running {input_text[:20]}..., {model_name}{kwargs}"
            # )
            input_data = input_adapter(input_text, model_name, **kwargs)
            response = completion_fn(**input_data)  # type: ignore[fixme]
            out = output_adapter(response)
            return out
        except Exception as e:
            print("EXCEPTION:")
            tb.print_exc()
            return f"this was an exception:\n{input_text=}{kwargs=}\nexn={e}\n{tb.format_exc()}"

    return _adapted_completion_fn


def make_openai_text_to_structured_instructor(
    client_config: OpenAIClientConfig,
    input_adapter: InputAdapter,
    output_adapter: OutputAdapter,
) -> Callable[..., dict[Any, Any]]:  # TODO: fix types
    client = _client_config_to_client(client_config)
    client_structured = instructor.patch(client)
    completion_fn = make_general_openai_completion_fn(client_structured)
    text_to_structured = make_adapted_completion_fn(
        completion_fn,
        input_adapter=input_adapter,
        output_adapter=output_adapter,
    )

    return text_to_structured  # type: ignore[fixme]


def _client_config_to_client(client_config: OpenAIClientConfig) -> OpenAI:
    match client_config:
        case RealOpenAIClientConfig():
            return OpenAI()
        case MockOpenAIClientConfig(create_fn):
            # TODO replace this with real OpenAI client
            # containing mock create fn
            return MockOpenAI(create_fn)  # type: ignore[fixme]


def make_general_openai_completion_fn(client: OpenAI):
    @retry_with_exponential_backoff
    def _completion_fn(
        **kwargs: Any,  # TODO: fix this
    ) -> openai_types.ChatCompletion:
        out = cast(
            openai_types.ChatCompletion,
            client.chat.completions.create(**kwargs),
        )
        return out

    return _completion_fn
