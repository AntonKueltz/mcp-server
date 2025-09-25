from mcp_server.context import RequestContext
from mcp_server.data_types import MethodResult
from mcp_server.json_rpc.exceptions import JsonRpcException
from mcp_server.json_rpc.model import INVALID_PARAMS
from mcp_server.prompts import all_prompts, get_prompt as get_prompt_by_name
from mcp_server.prompts.model import Prompt


async def list_prompts(request_context: RequestContext) -> MethodResult:
    prompts = {"prompts": [p.as_list_item().model_dump() for p in all_prompts.values()]}
    return prompts, {}


async def get_prompt(
    name: str, arguments: dict[str, str], request_context: RequestContext
) -> MethodResult:
    prompt = get_prompt_by_name(name)

    if prompt is None:
        raise JsonRpcException(
            code=INVALID_PARAMS, message=f"Invalid prompt name: {name}"
        )

    _validate_args(arguments, prompt)
    detail = await prompt.as_detail(arguments)
    return detail.model_dump(), {}


def _validate_args(args: dict[str, str], prompt: Prompt):
    if not prompt.arguments:
        return

    for required_arg in [a for a in prompt.arguments if a.required]:
        if required_arg.name not in args:
            raise JsonRpcException(
                code=INVALID_PARAMS,
                message=f"Missing required argument: {required_arg.name}",
            )
