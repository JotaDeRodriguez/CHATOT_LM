import asyncio
from ai_players import Local_AIPlayer, Router_AIPlayer
from poke_env import AccountConfiguration

gemma_player = Local_AIPlayer(model="gemma3:4b", account_configuration=AccountConfiguration("AI_Player_Gemma", None))

gemini_flash_player = Router_AIPlayer(model="google/gemini-2.5-flash", account_configuration=AccountConfiguration("AI_Player_Gemini", None))

async def main():
    # await gemini_flash_player.accept_challenges(opponent=None, n_challenges=1)
    await gemma_player.battle_against(gemini_flash_player, n_battles=1)

asyncio.run(main())