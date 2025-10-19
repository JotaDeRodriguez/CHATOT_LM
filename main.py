import asyncio
import random
from ai_players import Local_AIPlayer, Router_AIPlayer
from poke_env import AccountConfiguration
from poke_env.player import RandomPlayer, SimpleHeuristicsPlayer, MaxBasePowerPlayer
from teams import *

# Randomly assign teams to players
all_teams = [team_1, team_2, team_3, team_4, team_5, team_6, team_7]
random.shuffle(all_teams)

# Assign teams sequentially from shuffled list
team_assignments = {
    'gemma': all_teams[0] if len(all_teams) > 0 else team_1,
    'qwen': all_teams[1] if len(all_teams) > 1 else team_2,
    'gemini': all_teams[2] if len(all_teams) > 2 else team_3,
    'gpt5': all_teams[3] if len(all_teams) > 3 else team_4,
    'gpt_oss': all_teams[4] if len(all_teams) > 4 else team_5,
    'qwen_32b': all_teams[5] if len(all_teams) > 5 else team_6,
    'grok': all_teams[6] if len(all_teams) > 6 else team_7,
    'random': random.choice(all_teams),
    'simple': random.choice(all_teams),
    'max': random.choice(all_teams),
}

print("Team Assignments:")
for player, team in team_assignments.items():
    # More robust team name extraction
    try:
        # Try splitting by actual newline character
        lines = team.split('\n')
        if len(lines) > 1:
            team_name = lines[1].split('@')[0].strip()
        else:
            # Fallback: just show first few characters
            team_name = team[:30].replace('\n', ' ')
        print(f"{player}: {team_name}'s team")
    except (IndexError, AttributeError):
        print(f"{player}: Team assigned")
print()

### LOCAL AI ###

gemma_player = Local_AIPlayer(model="gemma3:12b", verbosity=True,
                                      account_configuration=AccountConfiguration("gemma3_12b", None),
                                      battle_format="gen3ubers",
                                      log_length=25,
                                      team=team_assignments['gemma'])

qwen_player = Local_AIPlayer(model="qwen3:14b", verbosity=True,
                                      account_configuration=AccountConfiguration("qwen3_14b", None),
                                      battle_format="gen3ubers",
                                      team=team_assignments['qwen'])


### OPEN ROUTER ###

gemini_flash_player = Router_AIPlayer(model="google/gemini-2.5-flash", 
                                      verbosity=True,
                                      account_configuration=AccountConfiguration("Gemini_Flash", None),
                                      battle_format="gen3ubers",
                                      team=team_assignments['gemini'])

gpt_5_player = Router_AIPlayer(model="openai/gpt-5-mini",  
                               verbosity=True,
                                account_configuration=AccountConfiguration("gpt_5", None), 
                                battle_format="gen3ubers",
                                team=team_assignments['gpt5'])

gpt_oss_player = Router_AIPlayer(model="openai/gpt-oss-120b",  
                                verbosity=True,
                                account_configuration=AccountConfiguration("gpt_oss", None),
                                battle_format="gen3ubers",
                                team=team_assignments['gpt_oss'])

qwen_3_32b_player = Router_AIPlayer(model="qwen/qwen3-32b",  
                                verbosity=True,
                                account_configuration=AccountConfiguration("qwen_3_32_b", None),
                                battle_format="gen3ubers",
                                team=team_assignments['qwen_32b'])

grok_4_player = Router_AIPlayer(model="x-ai/grok-4-fast",  
                                verbosity=True,
                                account_configuration=AccountConfiguration("grok_4_fast", None),
                                battle_format="gen3ubers",
                                team=team_assignments['grok'])


### DEFAULTS ###

random_player = RandomPlayer(account_configuration=AccountConfiguration("random_player", None), 
                            battle_format="gen3ubers", 
                            team=team_assignments['random'])

simple_player = SimpleHeuristicsPlayer(account_configuration=AccountConfiguration("simple_player", None), 
                                      battle_format="gen3ubers", 
                                      team=team_assignments['simple'])

max_player = MaxBasePowerPlayer(account_configuration=AccountConfiguration("max_damage_player", None), 
                               battle_format="gen3ubers", 
                               team=team_assignments['max'])

async def main():
    # await gemma_player.accept_challenges(opponent=None, n_challenges=1)
    await gemma_player.battle_against(simple_player, n_battles=1)

if __name__ == "__main__":
    asyncio.run(main())