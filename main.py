import asyncio
from ai_players import Local_AIPlayer, Router_AIPlayer
from poke_env import AccountConfiguration
from poke_env.player import RandomPlayer, SimpleHeuristicsPlayer
from teams import groudon, metagross

gemma_player = Local_AIPlayer(model="gemma3:4b", account_configuration=AccountConfiguration("AI_Player_Gemma", None))


gemini_flash_player = Router_AIPlayer(model="google/gemini-2.5-flash", 
                                      verbosity=True,
                                      account_configuration=AccountConfiguration("Gemini_Flash", None), # Add password for messages
                                      battle_format="gen3ubers",
                                      team=groudon)

open_router_gemma_player = Router_AIPlayer(model="google/gemma-3-12b-it", 
                                      verbosity=True,
                                      account_configuration=AccountConfiguration("Gemini_Gemma_3b", None), # Add password for messages
                                      battle_format="gen3ubers",
                                      team=groudon)


gpt_5_player = Router_AIPlayer(model="openai/gpt-5",  
                               verbosity=True,
                                account_configuration=AccountConfiguration("gpt_5", None), 
                                battle_format="gen3ubers",
                                team=groudon)

gpt_oss_player = Router_AIPlayer(model="openai/gpt-oss-120b",  
                                verbosity=True,
                                account_configuration=AccountConfiguration("gpt_oss", None),
                                battle_format="gen3ubers",
                                team=groudon)

qwen_3_32b_player = Router_AIPlayer(model="qwen/qwen3-32b",  
                                verbosity=True,
                                account_configuration=AccountConfiguration("qwen_3_32_b", None),
                                battle_format="gen3ubers",
                                team=groudon)


random_player = RandomPlayer(account_configuration=AccountConfiguration("random_player", None), battle_format="gen3ubers", team=groudon)
simple_player = SimpleHeuristicsPlayer(account_configuration=AccountConfiguration("simple_player", None), battle_format="gen3ubers", team=groudon)

async def main():
    await gpt_5_player.accept_challenges(opponent=None, n_challenges=1)
    # await qwen_3_32b_player.battle_against(simple_player, n_battles=5)

asyncio.run(main())