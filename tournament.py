from poke_env import AccountConfiguration
from poke_env.player import RandomPlayer, SimpleHeuristicsPlayer, MaxBasePowerPlayer
from ai_players import AIPlayer
from random_team_builder import RandomTeamBuilder
from tabulate import tabulate
from typing import List, Dict


class PlayerFactory:
    """Factory for creating Pokemon battle players with random teams."""

    def __init__(self, team_builder: RandomTeamBuilder, battle_format: str = "gen3ubers", team_size: int = 4):
        self.team_builder = team_builder
        self.battle_format = battle_format
        self.team_size = team_size

    def create_player(self, config: dict, team: str = None):
        """
        Create a player from configuration.

        Args:
            config: Player configuration dictionary
            team: Optional team string. If None, generates a random team.

        Returns:
            Player instance
        """
        if team is None:
            team = self.team_builder.generate_random_team(team_size=self.team_size)

        account_config = AccountConfiguration(config["username"], None)

        if config["type"] == "local":
            return AIPlayer.local(
                model=config["model"],
                verbosity=config.get("verbosity", False),
                account_configuration=account_config,
                battle_format=self.battle_format,
                team=team,
                max_turns=config.get("max_turns", 25)
            )
        elif config["type"] == "router":
            return AIPlayer.router(
                model=config["model"],
                verbosity=config.get("verbosity", False),
                account_configuration=account_config,
                battle_format=self.battle_format,
                team=team,
                max_turns=config.get("max_turns", 25)
            )
        elif config["type"] == "random":
            return RandomPlayer(
                account_configuration=account_config,
                battle_format=self.battle_format,
                team=team,
                max_concurrent_battles=0
            )
        elif config["type"] == "simple":
            return SimpleHeuristicsPlayer(
                account_configuration=account_config,
                battle_format=self.battle_format,
                team=team,
                max_concurrent_battles=0
            )
        elif config["type"] == "max":
            return MaxBasePowerPlayer(
                account_configuration=account_config,
                battle_format=self.battle_format,
                team=team,
                max_concurrent_battles=0
            )
        else:
            raise ValueError(f"Unknown player type: {config['type']}")


async def cross_evaluate_with_random_teams(
    player_configs: List[dict],
    team_builder: RandomTeamBuilder,
    n_challenges: int = 3,
    battle_format: str = "gen3ubers",
    team_size: int = 4
) -> Dict[str, Dict[str, float]]:
    """
    Custom cross-evaluation that generates random teams for each matchup.

    This creates new players with random teams for each matchup, then runs
    all n_challenges battles with those teams. This is different from the
    default cross_evaluate which keeps the same teams throughout.

    Args:
        player_configs: List of player configuration dictionaries
        team_builder: RandomTeamBuilder instance
        n_challenges: Number of challenges per player pair
        battle_format: Battle format to use
        team_size: Number of Pokemon per team

    Returns:
        Dictionary with win rates for each player pair
    """
    factory = PlayerFactory(team_builder, battle_format, team_size)
    results = {config["username"]: {} for config in player_configs}

    # Calculate only unique matchups (like built-in cross_evaluate)
    total_matchups = len(player_configs) * (len(player_configs) - 1) // 2
    current_matchup = 0

    print(f"\n{'='*80}")
    print(f"Starting Round Robin Tournament")
    print(f"{'='*80}")
    print(f"Players: {len(player_configs)}")
    print(f"Battles per matchup: {n_challenges}")
    print(f"Total unique matchups: {total_matchups}")
    print(f"Total battles: {total_matchups * n_challenges}")
    print(f"{'='*80}\n")

    # Cross-evaluate all pairs (only unique matchups)
    for i, config1 in enumerate(player_configs):
        for j, config2 in enumerate(player_configs):
            if i == j:
                # Self-play: mark as None
                results[config1["username"]][config2["username"]] = None
                continue

            if j <= i:
                # Skip reverse matchup (already played)
                continue

            current_matchup += 1

            print(f"\n[Matchup {current_matchup}/{total_matchups}] {config1['username']} vs {config2['username']}")
            print(f"{'-'*80}")
            print(f"  Generating random teams for this matchup...", end=" ")

            # Create players ONCE per matchup with unique usernames and random teams
            # Add matchup number to username to avoid conflicts with previous matchups
            config1_copy = config1.copy()
            config2_copy = config2.copy()
            config1_copy["username"] = f"{config1['username']}_{current_matchup}"
            config2_copy["username"] = f"{config2['username']}_{current_matchup}"

            player1 = factory.create_player(config1_copy)
            player2 = factory.create_player(config2_copy)

            print("Done!")

            # Battle n_challenges times with the same teams
            await player1.battle_against(player2, n_battles=n_challenges)

            # Calculate win rates for both directions
            win_rate_p1 = player1.win_rate
            win_rate_p2 = player2.win_rate

            results[config1["username"]][config2["username"]] = win_rate_p1
            results[config2["username"]][config1["username"]] = win_rate_p2

            print(f"  Results: {config1['username']} won {player1.n_won_battles}/{n_challenges} ({win_rate_p1:.1%})")
            print(f"           {config2['username']} won {player2.n_won_battles}/{n_challenges} ({win_rate_p2:.1%})")

    return results


def print_results(cross_evaluation: Dict[str, Dict[str, float]], player_configs: List[dict], n_challenges: int):
    """
    Print tournament results in a formatted table with overall statistics.

    Args:
        cross_evaluation: Dictionary with win rates for each player pair
        player_configs: List of player configuration dictionaries
        n_challenges: Number of challenges per player pair
    """
    print(f"\n\n{'='*80}")
    print("FINAL RESULTS - WIN RATE MATRIX")
    print(f"{'='*80}\n")

    usernames = [config["username"] for config in player_configs]
    table = [["-"] + usernames]

    for username in usernames:
        row = [username]
        for opponent in usernames:
            win_rate = cross_evaluation[username][opponent]
            row.append("-" if win_rate is None else f"{win_rate:.2f}")
        table.append(row)

    print(tabulate(table, headers="firstrow", tablefmt="grid"))
    print(f"\n{'='*80}")

    # Calculate overall statistics
    print("\nOVERALL STATISTICS")
    print(f"{'='*80}")

    for username in usernames:
        wins = 0
        total = 0
        for opponent in usernames:
            if username != opponent:
                win_rate = cross_evaluation[username][opponent]
                wins += win_rate * n_challenges
                total += n_challenges

        overall_win_rate = wins / total if total > 0 else 0
        print(f"{username:20} | Win Rate: {overall_win_rate:.1%} ({int(wins)}/{total} battles won)")

    print(f"{'='*80}\n")
