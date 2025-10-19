import json
from poke_env.player import Player
from ollama_chat import local_choose_action
from open_router_chat import router_choose_action
from poke_env.battle import Battle
from colorama import init, Fore

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

    async def choose_move(self, battle: Battle):

        battle_message = "\n\n===Recent Battle History ==="
        # Get all battle events from observations
        #TODO Maybe Cleanup messages
        #TODO add opposing team observation, status, etc.

        all_events = []
        for turn_num in sorted(battle.observations.keys()):
            for event in battle.observations[turn_num].events:
                # Format event as a string (join the split message parts with |)
                if "html" not in event:
                    all_events.append("|".join(event))

        # Get last n events
        recent_messages = all_events[-100:] if len(all_events) > 100 else all_events
        for msg in recent_messages:
            battle_message += f"\n  {msg}"

        battle_message += f"""\n=== Current State (Turn {battle.turn}) ===

My Active Pokemon:
species: {battle.active_pokemon.species}
hp: {battle.active_pokemon.current_hp_fraction:.1%}
available_moves:"""
        if battle.available_moves:
            for move in battle.available_moves:
                battle_message += f"\n    - {move.id}: type={move.type}, power={move.base_power}"
        if battle.active_pokemon.status: 
            battle_message += f"The current status of your pokemon is {battle.active_pokemon.status}"

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

        battle_message += "\n\nOpponents team: "
        battle_message += f"{battle.opponent_team}"

        ai_decision = await self.ask_ai_model(battle_message)

        # TODO Replace for proper logging
        if self.verbosity:
            print(battle_message)
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

