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
        description="The action to take - either use a move or switch Pokemon",
        discriminator="action_type"
    )