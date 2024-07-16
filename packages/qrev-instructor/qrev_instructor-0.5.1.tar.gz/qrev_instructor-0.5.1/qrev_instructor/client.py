from typing import Any, Iterable, Optional, TypeVar, Union

import instructor
from pydantic import BaseModel

from qrev_instructor.apis import get_api_service, get_apis
from qrev_instructor.models import APIModel, APIType

T = TypeVar("T", bound=Union[BaseModel, "Iterable[Any]"])

apis = get_apis()


def _get_client(
    model: Optional[str | APIModel] = None,
    client: Optional[Any] = None,
    llm_type: Optional[str] = None,
    client_params: Optional[dict[str, Any]] = None,
    func_params: Optional[dict[str, Any]] = None,
) -> instructor.Instructor:
    if model and llm_type:
        raise ValueError(f"Cannot specify both model and llm_type. Got {model} and {llm_type}")
    if client:
        client_cls_name = client.__class__.__name__.lower()
        if "anthropic" in client_cls_name:
            _llm_type = APIType.ANTHROPIC
        elif "openai" in client_cls_name:
            _llm_type = APIType.OPENAI
        else:
            raise NotImplementedError(f"Client {client} not supported yet")
    else:
        _llm_type = None
    nllm_type = None
    if model:
        nllm_type = get_api_service(str(model))
    elif llm_type:
        nllm_type = APIType(llm_type)
    if _llm_type and nllm_type and nllm_type != _llm_type:
        raise ValueError(f"Cannot specify different llm_types. Got {_llm_type} != {nllm_type}")
    if _llm_type is None:
        _llm_type = nllm_type
    if nllm_type is None:
        nllm_type = APIType.OPENAI

    if client_params is None:
        client_params = {}
    if func_params is None:
        func_params = {}
    wrap = apis[nllm_type]
    instance = wrap.from_class(**client_params)
    if client:
        return_client = wrap.from_func(client, **func_params)
    else:
        return_client = wrap.from_func(instance, **func_params)
    return return_client


def get_client(
    model: Optional[str | APIModel] = None,
    client: Optional[Any] = None,
    llm_type: Optional[str] = None,
    client_params: Optional[dict[str, Any]] = None,
    func_params: Optional[dict[str, Any]] = None,
) -> instructor.Instructor:
    client = _get_client(model=model, client=client, llm_type=llm_type, client_params=client_params,func_params= func_params)
    return client
