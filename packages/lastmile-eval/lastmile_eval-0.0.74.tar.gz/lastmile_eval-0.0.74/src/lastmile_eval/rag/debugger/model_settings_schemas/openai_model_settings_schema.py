from typing import Any, Dict


from lastmile_eval.rag.debugger.model_settings_schemas.prompt_model_settings_schema import (
    PromptModelSettingsSchema,
)


# properties *should* be Dict[str, JSONValue], but doing that gives:
# pydantic.errors.PydanticUserError: `PromptModel` is not fully defined; you
# should define `JSONValue`, then call `PromptModel.model_rebuild()`.
# And redefining JSONValue here ends up with pydantic maximum recursion depth
# reached (https://github.com/pydantic/pydantic/issues/2279#issuecomment-1876108310)
class OpenAIModelSettingsSchema(PromptModelSettingsSchema):
    """
    Schema for OpenAI model settings.
    """

    properties: Dict[str, Any] = {
        "frequency_penalty": {
            "type": "number",
            "minimum": -2.0,
            "maximum": 2.0,
            "description": "Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.",
        },
        "max_tokens": {
            "type": "integer",
            "description": "The maximum number of tokens that can be generated in the completion. The token count of your prompt plus max_tokens cannot exceed the model's context length.",
        },
        "n": {
            "type": "integer",
            "description": "How many completions to generate for each prompt. Note: Because this parameter generates many completions, it can quickly consume your token quota. Use carefully and ensure that you have reasonable settings for max_tokens and stop.",
        },
        "presence_penalty": {
            "type": "number",
            "minimum": -2.0,
            "maximum": 2.0,
            "description": "Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.",
        },
        "stop": {
            "type": "array",
            "items": {
                "type": "string",
            },
            "description": "Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.",
        },
        "temperature": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 2.0,
            "description": "What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or top_p but not both.",
        },
        "top_p": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or temperature but not both.",
        },
        "user": {
            "type": "string",
            "description": "A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse",
        },
    }
