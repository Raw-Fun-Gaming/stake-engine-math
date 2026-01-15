#!/usr/bin/env python3
"""Validate game configuration files.

This script validates game configurations for common errors before running
simulations. Use it to catch configuration issues early in development.

Usage:
    python scripts/validate_config.py <game_name>
    make validate GAME=<game_name>

Example:
    python scripts/validate_config.py tower_treasures
    make validate GAME=tower_treasures
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.exceptions import GameConfigError


def validate_game(game_name: str, verbose: bool = False) -> bool:
    """Validate a game's configuration.

    Args:
        game_name: Name of the game directory (e.g., "tower_treasures")
        verbose: If True, print detailed validation info

    Returns:
        True if validation passed, False otherwise
    """
    print(f"Validating game: {game_name}")
    print("-" * 50)

    # Check game directory exists
    game_path = project_root / "games" / game_name
    if not game_path.exists():
        print(f"ERROR: Game directory not found: {game_path}")
        print(f"Available games:")
        for game_dir in (project_root / "games").iterdir():
            if game_dir.is_dir() and not game_dir.name.startswith("_"):
                print(f"  - {game_dir.name}")
        return False

    # Check required files exist
    required_files = ["game_config.py", "gamestate.py", "run.py"]
    missing_files = []
    for file_name in required_files:
        if not (game_path / file_name).exists():
            missing_files.append(file_name)

    if missing_files:
        print(f"ERROR: Missing required files: {missing_files}")
        return False

    if verbose:
        print("Required files present")

    # Try to import the game config
    try:
        config_module = importlib.import_module(f"games.{game_name}.game_config")
        config_class = getattr(config_module, "GameConfig", None)
        if config_class is None:
            print("ERROR: game_config.py must define a GameConfig class")
            return False

        config = config_class()
        if verbose:
            print(f"Config imported: {config.game_id}")
    except Exception as e:
        print(f"ERROR: Failed to import game config: {e}")
        return False

    # Run validation
    try:
        errors = config.validate_config(raise_on_error=False)
        if errors:
            print(f"Configuration errors ({len(errors)}):")
            for error in errors:
                print(f"  - {error}")
            return False
        else:
            print("Configuration: VALID")
    except Exception as e:
        print(f"ERROR: Validation failed unexpectedly: {e}")
        return False

    # Check reels directory
    reels_path = game_path / "reels"
    if reels_path.exists():
        reel_files = list(reels_path.glob("*.csv"))
        if verbose:
            print(f"Reel strip files: {len(reel_files)}")
            for rf in reel_files[:5]:
                print(f"  - {rf.name}")
            if len(reel_files) > 5:
                print(f"  ... and {len(reel_files) - 5} more")
    else:
        print(f"WARNING: Reels directory not found: {reels_path}")

    # Summary
    print("-" * 50)
    print(f"Validation PASSED for {game_name}")
    return True


def main() -> int:
    """Main entry point for the validation script."""
    parser = argparse.ArgumentParser(
        description="Validate game configuration files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s tower_treasures           # Validate single game
    %(prog)s tower_treasures -v        # Verbose output
    %(prog)s --list                    # List all available games
        """,
    )
    parser.add_argument(
        "game_name",
        nargs="?",
        help="Name of the game to validate (e.g., tower_treasures)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed validation information",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available games",
    )

    args = parser.parse_args()

    if args.list:
        games_dir = project_root / "games"
        print("Available games:")
        for game_dir in sorted(games_dir.iterdir()):
            if game_dir.is_dir() and not game_dir.name.startswith("_"):
                # Check if it has required files
                has_config = (game_dir / "game_config.py").exists()
                has_gamestate = (game_dir / "gamestate.py").exists()
                status = "ready" if (has_config and has_gamestate) else "incomplete"
                print(f"  {game_dir.name:25} [{status}]")
        return 0

    if not args.game_name:
        parser.error("game_name is required unless using --list")

    success = validate_game(args.game_name, verbose=args.verbose)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
