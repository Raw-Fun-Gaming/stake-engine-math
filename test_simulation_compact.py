"""Test game simulation with compact vs verbose output."""

import sys
import os
import json
import importlib.util

sys.path.insert(0, os.path.dirname(__file__))

# Import modules dynamically
game_config_spec = importlib.util.spec_from_file_location(
    "game_config",
    "games/0_0_lines/game_config.py"
)
game_config_module = importlib.util.module_from_spec(game_config_spec)
game_config_spec.loader.exec_module(game_config_module)
GameConfig = game_config_module.GameConfig

gamestate_spec = importlib.util.spec_from_file_location(
    "gamestate",
    "games/0_0_lines/gamestate.py"
)
gamestate_module = importlib.util.module_from_spec(gamestate_spec)
gamestate_spec.loader.exec_module(gamestate_module)
GameState = gamestate_module.GameState

from src.output.output_formatter import OutputMode

def run_simulations(config, num_sims=100):
    """Run simulations and return library of books."""
    # Reset singleton instance
    if hasattr(GameState, '_instance'):
        delattr(GameState, '_instance')

    game = GameState(config)
    game.betmode = "base"
    library = []

    for i in range(num_sims):
        game.sim = i
        game.criteria = "base"
        game.reset_seed(i)
        game.reset_book()
        game.run_spin(i)

        # Add book to library
        library.append(game.book.to_json())

    return library

print("=" * 70)
print("TESTING GAME SIMULATION: COMPACT VS VERBOSE")
print("=" * 70)

# Test 1: Verbose mode
print("\n[1] Running 100 spins in VERBOSE mode...")
config_verbose = GameConfig()
config_verbose.output_mode = OutputMode.VERBOSE

library_verbose = run_simulations(config_verbose, 100)

print(f"   Books generated: {len(library_verbose)}")
if library_verbose:
    first_book = library_verbose[0]
    print(f"   First book ID: {first_book['id']}")
    print(f"   Format version: {first_book.get('formatVersion', 'NOT SET')}")

    # Check first event
    if first_book['events']:
        first_event = first_book['events'][0]
        if 'board' in first_event and first_event['board']:
            first_symbol = first_event['board'][0][0]
            print(f"   First symbol type: {type(first_symbol).__name__}")
            print(f"   First symbol value: {first_symbol}")

verbose_json = json.dumps(library_verbose)
verbose_size = len(verbose_json)
print(f"   Total JSON size: {verbose_size:,} bytes ({verbose_size/1024:.2f} KB)")

# Test 2: Compact mode
print("\n[2] Running 100 spins in COMPACT mode...")
config_compact = GameConfig()
config_compact.output_mode = OutputMode.COMPACT

library_compact = run_simulations(config_compact, 100)

print(f"   Books generated: {len(library_compact)}")
if library_compact:
    first_book = library_compact[0]
    print(f"   First book ID: {first_book['id']}")
    print(f"   Format version: {first_book.get('formatVersion', 'NOT SET')}")

    # Check first event
    if first_book['events']:
        first_event = first_book['events'][0]
        if 'board' in first_event and first_event['board']:
            first_symbol = first_event['board'][0][0]
            print(f"   First symbol type: {type(first_symbol).__name__}")
            print(f"   First symbol value: {first_symbol}")

compact_json = json.dumps(library_compact)
compact_size = len(compact_json)
print(f"   Total JSON size: {compact_size:,} bytes ({compact_size/1024:.2f} KB)")

# Comparison
print("\n[3] COMPARISON (100 simulations)")
print("=" * 70)
print(f"   Verbose size:  {verbose_size:,} bytes ({verbose_size/1024:.2f} KB)")
print(f"   Compact size:  {compact_size:,} bytes ({compact_size/1024:.2f} KB)")
print(f"   Difference:    {verbose_size - compact_size:,} bytes")
print(f"   Savings:       {100 * (1 - compact_size/verbose_size):.1f}%")
print("=" * 70)

# Estimate for 10k simulations
print(f"\n[4] ESTIMATED FOR 10,000 SIMULATIONS")
est_verbose = verbose_size * 100
est_compact = compact_size * 100
print(f"   Verbose:  {est_verbose / 1024 / 1024:.2f} MB")
print(f"   Compact:  {est_compact / 1024 / 1024:.2f} MB")
print(f"   Saved:    {(est_verbose - est_compact) / 1024 / 1024:.2f} MB")

print("\n✅ Simulation test complete!")

# Write sample books to files for inspection
with open('test_verbose_sample.json', 'w') as f:
    json.dump(library_verbose[0], f, indent=2)
    print("\n📝 Wrote sample verbose book to: test_verbose_sample.json")

with open('test_compact_sample.json', 'w') as f:
    json.dump(library_compact[0], f, indent=2)
    print("📝 Wrote sample compact book to: test_compact_sample.json")
