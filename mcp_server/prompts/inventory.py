from mcp_server.prompts.model import Prompt

all_prompts: dict[str, Prompt] = {}


def add_prompt(prompt: Prompt):
    all_prompts[prompt.name] = prompt


def get_prompt(name: str) -> Prompt | None:
    return all_prompts.get(name)
