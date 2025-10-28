from random_team_builder import RandomTeamBuilder
from tournament import cross_evaluate_with_random_teams, print_results
import asyncio


# Model configurations - easy to add/remove models
MODEL_CONFIGS = [
    # {
    #     "type": "local",
    #     "model": "qwen3:14b",
    #     "username": "qwen3_14b",
    #     "verbosity": True
    # },
    # {
    #     "type": "router",
    #     "model": "openai/gpt-5-nano",
    #     "username": "gpt_5",
    #     "verbosity": True
    # },
    {
        "type": "router",
        "model": "google/gemini-2.5-flash",
        "username": "Gemini_Flash",
        "verbosity": True
    },
    {
        "type": "router",
        "model": "x-ai/grok-4-fast",
        "username": "grok4_fast",
        "verbosity": True
    },
    {
        "type": "router",
        "model": "deepseek/deepseek-v3.2-exp",
        "username": "deepseek",
        "verbosity": True
    },
    {
        "type": "simple",
        "username": "simple_player"
    },
    # {
    #     "type": "max",
    #     "username": "max_damage_player"
    # }
]

# Tournament configuration variables
BUILDS_FILE = "pokemon_builds.txt"
FILTER_FORMAT = "doubles"
TEAM_SIZE = 4
N_CHALLENGES = 5
BATTLE_FORMAT = "gen3ubers"


async def main():
    # Initialize team builder
    print("Initializing Random Team Builder...")
    team_builder = RandomTeamBuilder(
        builds_file=BUILDS_FILE,
        filter_format=FILTER_FORMAT,
    )

    # Run cross-evaluation with random teams for each match
    cross_evaluation = await cross_evaluate_with_random_teams(
        player_configs=MODEL_CONFIGS,
        team_builder=team_builder,
        n_challenges=N_CHALLENGES,
        battle_format=BATTLE_FORMAT,
        team_size=TEAM_SIZE
    )

    # Print results
    print_results(cross_evaluation, MODEL_CONFIGS, N_CHALLENGES)


if __name__ == "__main__":
    asyncio.run(main())
