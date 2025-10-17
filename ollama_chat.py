import asyncio
from ollama import AsyncClient
from pydantic import BaseModel, Field
from typing import Literal, Union


class MoveAction(BaseModel):
    action_type: Literal["move"] = "move"
    move_name: str = Field(description="The name of the move to use")

class SwitchAction(BaseModel):
    action_type: Literal["switch"] = "switch"
    pokemon_species: str = Field(description="The species name of the Pokemon to switch to")

class BattleDecision(BaseModel):
    reasoning: str = Field(description="Brief explanation of why this action was chosen")
    action: Union[MoveAction, SwitchAction] = Field(
        description="The action to take - either use a move or switch Pokemon"
    )

async def choose_action(battle_messages, model: str) -> str:
    client = AsyncClient()
    response = await client.chat(
        messages=[
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

    result = asyncio.run(choose_action(battle_messages, model))
    print(result)