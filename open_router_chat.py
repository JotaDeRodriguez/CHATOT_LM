import asyncio
import httpx
import json
from dotenv import load_dotenv
import os

load_dotenv()

async def router_choose_action(battle_messages: list, model: str) -> str:
    
    try:
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

        # Check HTTP status code
        if response.status_code != 200:
            raise Exception(f"API returned status code {response.status_code}: {response.text}")

        # Try to parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse API response as JSON: {str(e)}. Response text: {response.text[:500]}")

        # Check for errors in the response
        if "error" in data:
            raise Exception(f"API Error: {data['error']}")

        # Validate response structure
        if "choices" not in data or not data["choices"]:
            raise Exception(f"Invalid API response structure - missing choices: {data}")

        return data["choices"][0]["message"]["content"]

    except httpx.RequestError as e:
        raise Exception(f"Network error during API request: {str(e)}")
    except Exception as e:
        # Re-raise with context if not already wrapped
        if "API" not in str(e) and "Network" not in str(e):
            raise Exception(f"Unexpected error in router_choose_action: {str(e)}")
        raise

