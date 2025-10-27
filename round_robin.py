from poke_env import cross_evaluate
from main import *
from tabulate import tabulate


players = [qwen_player,
           gpt_5_player,
           gemini_flash_player,
           grok_4_player,
           random_player,
           simple_player,
           max_player]

async def main():
    cross_evaluation = await cross_evaluate(players, n_challenges=3)
    table = [["-"] + [p.username for p in players]]
    for p_1, results in cross_evaluation.items():
        row = [p_1]
        for p_2 in results:
            win_rate = cross_evaluation[p_1][p_2]
            # Display "-" for self-play (diagonal entries)
            row.append("-" if win_rate is None else f"{win_rate:.2f}")
        table.append(row)

    print(tabulate(table))


if __name__ == "__main__":
    asyncio.run(main())