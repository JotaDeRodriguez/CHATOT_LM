import json
from poke_env.battle import Battle
import yaml
import os
from toon import encode as toon_encode


def remove_empty_values(data):
    """
    Recursively remove null, empty strings, empty arrays, empty dicts,
    and dicts/objects with only zero values (like zero-only boosts/stats).
    """
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            if value is None or value == "" or value == []:
                continue
            # Remove empty dicts
            if isinstance(value, dict) and not value:
                continue
            # Remove dicts with only zero values (boosts, partial stats)
            if isinstance(value, dict) and all(v == 0 or v is None for v in value.values()):
                continue
            # Recursively clean nested structures
            cleaned_value = remove_empty_values(value)
            if cleaned_value is not None and cleaned_value != "" and cleaned_value != [] and cleaned_value != {}:
                cleaned[key] = cleaned_value
        return cleaned if cleaned else {}
    elif isinstance(data, list):
        return [remove_empty_values(item) for item in data if item is not None and item != "" and item != []]
    else:
        return data


def create_observation_dictionary(battle: Battle):
    """
    Create a token-optimized observation dictionary.
    Omits null values, empty arrays, and zero-only boosts/stats.
    """
    obs = {
        "weather": str(battle.weather) if battle.weather else None,
        "fields": [str(field) for field in battle.fields],
        "side_conditions": {str(condition): value for condition, value in battle.side_conditions.items()},
        "opponent_side_conditions": {str(condition): value for condition, value in
                                     battle.opponent_side_conditions.items()},
        "turn": battle.turn,
    }

    # Active Pokemon
    if battle.active_pokemon:
        active_data = {
            "species": str(battle.active_pokemon.species),
            "level": battle.active_pokemon.level,
            "ability": str(battle.active_pokemon.ability),
            "item": str(battle.active_pokemon.item),
            "current_hp_fraction": "{:.2%}".format(battle.active_pokemon.current_hp_fraction),
            "status": str(battle.active_pokemon.status) if battle.active_pokemon.status else None,
            "boosts": {k: v for k, v in battle.active_pokemon.boosts.items() if v != 0},
            "effects": [str(effect) for effect in battle.active_pokemon.effects],
        }
        # Add stats if available (flatten the dict)
        if battle.active_pokemon.stats:
            stats = {k: v for k, v in battle.active_pokemon.stats.items() if v is not None}
            if stats:
                active_data["stats"] = stats
        obs["active_pokemon"] = active_data

    # Team status summary (simplified - just species and status if any)
    team_status = {}
    for pokemon in battle.team.values():
        if pokemon.status:
            team_status[pokemon.species] = str(pokemon.status)
    if team_status:
        obs["team"] = team_status

    # Opponent Active Pokemon
    if battle.opponent_active_pokemon:
        opp_data = {
            "species": str(battle.opponent_active_pokemon.species),
            "level": battle.opponent_active_pokemon.level,
            "ability": str(battle.opponent_active_pokemon.ability),
            "item": str(battle.opponent_active_pokemon.item),
            "current_hp_fraction": "{:.2%}".format(battle.opponent_active_pokemon.current_hp_fraction),
            "status": str(battle.opponent_active_pokemon.status) if battle.opponent_active_pokemon.status else None,
            "boosts": {k: v for k, v in battle.opponent_active_pokemon.boosts.items() if v != 0},
            "moves": list(battle.opponent_active_pokemon.moves.keys()),
            "effects": [str(effect) for effect in battle.opponent_active_pokemon.effects],
        }
        # Only add stats if we know them (not all None)
        if battle.opponent_active_pokemon.stats:
            stats = {k: v for k, v in battle.opponent_active_pokemon.stats.items() if v is not None}
            if stats:
                opp_data["stats"] = stats
        obs["opponent_active_pokemon"] = opp_data

    # Opponent team status
    opp_team_status = {}
    for pokemon in battle.opponent_team.values():
        if pokemon.status:
            opp_team_status[pokemon.species] = str(pokemon.status)
    if opp_team_status:
        obs["opponent_team"] = opp_team_status

    # Remove all empty/null values
    return remove_empty_values(obs)


