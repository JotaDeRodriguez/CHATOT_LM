import json
import os
from poke_env.player import Player
from ollama_chat import local_choose_action
from open_router_chat import router_choose_action
from poke_env.battle import Battle
from colorama import init, Fore
from utils import (create_observation_dictionary, create_team_array, create_action_context,
                   encode_to_toon, load_yaml, log_battle_interaction)

init(autoreset=True)

class AIPlayer(Player):
    def __init__ (self, model, provider, verbosity=False, account_configuration=None, team=None, battle_format=None, log_length=15, max_concurrent_battles=0, max_turns=25):
        super().__init__(account_configuration=account_configuration, team=team, battle_format=battle_format, max_concurrent_battles=max_concurrent_battles)
        self.model = model
        self._provider = provider  # 'local' or 'router'
        self.verbosity = verbosity
        self.log_length = log_length
        self.max_turns = max_turns
        # Store battle interactions to log when battle finishes
        self.battle_interactions = {}
        # Store scratchpad content per battle for context persistence
        self.battle_scratchpads = {}

    @classmethod
    def local(cls, model, verbosity=False, account_configuration=None, team=None, battle_format=None, log_length=10, max_concurrent_battles=0, max_turns=25):
        """Create an AIPlayer that uses local Ollama models"""
        return cls(
            model=model,
            provider='local',
            verbosity=verbosity,
            account_configuration=account_configuration,
            team=team,
            battle_format=battle_format,
            log_length=log_length if log_length is not None else 25,
            max_concurrent_battles=max_concurrent_battles,
            max_turns=max_turns
        )

    @classmethod
    def router(cls, model, verbosity=False, account_configuration=None, team=None, battle_format=None, log_length=None, max_concurrent_battles=0, max_turns=25):
        """Create an AIPlayer that uses OpenRouter models"""
        return cls(
            model=model,
            provider='router',
            verbosity=verbosity,
            account_configuration=account_configuration,
            team=team,
            battle_format=battle_format,
            log_length=log_length if log_length is not None else 100,
            max_concurrent_battles=max_concurrent_battles,
            max_turns=max_turns
        )

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

        # Add battle log (plain text - already optimal)
        prompt_parts.append("Battle Log (Recent Events):")
        for msg in recent_messages:
            prompt_parts.append(f"  {msg}")

        # Use TOON encoding for structured data to save tokens
        observations = create_observation_dictionary(battle)
        prompt_parts.append("Observations:")
        prompt_parts.append(encode_to_toon(observations))

        team_info = create_team_array(battle)
        prompt_parts.append("Team Status:")
        prompt_parts.append(encode_to_toon(team_info))

        # Add available actions (simplified - no duplication of moves already in team/observations)
        available_actions = create_action_context(battle)
        prompt_parts.append("Available Actions:")
        prompt_parts.append(encode_to_toon(available_actions))

        # Add scratchpad from previous turn if it exists
        if battle_tag in self.battle_scratchpads:
            prompt_parts.append(f"Scratchpad (from previous turn):\n{self.battle_scratchpads[battle_tag]}")

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
        # Check if turn limit exceeded
        if battle.turn > self.max_turns:
            if self.verbosity:
                print(Fore.YELLOW + f"Turn limit ({self.max_turns}) exceeded. Forfeiting battle.")
            try:
                await self.ps_client.send_message(message="/forfeit", room=battle.battle_tag)
            except Exception:
                pass
            # Return a random move as fallback (forfeit command should end the battle)
            return self.choose_random_move(battle)

        battle_message = self.write_prompt(battle=battle)
        ai_decision = await self.ask_ai_model(battle_message)

        # Ensure ai_decision is a dict
        if not isinstance(ai_decision, dict):
            if self.verbosity:
                print(Fore.RED + f"AI returned invalid type: {type(ai_decision)}. Value: {ai_decision}")
            ai_decision = {"reasoning": "Invalid response type", "action": None}

        # Append scratchpad if provided
        if ai_decision.get("scratchpad"):
            # Convert scratchpad to string if it's a dict
            scratchpad_str = ai_decision["scratchpad"]
            if isinstance(scratchpad_str, dict):
                scratchpad_str = json.dumps(scratchpad_str, indent=2)
            elif not isinstance(scratchpad_str, str):
                scratchpad_str = str(scratchpad_str)

            if battle.battle_tag in self.battle_scratchpads:
                self.battle_scratchpads[battle.battle_tag] += "\n\n" + scratchpad_str
            else:
                self.battle_scratchpads[battle.battle_tag] = scratchpad_str

        # Store interaction to log when battle finishes
        if battle.battle_tag not in self.battle_interactions:
            self.battle_interactions[battle.battle_tag] = []

        # Create interaction entry
        interaction = {
            "messages": battle_message,
            "response": ai_decision,
            "is_valid_response": False
        }

        self.battle_interactions[battle.battle_tag].append(interaction)

        # TODO Replace for proper logging
        if self.verbosity:
            # print("-"*30)
            # print(f"Full prompt: {battle_message}\n")
            print(f"{(self.model).split("/")[-1]}:")
            if ai_decision.get("scratchpad"):
                print(f"Scratchpad: {ai_decision.get("scratchpad")}")
            print(f"Decision: {ai_decision.get("reasoning")}")
            print(f"Action: {ai_decision.get("action")}")


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
        Call AI model to get battle decision (local or router based on provider)
        """
        try:
            if self._provider == 'local':
                # Call Ollama
                response = await local_choose_action(battle_message, self.model)
                try:
                    decision = json.loads(response)
                    return decision
                except json.JSONDecodeError:
                    return {"reasoning": "Failed to parse response", "action": None}

            elif self._provider == 'router':
                # Call OpenRouter
                response = await router_choose_action(battle_message, self.model)
                try:
                    decision = json.loads(response)
                    # Ensure decision is a dict
                    if not isinstance(decision, dict):
                        if self.verbosity:
                            print(Fore.RED + f"AI response parsed but not a dict: {type(decision)} = {decision}")
                        return {"reasoning": "Response not a dict", "action": None}
                    return decision
                except json.JSONDecodeError as e:
                    if self.verbosity:
                        print(Fore.RED + f"Failed to parse AI response as JSON: {str(e)}")
                        print(Fore.RED + f"Response was: {response[:200]}")
                    return {"reasoning": "Failed to parse response", "action": None}

            else:
                raise ValueError(f"Unknown provider: {self._provider}")

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

        # Clean up scratchpad for this battle
        if battle.battle_tag in self.battle_scratchpads:
            del self.battle_scratchpads[battle.battle_tag]

