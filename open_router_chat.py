import asyncio
import httpx
import json
from response_models import BattleDecision
from dotenv import load_dotenv
import os

load_dotenv()

async def router_choose_action(battle_messages, model: str) -> str:
    battle_decision_schema = BattleDecision.model_json_schema()

    # Format schema description for the prompt
    schema_str = json.dumps(battle_decision_schema, indent=2)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv("OPEN_ROUTER_KEY")}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": f"You're in a Pokemon Battle. At every turn you'll have a list of actions to take. Choose carefully.\n"
                        f"If no moves are available, your pokemon was fainted and you need to switch.\n\n"
                        f"Respond with valid JSON matching this schema:\n{schema_str}"
                    },
                    {
                        "role": "user",
                        "content": battle_messages
                    },
                ],
                "response_format": {"type": "json_object"},
            },
        )

    data = response.json()
    return data["choices"][0]["message"]["content"]


if __name__ == "__main__":
    model = "google/gemini-2.5-flash"
    battle_messages = """
    === Battle State (Turn 1) ===
    {'turn': 1, 'my_active': {'species': 'dugtrio', 'hp': 1.0, 'moves': [{'name': 'earthquake', 'type': 'GROUND (pokemon type) object', 'power': 100}, {'name': 'suckerpunch', 'type': 'DARK (pokemon type) object', 'power': 70}, {'name': 'swordsdance', 'type': 'NORMAL (pokemon type) object', 'power': 0}, {'name': 'stoneedge', 'type': 'ROCK (pokemon type) object', 'power': 100}]}, 'opponent_active': {'species': 'leafeon', 'hp': 1.0}, 'my_team': [{'species': 'dugtrio', 'hp': 1.0}, {'species': 'glimmora', 'hp': 1.0}, {'species': 'smeargle', 'hp': 1.0}, {'species': 'noctowl', 'hp': 1.0}, {'species': 'skuntank', 'hp': 1.0}, {'species': 'klawf', 'hp': 1.0}], 'available_switches': ['glimmora', 'smeargle', 'noctowl', 'skuntank', 'klawf']}
    This is a sample text
    """

    result = asyncio.run(router_choose_action(battle_messages, model))
    print(result)
