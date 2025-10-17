import asyncio
from ai_player import AIPlayer
from poke_env import AccountConfiguration

async def main():
    ai_player = AIPlayer(
        account_configuration=AccountConfiguration("AI_Player_1232123", None))
    
    await ai_player.accept_challenges(opponent=None, n_challenges=1)

asyncio.run(main())