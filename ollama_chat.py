import asyncio
from ollama import AsyncClient

async def local_choose_action(battle_messages: list, model: str) -> str:
    client = AsyncClient()
    response = await client.chat(
        messages=battle_messages,
        model=model,
        format={
            'properties': {
                'reasoning': {
                    'description': 'Explanation of why this action was chosen',
                    'title': 'Reasoning',
                    'type': 'string'
                },
                'action': {
                    'description': 'The action to take - either use a move name or the name of the Pokemon to switch to',
                    'title': 'Action',
                    'type': 'string'
                }
            },
            'required': ['reasoning', 'action'],
            'title': 'BattleDecision',
            'type': 'object',
            'additionalProperties': False
        },
    )
    return response.message.content
