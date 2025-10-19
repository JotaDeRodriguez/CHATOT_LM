import json
from poke_env.battle import Battle
import yaml
import os


def create_observation_dictionary(battle: Battle):
    return {
        "weather": str(battle.weather),
        "fields": [str(field) for field in battle.fields],
        "side_conditions": {str(condition): value for condition, value in battle.side_conditions.items()},
        "opponent_side_conditions": {str(condition): value for condition, value in
                                     battle.opponent_side_conditions.items()},
        "turn": battle.turn,
        "active_pokemon": {
            "species": str(battle.active_pokemon.species) if battle.active_pokemon else None,
            "level": battle.active_pokemon.level if battle.active_pokemon else None,
            "ability": str(battle.active_pokemon.ability) if battle.active_pokemon else None,
            "item": str(battle.active_pokemon.item) if battle.active_pokemon else None,
            "gender": str(battle.active_pokemon.gender) if battle.active_pokemon else None,
            "current_hp_fraction": "{:.2%}".format(
                battle.active_pokemon.current_hp_fraction) if battle.active_pokemon else None,
            "status": str(
                battle.active_pokemon.status) if battle.active_pokemon and battle.active_pokemon.status else None,
            "boosts": battle.active_pokemon.boosts if battle.active_pokemon else None,
            "moves": list(battle.active_pokemon.moves.keys()) if battle.active_pokemon else None,
            "effects": [str(effect) for effect in battle.active_pokemon.effects] if battle.active_pokemon else None,
            "stats": battle.active_pokemon.stats if battle.active_pokemon else None
        },
        "team": {
            pokemon.species: str(pokemon.status) if pokemon.status else None for pokemon in battle.team.values()
        },
        "opponent_active_pokemon": {
            "species": str(battle.opponent_active_pokemon.species) if battle.opponent_active_pokemon else None,
            "level": battle.opponent_active_pokemon.level if battle.opponent_active_pokemon else None,
            "ability": str(battle.opponent_active_pokemon.ability) if battle.opponent_active_pokemon else None,
            "item": str(battle.opponent_active_pokemon.item) if battle.opponent_active_pokemon else None,
            "gender": str(battle.opponent_active_pokemon.gender) if battle.opponent_active_pokemon else None,
            "current_hp_fraction": "{:.2%}".format(
                battle.opponent_active_pokemon.current_hp_fraction) if battle.opponent_active_pokemon else None,
            "status": str(
                battle.opponent_active_pokemon.status) if battle.opponent_active_pokemon and battle.opponent_active_pokemon.status else None,
            "boosts": battle.opponent_active_pokemon.boosts if battle.opponent_active_pokemon else None,
            "moves": list(battle.opponent_active_pokemon.moves.keys()) if battle.opponent_active_pokemon else None,
            "effects": [str(effect) for effect in
                        battle.opponent_active_pokemon.effects] if battle.opponent_active_pokemon else None,
            "stats": battle.opponent_active_pokemon.stats if battle.opponent_active_pokemon else None
        },
        "opponent_team": {
            pokemon.species: str(pokemon.status) if pokemon.status else None for pokemon in
            battle.opponent_team.values()
        }
    }


def create_team_dictionary(battle: Battle):
    return {
        "player_team": {
            pokemon.species: {
                "level": pokemon.level,
                "ability": str(pokemon.ability),
                "item": str(pokemon.item),
                "gender": str(pokemon.gender),
                "current_hp": pokemon.current_hp,
                "max_hp": pokemon.max_hp,
                "current_hp_fraction": "{:.2%}".format(pokemon.current_hp_fraction),
                "status": str(pokemon.status) if pokemon.status else None,  # Changed this line
                "stats": pokemon.stats,
                "moves": {
                    move_id: {
                        "current_pp": move.current_pp,
                        "max_pp": move.max_pp
                    } for move_id, move in pokemon.moves.items()
                },
                "effects": [str(effect) for effect in pokemon.effects],
                "boosts": pokemon.boosts,
                "is_active": pokemon == battle.active_pokemon,
                "fainted": pokemon.fainted,
                "types": [str(type_) for type_ in pokemon.types]
            } for pokemon in battle.team.values()
        }
    }


def load_yaml(yaml_path="prompts.yaml"):
    with open(yaml_path, 'r', encoding="utf-8") as f:
        return yaml.safe_load(f)
    

if __name__ == "__main__":
    print(load_yaml())