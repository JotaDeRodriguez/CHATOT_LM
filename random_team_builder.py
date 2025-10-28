import random
import os
from typing import List


class RandomTeamBuilder:
    """Builds random Pokemon teams from a file of Pokemon builds."""

    def __init__(self, builds_file: str = "pokemon_builds.txt", filter_format: str = "doubles"):
        """
        Initialize the team builder by loading Pokemon builds from file.

        Args:
            builds_file: Path to the file containing Pokemon builds in Showdown format.
                        Defaults to "pokemon_builds.txt" (fixed HP + no banned moves).
                        Use "pokemon_builds_fixed.txt" for builds with only HP fixes.
                        Use "pokemon_builds.txt" for original builds (may have validation errors).
            filter_format: Format to filter out (e.g., "doubles" to exclude doubles battles).
                          Set to None to include all formats.
        """
        # Check if the file exists, fallback chain
        if not os.path.exists(builds_file) and builds_file == "pokemon_builds.txt":
            print(f"Warning: {builds_file} not found")
            print("Run: 1) fix_hidden_power.py then 2) remove_banned_moves.py")
            if os.path.exists("pokemon_builds_fixed.txt"):
                print("Falling back to pokemon_builds_fixed.txt")
                builds_file = "pokemon_builds_fixed.txt"
            else:
                print("Falling back to pokemon_builds.txt")
                builds_file = "pokemon_builds.txt"

        self.filter_format = filter_format
        self.pokemon_builds = self._parse_builds(builds_file)
        print(f"Loaded {len(self.pokemon_builds)} Pokemon builds from {builds_file}")
        if filter_format:
            print(f"  Filter applied: excluding '{filter_format}' format")

    def _parse_builds(self, file_path: str) -> List[str]:
        """
        Parse the builds file and return a list of individual Pokemon builds.

        Args:
            file_path: Path to the builds file

        Returns:
            List of Pokemon build strings in Showdown format
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by the separator line
        builds = content.split('============================================================')

        # Clean up builds
        cleaned_builds = []
        for build in builds:
            if not build.strip():
                continue

            # Filter out builds based on format
            if self.filter_format and self.filter_format.lower() in build.lower():
                continue

            lines = build.strip().split('\n')

            # Remove comment lines (lines starting with #)
            filtered_lines = [line for line in lines if not line.strip().startswith('#')]

            cleaned_build = '\n'.join(filtered_lines).strip()
            if cleaned_build:
                cleaned_builds.append(cleaned_build)

        return cleaned_builds

    def generate_random_team(self, team_size: int = 4) -> str:
        """
        Generate a random team of specified size.

        Args:
            team_size: Number of Pokemon in the team (default: 4)

        Returns:
            Team string in Showdown format

        Raises:
            ValueError: If requested team size exceeds available builds
        """
        if team_size > len(self.pokemon_builds):
            raise ValueError(
                f"Requested team size {team_size} exceeds available builds {len(self.pokemon_builds)}"
            )

        # Randomly select unique Pokemon builds
        selected_pokemon = random.sample(self.pokemon_builds, team_size)

        # Combine into a team string (Pokemon separated by blank lines)
        team = '\n\n'.join(selected_pokemon)

        return team

    def generate_teams(self, num_teams: int, team_size: int = 4) -> List[str]:
        """
        Generate multiple random teams.

        Args:
            num_teams: Number of teams to generate
            team_size: Number of Pokemon per team (default: 4)

        Returns:
            List of team strings in Showdown format
        """
        return [self.generate_random_team(team_size) for _ in range(num_teams)]
