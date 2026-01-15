"""Test full game simulation with compact output mode."""

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

run_sims_spec = importlib.util.spec_from_file_location(
    "run_sims",
    "src/state/run_sims.py"
)
run_sims_module = importlib.util.module_from_spec(run_sims_spec)
run_sims_spec.loader.exec_module(run_sims_module)
create_books = run_sims_module.create_books

from src.output.output_formatter import OutputMode

print("=" * 70)
print("TESTING FULL GAME SIMULATION WITH COMPACT MODE")
print("=" * 70)

# Test 1: Verbose mode (default)
print("\n[1] Running 100 spins in VERBOSE mode...")
config_verbose = GameConfig()
config_verbose.output_mode = OutputMode.VERBOSE

library_verbose = create_books(
    config=config_verbose,
    betmode="base",
    num_sims=100,
    sim_start=0,
    thread_id=0,
    repeat_index=0
)

# Check first book
if library_verbose:
    first_book_verbose = library_verbose[0]
    print(f"   Books generated: {len(library_verbose)}")
    print(f"   First book ID: {first_book_verbose['id']}")
    print(f"   Format version: {first_book_verbose.get('formatVersion', 'NOT SET')}")

    # Check first event's board
    if first_book_verbose['events']:
        first_event = first_book_verbose['events'][0]
        if 'board' in first_event and first_event['board']:
            first_symbol = first_event['board'][0][0]
            print(f"   First symbol type: {type(first_symbol).__name__}")
            print(f"   First symbol: {first_symbol}")

    # Calculate size
    verbose_json = json.dumps(library_verbose)
    verbose_size = len(verbose_json)
    print(f"   Total JSON size: {verbose_size:,} bytes ({verbose_size/1024:.2f} KB)")

# Test 2: Compact mode
print("\n[2] Running 100 spins in COMPACT mode...")
config_compact = GameConfig()
config_compact.output_mode = OutputMode.COMPACT

library_compact = create_books(
    config=config_compact,
    betmode="base",
    num_sims=100,
    sim_start=0,
    thread_id=0,
    repeat_index=0
)

# Check first book
if library_compact:
    first_book_compact = library_compact[0]
    print(f"   Books generated: {len(library_compact)}")
    print(f"   First book ID: {first_book_compact['id']}")
    print(f"   Format version: {first_book_compact.get('formatVersion', 'NOT SET')}")

    # Check first event's board
    if first_book_compact['events']:
        first_event = first_book_compact['events'][0]
        if 'board' in first_event and first_event['board']:
            first_symbol = first_event['board'][0][0]
            print(f"   First symbol type: {type(first_symbol).__name__}")
            print(f"   First symbol: {first_symbol}")

    # Calculate size
    compact_json = json.dumps(library_compact)
    compact_size = len(compact_json)
    print(f"   Total JSON size: {compact_size:,} bytes ({compact_size/1024:.2f} KB)")

# Compare
print("\n[3] COMPARISON")
print("=" * 70)
print(f"   Verbose size:  {verbose_size:,} bytes ({verbose_size/1024:.2f} KB)")
print(f"   Compact size:  {compact_size:,} bytes ({compact_size/1024:.2f} KB)")
print(f"   Difference:    {verbose_size - compact_size:,} bytes")
print(f"   Savings:       {100 * (1 - compact_size/verbose_size):.1f}%")
print("=" * 70)

# Estimate for 10k simulations
print(f"\n[4] ESTIMATED FOR 10,000 SIMULATIONS")
print(f"   Verbose:  {verbose_size * 100 / 1024 / 1024:.2f} MB")
print(f"   Compact:  {compact_size * 100 / 1024 / 1024:.2f} MB")
print(f"   Saved:    {(verbose_size - compact_size) * 100 / 1024 / 1024:.2f} MB")

print("\n✅ Full simulation test complete!")
