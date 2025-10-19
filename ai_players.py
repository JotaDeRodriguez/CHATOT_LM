import json
import os
from poke_env.player import Player
from ollama_chat import local_choose_action
from open_router_chat import router_choose_action
from poke_env.battle import Battle
from colorama import init, Fore
from utils import create_observation_dictionary, create_team_dictionary, load_yaml

init(autoreset=True)

#TODO apply changes of Router player
class Local_AIPlayer(Player):
    def __init__ (self, model, account_configuration=None):
        super().__init__(account_configuration=account_configuration)
        self.model = model

    async def choose_move(self, battle):
        # Create YAML-like battle state message
        battle_message = f"""=== Battle State (Turn {battle.turn}) ===

My Active Pokemon:
  species: {battle.active_pokemon.species}
  hp: {battle.active_pokemon.current_hp_fraction:.1%}
  available_moves:"""

        for move in battle.available_moves:
            battle_message += f"\n    - {move.id}: type={move.type}, power={move.base_power}"

        battle_message += f"""

Opponent Active Pokemon:
  species: {battle.opponent_active_pokemon.species}
  hp: {battle.opponent_active_pokemon.current_hp_fraction:.1%}

My Team:"""

        for pokemon in battle.team.values():
            battle_message += f"\n  - {pokemon.species}: hp={pokemon.current_hp_fraction:.1%}"

        battle_message += "\n\nAvailable Switches:"
        for pokemon in battle.available_switches:
            battle_message += f"\n  - {pokemon.species}"

        # Get AI decision
        ai_decision = await self.ask_ai_model(battle_message)
        print(f"{self.model}AI Decision: {ai_decision}")

        # Send reasoning as a message to the battle room
        if ai_decision.get("reasoning"):
            try:
                await self.ps_client.send_message(message=ai_decision["reasoning"], room=battle.battle_tag)
            except Exception:
                # Silently ignore chat errors (e.g., unregistered accounts)
                pass

        # Execute the decision
        if ai_decision.get("action"):
            action_name = ai_decision["action"]

            # First try to find it as a move
            for move in battle.available_moves:
                if move.id == action_name:
                    return self.create_order(move)

            # If not a move, try to find it as a pokemon to switch to
            for pokemon in battle.available_switches:
                if pokemon.species == action_name:
                    return self.create_order(pokemon)

        # Fallback to random if AI decision fails
        return self.choose_random_move(battle)
    
    async def ask_ai_model(self, battle_message):
        """
        Call Ollama to get AI battle decision
        """
        # Await the async function
        response = await local_choose_action(battle_message, self.model)

        try:
            decision = json.loads(response)
            return decision
        except json.JSONDecodeError:
            return {"reasoning": "Failed to parse response", "action": None}


class Router_AIPlayer(Player):
    def __init__ (self, model, verbosity=False, account_configuration=None, team=None, battle_format=None):
        super().__init__(account_configuration=account_configuration, team=team, battle_format=battle_format)
        self.model = model
        self.verbosity = verbosity

    def write_prompt(self, battle: Battle):
        system_prompt = load_yaml()
        battle_tag = battle.battle_tag

        # Collect battle log events
        battle_log = []
        for turn_num in sorted(battle.observations.keys()):
            for event in battle.observations[turn_num].events:
                # Format event as a string (join the split message parts with |)
                if "html" not in event:
                    battle_log.append("|".join(event))

        # Get last 100 events
        recent_messages = battle_log[-100:] if len(battle_log) > 100 else battle_log

        # Build the prompt
        prompt_parts = []

        # Add battle log
        prompt_parts.append("Battle Log (Recent Events):")
        for msg in recent_messages:
            prompt_parts.append(f"  {msg}")

        observations = create_observation_dictionary(battle)
        prompt_parts.append(f"Observations:\n{json.dumps(observations, indent=2)}")

        team_info = create_team_dictionary(battle)
        prompt_parts.append(f"Team Status:\n{json.dumps(team_info, indent=2)}")

        # Add available actions
        available_actions = {
            "moves": [move.id for move in battle.available_moves],
            "switches": [pokemon.species for pokemon in battle.available_switches]
        }
        prompt_parts.append(f"Available Actions:\n{json.dumps(available_actions, indent=2)}")

        # Combine all parts with clear separation
        final_prompt = "\n".join(prompt_parts)

        return [
            {
                "role": "system",
                "content": system_prompt["agent"]["system_prompt"]
            },
            {
                "role": "user",
                "content": final_prompt
            }
        ]


    async def choose_move(self, battle: Battle):

        battle_message = self.write_prompt(battle=battle)
        ai_decision = await self.ask_ai_model(battle_message)

        # TODO Replace for proper logging
        if self.verbosity:
            print("-"*30)
            print(f"{(self.model).split("/")[-1]} Decision: {ai_decision}")
            print("-"*30)

        # Send reasoning as a message to the battle room
        if ai_decision.get("reasoning"):
            try:
                await self.ps_client.send_message(message=ai_decision["reasoning"], room=battle.battle_tag)
            except Exception:
                # Silently ignore chat errors (e.g., unregistered accounts)
                pass

        # Execute the decision
        if ai_decision.get("action"):
            action_name = ai_decision["action"].lower()

            # First try to find it as a move
            for move in battle.available_moves:
                if move.id == action_name:
                    return self.create_order(move)

            # If not a move, try to find it as a pokemon to switch to
            for pokemon in battle.available_switches:
                if pokemon.species == action_name:
                    return self.create_order(pokemon)

        # Fallback to random if AI decision fails
        if self.verbosity: 
            print(Fore.RED +"Error in decision response. Defaulting to a random choice")
        return self.choose_random_move(battle)
    
    async def ask_ai_model(self, battle_message):
        """
        Call OpenRouter to get AI battle decision
        """
        # Await the async function
        response = await router_choose_action(battle_message, self.model)

        try:
            decision = json.loads(response)
            return decision
        except json.JSONDecodeError:
            return {"reasoning": "Failed to parse response", "action": None}

