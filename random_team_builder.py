import random
import os
from typing import List


class RandomTeamBuilder:
    """Builds random Pokemon teams from a file of Pokemon builds."""

    def __init__(self, builds_file: str = "pokemon_builds.txt", filter_format: str = "doubles", include_formats: List[str] = None):
        """
        Initialize the team builder by loading Pokemon builds from file.

        Args:
            builds_file: Path to the file containing Pokemon builds in Showdown format.
                        Defaults to "pokemon_builds.txt" (fixed HP + no banned moves).
                        Use "pokemon_builds_fixed.txt" for builds with only HP fixes.
                        Use "pokemon_builds.txt" for original builds (may have validation errors).
            filter_format: Format to filter out (e.g., "doubles" to exclude doubles battles).
                          Set to None to include all formats.
            include_formats: List of formats to include (e.g., ["OU", "Uber"] for balanced teams).
                            If specified, only Pokemon with these format tags will be included.
                            Set to None to include all formats (subject to filter_format).
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
        self.include_formats = include_formats
        self.pokemon_builds = self._parse_builds(builds_file)
        print(f"Loaded {len(self.pokemon_builds)} Pokemon builds from {builds_file}")
        if filter_format:
            print(f"  Filter applied: excluding '{filter_format}' format")
        if include_formats:
            print(f"  Include filter: only including {include_formats} formats")

    def _normalize_species(self, species: str) -> str:
        """
        Normalize species names to treat alternate formes as the same species.
        Example: 'Deoxys-Attack' -> 'Deoxys'
        """
        base_species = species.split('-')[0]
        return base_species

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

            # Filter out builds based on format (negative filter)
            if self.filter_format and self.filter_format.lower() in build.lower():
                continue

            # Include only builds with specified formats (positive filter)
            if self.include_formats:
                has_included_format = any(
                    f" - {fmt.lower()}" in build.lower() for fmt in self.include_formats
                )
                if not has_included_format:
                    continue

            lines = build.strip().split('\n')

            # Remove comment lines (lines starting with #)
            filtered_lines = [line for line in lines if not line.strip().startswith('#')]

            cleaned_build = '\n'.join(filtered_lines).strip()
            if cleaned_build:
                cleaned_builds.append(cleaned_build)

        return cleaned_builds

    def _extract_species(self, build: str) -> str:
        """
        Extract the Pokemon species name from a build.

        Args:
            build: Pokemon build string in Showdown format

        Returns:
            Pokemon species name
        """
        # Get the first line which contains the Pokemon name
        first_line = build.strip().split('\n')[0]

        # Check if there's a parenthesis (named Pokemon format: "Nickname (Species)")
        if '(' in first_line and ')' in first_line:
            # Extract species from parentheses
            species = first_line.split('(')[1].split(')')[0].strip()
        else:
            # Otherwise, species is before the @ symbol or the whole first line
            species = first_line.split('@')[0].strip()

        return species

    def generate_random_team(self, team_size: int = 4) -> str:
        """
        Generate a random team of specified size with unique species.

        Args:
            team_size: Number of Pokemon in the team (default: 4)

        Returns:
            Team string in Showdown format

        Raises:
            ValueError: If requested team size exceeds available unique species
        """
        # Track unique species to avoid duplicates
        selected_species = set()
        selected_pokemon = []

        # Create a shuffled copy of builds to sample from
        available_builds = self.pokemon_builds.copy()
        random.shuffle(available_builds)

        # Select Pokemon with unique species
        for build in available_builds:
            species = self._normalize_species(self._extract_species(build))

            if species not in selected_species:
                selected_species.add(species)
                selected_pokemon.append(build)

                if len(selected_pokemon) == team_size:
                    break

        # Check if we have enough unique species
        if len(selected_pokemon) < team_size:
            raise ValueError(
                f"Requested team size {team_size} exceeds available unique species {len(selected_pokemon)}"
            )

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
