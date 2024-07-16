from dataclasses import dataclass
from typing import Any, Callable, Optional

import instructor

from qrev_instructor.models import AnthropicModel, APIModel, APIType, OpenAIModel


## Load the APIs
@dataclass
class FuncApiWrapper:
    """
    Wrapper for the API function call and class
    """

    from_class: type[Any]
    from_func: Callable[..., Any]
    original_func: Optional[Callable[..., Any]] = None


def get_apis() -> dict[APIType, FuncApiWrapper]:
    # Load the OpenAI API
    apis: dict[APIType, FuncApiWrapper] = {}
    try:
        from openai import OpenAI

        apis[APIType.OPENAI] = FuncApiWrapper(OpenAI, instructor.from_openai)

    except ImportError:
        pass

    # Load the Anthropic API
    try:
        from anthropic import Anthropic

        apis[APIType.ANTHROPIC] = FuncApiWrapper(Anthropic, instructor.from_anthropic)

    except ImportError:
        pass
    return apis



def get_api_service(model_name: str) -> APIType:
    model_name = model_name.lower()
    if model_name in AnthropicModel._value2member_map_:
        return APIType.ANTHROPIC
    elif model_name in OpenAIModel._value2member_map_:
        return APIType.OPENAI
    model_name = model_name.replace("-", "_").replace(".", "_").upper()
    if model_name in AnthropicModel._member_names_:
        return APIType.ANTHROPIC
    elif model_name in OpenAIModel._member_names_:
        return APIType.OPENAI
    else:
        raise NotImplementedError(f"Model {model_name} not supported")
