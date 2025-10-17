import json
from poke_env.player import Player
from ollama_chat import local_choose_action
from open_router_chat import router_choose_action

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

        print(battle_message)

        # Get AI decision
        ai_decision = await self.ask_ai_model(battle_message)
        print(f"AI Decision: {ai_decision}")

        # Send reasoning as a message to the battle room
        if ai_decision.get("reasoning"):
            await self.ps_client.send_message(ai_decision["reasoning"], battle.battle_tag)

        # Execute the decision
        if ai_decision.get("action"):
            action = ai_decision["action"]

            if action.get("action_type") == "move":
                move_name = action.get("move_name")
                # Find the move in available moves
                for move in battle.available_moves:
                    if move.id == move_name:
                        return self.create_order(move)

            elif action.get("action_type") == "switch":
                pokemon_species = action.get("pokemon_species")
                # Find the pokemon to switch to
                for pokemon in battle.available_switches:
                    if pokemon.species == pokemon_species:
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

        print(battle_message)

        # Get AI decision
        ai_decision = await self.ask_ai_model(battle_message)
        print(f"AI Decision: {ai_decision}")

        # Send reasoning as a message to the battle room
        if ai_decision.get("reasoning"):
            await self.ps_client.send_message(ai_decision["reasoning"], battle.battle_tag)

        # Execute the decision
        if ai_decision.get("action"):
            action = ai_decision["action"]

            if action.get("action_type") == "move":
                move_name = action.get("move_name")
                # Find the move in available moves
                for move in battle.available_moves:
                    if move.id == move_name:
                        return self.create_order(move)

            elif action.get("action_type") == "switch":
                pokemon_species = action.get("pokemon_species")
                # Find the pokemon to switch to
                for pokemon in battle.available_switches:
                    if pokemon.species == pokemon_species:
                        return self.create_order(pokemon)

        # Fallback to random if AI decision fails
        return self.choose_random_move(battle)
    
    async def ask_ai_model(self, battle_message):
        """
        Call Ollama to get AI battle decision
        """
        # Await the async function
        response = await router_choose_action(battle_message, self.model)

        try:
            decision = json.loads(response)
            return decision
        except json.JSONDecodeError:
            return {"reasoning": "Failed to parse response", "action": None}

