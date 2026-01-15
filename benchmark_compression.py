#!/usr/bin/env python3
"""Benchmark compression savings for output compression feature.

Runs simulations with both verbose and compact modes to measure actual
file size improvements.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Import dynamically due to numeric module name
import importlib.util

# Load game modules dynamically
game_config_spec = importlib.util.spec_from_file_location(
    "game_config", "games/0_0_lines/game_config.py"
)
game_config_module = importlib.util.module_from_spec(game_config_spec)
game_config_spec.loader.exec_module(game_config_module)
GameConfig = game_config_module.GameConfig

gamestate_spec = importlib.util.spec_from_file_location(
    "gamestate", "games/0_0_lines/gamestate.py"
)
gamestate_module = importlib.util.module_from_spec(gamestate_spec)
gamestate_spec.loader.exec_module(gamestate_module)
GameState = gamestate_module.GameState

from src.output.output_formatter import OutputMode
from src.state.run_sims import create_books


def run_benchmark(num_sims=1000):
    """Run benchmark comparing verbose vs compact output modes."""
    print("=" * 70)
    print("OUTPUT COMPRESSION BENCHMARK")
    print("=" * 70)
    print(f"\nRunning {num_sims} simulations per mode...")

    # Test 1: Verbose mode
    print("\n[1] Running simulations in VERBOSE mode...")
    config_verbose = GameConfig()
    config_verbose.output_mode = OutputMode.VERBOSE
    config_verbose.compress_symbols = False
    config_verbose.compress_positions = False

    gamestate_verbose = GameState(config_verbose)

    # Run simulations
    create_books(
        gamestate=gamestate_verbose,
        config=config_verbose,
        num_sim_args={"base": num_sims},
        batch_size=num_sims,
        threads=1,
        compress=False,  # Don't compress so we can measure JSON size
        profiling=False,
    )

    # Measure file size (check both locations)
    verbose_file = Path(config_verbose.library_path) / "books" / "books_base.json"
    if not verbose_file.exists():
        verbose_file = Path(config_verbose.library_path) / "publish_files" / "books_base.jsonl"

    if verbose_file.exists():
        verbose_size = verbose_file.stat().st_size
        with open(verbose_file, "r") as f:
            verbose_lines = len(f.readlines())
        print(f"   ✅ Verbose mode complete")
        print(f"   File: {verbose_file.name}")
        print(f"   Size: {verbose_size:,} bytes ({verbose_size/1024:.2f} KB)")
        print(f"   Lines: {verbose_lines:,}")
    else:
        print(f"   ❌ Error: Verbose file not found at {verbose_file}")
        return

    # Test 2: Compact mode
    print("\n[2] Running simulations in COMPACT mode...")
    config_compact = GameConfig()
    config_compact.output_mode = OutputMode.COMPACT
    config_compact.compress_symbols = True
    config_compact.compress_positions = True

    # Reset singleton
    if hasattr(GameState, "_instance"):
        delattr(GameState, "_instance")

    gamestate_compact = GameState(config_compact)

    # Run simulations
    create_books(
        gamestate=gamestate_compact,
        config=config_compact,
        num_sim_args={"base": num_sims},
        batch_size=num_sims,
        threads=1,
        compress=False,  # Don't compress so we can measure JSON size
        profiling=False,
    )

    # Measure file size (check both locations)
    compact_file = Path(config_compact.library_path) / "books" / "books_base.json"
    if not compact_file.exists():
        compact_file = Path(config_compact.library_path) / "publish_files" / "books_base.jsonl"

    if compact_file.exists():
        compact_size = compact_file.stat().st_size
        with open(compact_file, "r") as f:
            compact_lines = len(f.readlines())
        print(f"   ✅ Compact mode complete")
        print(f"   File: {compact_file.name}")
        print(f"   Size: {compact_size:,} bytes ({compact_size/1024:.2f} KB)")
        print(f"   Lines: {compact_lines:,}")
    else:
        print(f"   ❌ Error: Compact file not found at {compact_file}")
        return

    # Comparison
    print("\n[3] COMPARISON")
    print("=" * 70)
    print(f"   Simulations:  {num_sims:,}")
    print(f"   Verbose size: {verbose_size:,} bytes ({verbose_size/1024:.2f} KB)")
    print(f"   Compact size: {compact_size:,} bytes ({compact_size/1024:.2f} KB)")
    print(f"   Difference:   {verbose_size - compact_size:,} bytes")
    savings_pct = 100 * (1 - compact_size / verbose_size)
    print(f"   Savings:      {savings_pct:.1f}%")
    print("=" * 70)

    # Extrapolation
    print(f"\n[4] ESTIMATED FOR 10,000 SIMULATIONS")
    factor = 10000 / num_sims
    est_verbose = verbose_size * factor
    est_compact = compact_size * factor
    print(f"   Verbose:  {est_verbose / 1024 / 1024:.2f} MB")
    print(f"   Compact:  {est_compact / 1024 / 1024:.2f} MB")
    print(f"   Saved:    {(est_verbose - est_compact) / 1024 / 1024:.2f} MB")

    # Sample books
    print("\n[5] SAMPLE BOOKS")
    with open(verbose_file, "r") as f:
        content = f.read()
        if verbose_file.suffix == ".json":
            books = json.loads(content)
            verbose_book = books[0] if isinstance(books, list) else books
        else:
            verbose_book = json.loads(content.split("\n")[0])

    with open(compact_file, "r") as f:
        content = f.read()
        if compact_file.suffix == ".json":
            books = json.loads(content)
            compact_book = books[0] if isinstance(books, list) else books
        else:
            compact_book = json.loads(content.split("\n")[0])

    print(f"   Verbose format version: {verbose_book.get('formatVersion', 'NOT SET')}")
    print(f"   Compact format version: {compact_book.get('formatVersion', 'NOT SET')}")

    # Check first event board formatting
    if verbose_book["events"] and "board" in verbose_book["events"][0]:
        verbose_first_symbol = verbose_book["events"][0]["board"][0][0]
        compact_first_symbol = compact_book["events"][0]["board"][0][0]
        print(f"   Verbose symbol format: {verbose_first_symbol} (type: {type(verbose_first_symbol).__name__})")
        print(f"   Compact symbol format: {compact_first_symbol} (type: {type(compact_first_symbol).__name__})")

    print("\n✅ Benchmark complete!")


if __name__ == "__main__":
    num_sims = 1000
    if len(sys.argv) > 1:
        num_sims = int(sys.argv[1])

    run_benchmark(num_sims)
