from http.client import NOT_FOUND

from fastapi import HTTPException

from mcp_server.context import RequestContext
from mcp_server.data_types import MethodResult
from mcp_server.prompts import all_prompts, get_prompt as get_prompt_by_name


async def list_prompts(request_context: RequestContext) -> MethodResult:
    prompts = {"prompts": [p.as_list_item().model_dump() for p in all_prompts.values()]}
    return prompts, {}


async def get_prompt(
    name: str, arguments: dict[str, str], request_context: RequestContext
) -> MethodResult:
    prompt = get_prompt_by_name(name)

    if prompt is None:
        raise HTTPException(status_code=NOT_FOUND)

    result = prompt.model_copy()
    result.set_messages(arguments)

    return result.as_detail().model_dump(), {}
