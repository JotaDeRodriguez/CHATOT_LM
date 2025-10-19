from pydantic import BaseModel, Field

class BattleDecision(BaseModel):
    reasoning: str = Field(description="Brief explanation of why this action was chosen")
    action: str = Field(
        description="The action to take - either use a move name or the name of the Pokemon to swithc to"
    )

if __name__ == "__main__":
    battle_decision_schema = BattleDecision.model_json_schema()
    battle_decision_schema["additionalProperties"] = False
    print(battle_decision_schema)
