import asyncio
from ai_players import Local_AIPlayer, Router_AIPlayer
from poke_env import AccountConfiguration
from poke_env.player import RandomPlayer
from teams import groudon, metagross

gemma_player = Local_AIPlayer(model="gemma3:4b", account_configuration=AccountConfiguration("AI_Player_Gemma", None))


gemini_flash_player = Router_AIPlayer(model="google/gemini-2.5-flash", 
                                      verbosity=True,
                                      account_configuration=AccountConfiguration("Gemini_Flash", None), # Add password for messages
                                    #   battle_format="gen3ubers",
                                    #   team=groudon)
)


gpt_5_player = Router_AIPlayer(model="openai/gpt-5", account_configuration=AccountConfiguration("GPT_5_mini", None))
gpt_oss_player = Router_AIPlayer(model="openai/gpt-oss-120b", account_configuration=AccountConfiguration("gpt_oss_player", None))

random_player = RandomPlayer(account_configuration=AccountConfiguration("random_player", None), battle_format="gen3ubers", team=metagross)

async def main():
    await gpt_5_player.accept_challenges(opponent=None, n_challenges=1)
    # await gemini_flash_player.battle_against(random_player, n_battles=1)

asyncio.run(main())