import json
import os
from poke_env.player import Player
from ollama_chat import local_choose_action
from open_router_chat import router_choose_action
from poke_env.battle import Battle
from colorama import init, Fore
from utils import create_observation_dictionary, create_team_dictionary, load_yaml, log_battle_interaction

init(autoreset=True)

class Local_AIPlayer(Player):
    def __init__ (self, model, verbosity=False, account_configuration=None, team=None, battle_format=None, log_length=25):
        super().__init__(account_configuration=account_configuration, team=team, battle_format=battle_format)
        self.model = model
        self.verbosity = verbosity
        self.log_length = log_length
        # Store battle interactions to log when battle finishes
        self.battle_interactions = {}

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
        recent_messages = battle_log[-self.log_length:] if len(battle_log) > self.log_length else battle_log

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

        # Store interaction to log when battle finishes (will update validity later)
        if battle.battle_tag not in self.battle_interactions:
            self.battle_interactions[battle.battle_tag] = []

        # Create interaction entry (will be updated with validity)
        interaction = {
            "messages": battle_message,
            "response": ai_decision,
            "is_valid_response": False  # Will be updated if action succeeds
        }

        self.battle_interactions[battle.battle_tag].append(interaction)

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
                    interaction["is_valid_response"] = True
                    return self.create_order(move)

            # If not a move, try to find it as a pokemon to switch to
            for pokemon in battle.available_switches:
                if pokemon.species == action_name:
                    interaction["is_valid_response"] = True
                    return self.create_order(pokemon)

        # Fallback to random if AI decision fails
        if self.verbosity:
            print(Fore.RED +"Error in decision response. Defaulting to a random choice")
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

    def _battle_finished_callback(self, battle: Battle):
        """
        Called when a battle finishes. Logs all interactions with the outcome.
        """
        if battle.battle_tag in self.battle_interactions:
            outcome = "win" if battle.won else "loss"

            for interaction in self.battle_interactions[battle.battle_tag]:
                log_battle_interaction(
                    model_name=self.model,
                    messages=interaction["messages"],
                    response=interaction["response"],
                    outcome=outcome,
                    is_valid_response=interaction["is_valid_response"]
                )

            # Clean up stored interactions for this battle
            del self.battle_interactions[battle.battle_tag]



class Router_AIPlayer(Player):
    def __init__ (self, model, verbosity=False, account_configuration=None, team=None, battle_format=None, log_length=100):
        super().__init__(account_configuration=account_configuration, team=team, battle_format=battle_format)
        self.model = model
        self.verbosity = verbosity
        self.log_length = log_length
        # Store battle interactions to log when battle finishes
        self.battle_interactions = {}


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
        recent_messages = battle_log[-self.log_length:] if len(battle_log) > self.log_length else battle_log

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

        # Store interaction to log when battle finishes (will update validity later)
        if battle.battle_tag not in self.battle_interactions:
            self.battle_interactions[battle.battle_tag] = []

        # Create interaction entry (will be updated with validity)
        interaction = {
            "messages": battle_message,
            "response": ai_decision,
            "is_valid_response": False  # Will be updated if action succeeds
        }

        self.battle_interactions[battle.battle_tag].append(interaction)

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
                    interaction["is_valid_response"] = True
                    return self.create_order(move)

            # If not a move, try to find it as a pokemon to switch to
            for pokemon in battle.available_switches:
                if pokemon.species == action_name:
                    interaction["is_valid_response"] = True
                    return self.create_order(pokemon)

        # Fallback to random if AI decision fails
        if self.verbosity:
            print(Fore.RED +"Error in decision response. Defaulting to a random choice")
        return self.choose_random_move(battle)

    async def ask_ai_model(self, battle_message):
        """
        Call OpenRouter to get AI battle decision
        """
        try:
            # Await the async function
            response = await router_choose_action(battle_message, self.model)

            try:
                decision = json.loads(response)
                return decision
            except json.JSONDecodeError as e:
                if self.verbosity:
                    print(Fore.RED + f"Failed to parse AI response as JSON: {str(e)}")
                return {"reasoning": "Failed to parse response", "action": None}

        except Exception as e:
            if self.verbosity:
                print(Fore.RED + f"Error calling AI model: {str(e)}")
            return {"reasoning": f"API error: {str(e)}", "action": None}

    def _battle_finished_callback(self, battle: Battle):
        """
        Called when a battle finishes. Logs all interactions with the outcome.
        """
        if battle.battle_tag in self.battle_interactions:
            outcome = "win" if battle.won else "loss"

            for interaction in self.battle_interactions[battle.battle_tag]:
                log_battle_interaction(
                    model_name=self.model,
                    messages=interaction["messages"],
                    response=interaction["response"],
                    outcome=outcome,
                    is_valid_response=interaction["is_valid_response"]
                )

            # Clean up stored interactions for this battle
            del self.battle_interactions[battle.battle_tag]

