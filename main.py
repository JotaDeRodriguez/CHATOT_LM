import asyncio
import random
from ai_players import AIPlayer
from poke_env import AccountConfiguration
from poke_env.player import RandomPlayer, SimpleHeuristicsPlayer, MaxBasePowerPlayer
from random_team_builder import RandomTeamBuilder

# Tournament configuration variables
BUILDS_FILE = "pokemon_builds.txt"
FILTER_FORMAT = "doubles"
INCLUDE_FORMATS=["OU", "UBER"]
TEAM_SIZE = 4
BATTLE_FORMAT = "gen3ubers"

team_builder = RandomTeamBuilder(
        builds_file=BUILDS_FILE,
        filter_format=FILTER_FORMAT,
        include_formats=INCLUDE_FORMATS
    )

# Generate teams for each player
team_assignments = {
    'gemma': team_builder.generate_random_team(TEAM_SIZE),
    'qwen': team_builder.generate_random_team(TEAM_SIZE),
    'gemini': team_builder.generate_random_team(TEAM_SIZE),
    'gpt5': team_builder.generate_random_team(TEAM_SIZE),
    'gpt_oss': team_builder.generate_random_team(TEAM_SIZE),
    'qwen_32b': team_builder.generate_random_team(TEAM_SIZE),
    'grok': team_builder.generate_random_team(TEAM_SIZE),
    'random': team_builder.generate_random_team(TEAM_SIZE),
    'simple': team_builder.generate_random_team(TEAM_SIZE),
    'max': team_builder.generate_random_team(TEAM_SIZE),
}

### LOCAL AI ###

gemma_player = AIPlayer.local(model="gemma3:12b", verbosity=True,
                              account_configuration=AccountConfiguration("gemma3_12b", None),
                              battle_format="gen3ubers",
                              team=team_assignments['gemma'])

qwen_player = AIPlayer.local(model="qwen3:14b", verbosity=True,
                             account_configuration=AccountConfiguration("qwen3_14b", None),
                             battle_format="gen3ubers",
                             team=team_assignments['qwen'])


### OPEN ROUTER ###

gemini_flash_player = AIPlayer.router(model="google/gemini-2.5-flash",
                                      verbosity=True,
                                      account_configuration=AccountConfiguration("Gemini_Flash", None),
                                      battle_format="gen3ubers",
                                      team=team_assignments['gemini'])

gpt_5_player = AIPlayer.router(model="openai/gpt-5-nano",
                               verbosity=True,
                               account_configuration=AccountConfiguration("gpt_5", None),
                               battle_format="gen3ubers",
                               team=team_assignments['gpt5'])

gpt_oss_player = AIPlayer.router(model="openai/gpt-oss-120b",
                                 verbosity=True,
                                 account_configuration=AccountConfiguration("gpt_oss", None),
                                 battle_format="gen3ubers",
                                 team=team_assignments['gpt_oss'])

qwen_3_32b_player = AIPlayer.router(model="qwen/qwen3-32b",
                                    verbosity=True,
                                    account_configuration=AccountConfiguration("qwen_3_32_b", None),
                                    battle_format="gen3ubers",
                                    team=team_assignments['qwen_32b'])

grok_4_player = AIPlayer.router(model="x-ai/grok-4-fast",
                                verbosity=True,
                                account_configuration=AccountConfiguration("grok_4_fast", None),
                                battle_format="gen3ubers",
                                team=team_assignments['grok'])


### DEFAULTS ###

random_player = RandomPlayer(account_configuration=AccountConfiguration("random_player", None),
                            battle_format="gen3ubers",
                            team=team_assignments['random'],
                            max_concurrent_battles=0) # Unlimited concurrency

simple_player = SimpleHeuristicsPlayer(account_configuration=AccountConfiguration("simple_player", None),
                                      battle_format="gen3ubers",
                                      team=team_assignments['simple'],
                                      max_concurrent_battles=0)

max_player = MaxBasePowerPlayer(account_configuration=AccountConfiguration("max_damage_player", None),
                               battle_format="gen3ubers",
                               team=team_assignments['max'],
                               max_concurrent_battles=0)

async def main():
    # await gemma_player.accept_challenges(opponent=None, n_challenges=1)
    await grok_4_player.battle_against(gemma_player, n_battles=1)

if __name__ == "__main__":
    asyncio.run(main())