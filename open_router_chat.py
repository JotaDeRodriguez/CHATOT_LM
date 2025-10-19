import asyncio
import httpx
import json
from response_models import BattleDecision
from dotenv import load_dotenv
import os

load_dotenv()

async def router_choose_action(battle_messages: list, model: str) -> str:
    battle_decision_schema = BattleDecision.model_json_schema()
    battle_decision_schema["additionalProperties"] = False

    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv("OPEN_ROUTER_KEY")}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": battle_messages,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "action_response",
                        "strict": True,
                        "schema": 
                            {'properties': 
                                {'reasoning': 
                                    {'description': 'Explanation of why this action was chosen', 
                                    'title': 'Reasoning', 
                                    'type': 'string'}, 
                                'action': 
                                    {'description': 'The action to take - either use a move name or the name of the Pokemon to switch to', 
                                     'title': 'Action', 
                                     'type': 'string'}
                                }, 
                            'required': ['reasoning', 'action'], 
                            'title': 'BattleDecision', 
                            'type': 'object', 
                            'additionalProperties': False},
                        }
                    }
                }
        )

    data = response.json()

    # Check for errors in the response
    if "error" in data:
        raise Exception(f"API Error: {data['error']}")

    return data["choices"][0]["message"]["content"]