def create_team_array(battle: Battle):
    """
    Create a token-optimized team array with flattened structure.
    Converts from dict to array format for TOON compatibility.
    """
    team = []
    for pokemon in battle.team.values():
        poke_data = {
            "species": pokemon.species,
            "level": pokemon.level,
            "ability": str(pokemon.ability),
            "item": str(pokemon.item),
            "current_hp": pokemon.current_hp,
            "max_hp": pokemon.max_hp,
            "current_hp_fraction": "{:.2%}".format(pokemon.current_hp_fraction),
            "is_active": pokemon == battle.active_pokemon,
            "fainted": pokemon.fainted,
        }

        # Add status only if present
        if pokemon.status:
            poke_data["status"] = str(pokemon.status)

        # Flatten stats directly into pokemon object
        if pokemon.stats:
            for stat_name, stat_value in pokemon.stats.items():
                if stat_value is not None:
                    poke_data[stat_name] = stat_value

        # Add types
        poke_data["types"] = [str(type_) for type_ in pokemon.types]

        # Add boosts only if non-zero
        non_zero_boosts = {k: v for k, v in pokemon.boosts.items() if v != 0}
        if non_zero_boosts:
            poke_data["boosts"] = non_zero_boosts

        # Add moves with PP info (only include if not at max PP to save tokens)
        moves_info = []
        for move_id, move in pokemon.moves.items():
            if move.current_pp < move.max_pp:
                moves_info.append({
                    "id": move_id,
                    "pp": move.current_pp,
                    "max_pp": move.max_pp
                })
            else:
                # Just the move ID if at full PP
                moves_info.append({"id": move_id})
        if moves_info:
            poke_data["moves"] = moves_info

        # Add effects only if present
        if pokemon.effects:
            poke_data["effects"] = [str(effect) for effect in pokemon.effects]

        team.append(poke_data)

    return remove_empty_values({"player_team": team})


# Keep old function for backwards compatibility if needed
def create_team_dictionary(battle: Battle):
    """Deprecated: Use create_team_array() instead for better token efficiency."""
    return create_team_array(battle)


def create_action_context(battle: Battle):
    """
    Create a simplified action context that doesn't duplicate data from observations.
    Only includes moves and switches available right now.
    """
    return remove_empty_values({
        "moves": [move.id for move in battle.available_moves],
        "switches": [pokemon.species for pokemon in battle.available_switches]
    })


def encode_to_toon(data, indent=1):
    """
    Wrapper around TOON encoder with optimal settings for LLM prompts.
    Uses single-space indentation and comma delimiter for maximum token efficiency.
    """
    try:
        return toon_encode(data, {"indent": indent, "delimiter": ","})
    except Exception as e:
        # Fallback to JSON if TOON encoding fails
        return json.dumps(data, indent=indent)


def load_yaml(yaml_path="prompts.yaml"):
    with open(yaml_path, 'r', encoding="utf-8") as f:
        return yaml.safe_load(f)


def log_battle_interaction(model_name, messages, response, outcome, is_valid_response=True):
    """
    Log battle interactions to JSONL files organized by model and outcome.

    Args:
        model_name: Name of the model (will be sanitized for filename)
        messages: List of messages sent to the AI
        response: The AI's response (dict or string)
        outcome: "win", "loss", or None (for ongoing/unknown)
        is_valid_response: Whether the response conformed to the expected schema
    """
    # Create logs directory if it doesn't exist
    logs_dir = "battle_logs"
    os.makedirs(logs_dir, exist_ok=True)

    # Sanitize model name for filename (replace / and \ with _)
    safe_model_name = model_name.replace("/", "_").replace("\\", "_").replace(":", "_")

    # Determine which file to write to based on outcome and validity
    if not is_valid_response:
        filename = f"{safe_model_name}_invalid.jsonl"
    elif outcome == "win":
        filename = f"{safe_model_name}_wins.jsonl"
    elif outcome == "loss":
        filename = f"{safe_model_name}_losses.jsonl"
    else:
        # Don't log ongoing moves - only log when we know the outcome
        return

    filepath = os.path.join(logs_dir, filename)

    # Prepare log entry
    log_entry = {
        "model": model_name,
        "messages": messages,
        "response": response,
        "outcome": outcome if is_valid_response else "invalid",
        "is_valid_response": is_valid_response
    }

    # Append to JSONL file (one JSON object per line, no indentation)
    with open(filepath, 'a', encoding='utf-8') as f:
        json.dump(log_entry, f, ensure_ascii=False)
        f.write("\n")

if __name__ == "__main__":
    print(load_yaml())