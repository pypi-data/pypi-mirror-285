from typing import Any, Dict, List
import lastmile_utils.lib.core.api as core_utils


# properties *should* be Dict[str, JSONValue], but doing that gives:
# pydantic.errors.PydanticUserError: `PromptModel` is not fully defined; you
# should define `JSONValue`, then call `PromptModel.model_rebuild()`.
# And redefining JSONValue here ends up with pydantic maximum recursion depth
# reached (https://github.com/pydantic/pydantic/issues/2279#issuecomment-1876108310)


class PromptModelSettingsSchema(core_utils.Record):
    """
    Schema for prompt model settings.
    """

    type: str = "object"
    properties: Dict[str, Any] = {}
    required: List[str] = []
