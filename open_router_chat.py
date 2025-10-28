import asyncio
import httpx
import json
from dotenv import load_dotenv
import os

load_dotenv()

async def router_choose_action(battle_messages: list, model: str) -> str:
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
                        "schema": {
                            "type": "object",
                            "properties": {
                                "reasoning": {
                                    "type": "string",
                                    "description": "Explanation of why this action was chosen"
                                },
                                "action": {
                                    "type": "string",
                                    "description": "The action to take - either use a move name or the name of the Pokemon to switch to"
                                },
                                "scratchpad": {
                                    "type": "string",
                                    "description": "Private notes and strategic considerations for future turns. This content will be provided back in subsequent turns."
                                }
                            },
                            "required": ["reasoning", "action"],
                            "additionalProperties": False
                        }
                    }
                }
            }
        )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

