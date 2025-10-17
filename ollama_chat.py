import asyncio
from ollama import AsyncClient
from response_models import BattleDecision


async def local_choose_action(battle_messages, model: str) -> str:
    client = AsyncClient()
    response = await client.chat(
        messages=[
            {
                'role': 'system',
                'content': "You're in a Pokemon Battle. At every turn you'll have a list of actions to take. Choose carefully. \n"
                "If no moves are available, your pokemon was fainted and you need to switch."
            },
            {
                'role': 'user',
                'content': battle_messages,
            }
        ],
        model=model,
        format=BattleDecision.model_json_schema(),
    )
    return response.message.content


if __name__ == "__main__":

    model = "gemma3:4b"
    battle_messages = """
    === Battle State (Turn 1) ===
    {'turn': 1, 'my_active': {'species': 'dugtrio', 'hp': 1.0, 'moves': [{'name': 'earthquake', 'type': 'GROUND (pokemon type) object', 'power': 100}, {'name': 'suckerpunch', 'type': 'DARK (pokemon type) object', 'power': 70}, {'name': 'swordsdance', 'type': 'NORMAL (pokemon type) object', 'power': 0}, {'name': 'stoneedge', 'type': 'ROCK (pokemon type) object', 'power': 100}]}, 'opponent_active': {'species': 'leafeon', 'hp': 1.0}, 'my_team': [{'species': 'dugtrio', 'hp': 1.0}, {'species': 'glimmora', 'hp': 1.0}, {'species': 'smeargle', 'hp': 1.0}, {'species': 'noctowl', 'hp': 1.0}, {'species': 'skuntank', 'hp': 1.0}, {'species': 'klawf', 'hp': 1.0}], 'available_switches': ['glimmora', 'smeargle', 'noctowl', 'skuntank', 'klawf']}    
    This is a sample text
    """

    result = asyncio.run(local_choose_action(battle_messages, model))
    print(result)