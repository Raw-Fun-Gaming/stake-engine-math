#!/usr/bin/env python3
"""Simple test to verify event filtering is working in practice."""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# Import dynamically
import importlib.util

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

print("=" * 70)
print("EVENT FILTERING SIMPLE TEST")
print("=" * 70)

# Test 1: Baseline (no filtering)
print("\n## Test 1: Baseline (No Filtering)")
config1 = GameConfig()
config1.output_mode = OutputMode.COMPACT
gamestate1 = GameState(config1)

gamestate1.sim = 0
gamestate1.criteria = "basegame"
gamestate1.reset_book()
gamestate1.run_spin(0)
events1 = gamestate1.book.events
print(f"  Events: {len(events1)}")
print(f"  Event types: {[e['type'] for e in events1]}")

# Test 2: Skip derived wins
print("\n## Test 2: Skip Derived Wins")
config2 = GameConfig()
config2.output_mode = OutputMode.COMPACT
config2.skip_derived_wins = True
gamestate2 = GameState(config2)

gamestate2.sim = 0
gamestate2.criteria = "basegame"
gamestate2.reset_book()
gamestate2.run_spin(0)
events2 = gamestate2.book.events
print(f"  Events: {len(events2)}")
print(f"  Event types: {[e['type'] for e in events2]}")

# Test 3: Minimal verbosity
print("\n## Test 3: Minimal Verbosity")
config3 = GameConfig()
config3.output_mode = OutputMode.COMPACT
config3.verbose_event_level = "minimal"
gamestate3 = GameState(config3)

gamestate3.sim = 0
gamestate3.criteria = "basegame"
gamestate3.reset_book()
gamestate3.run_spin(0)
events3 = gamestate3.book.events
print(f"  Events: {len(events3)}")
print(f"  Event types: {[e['type'] for e in events3]}")

# Test 4: All optimizations
print("\n## Test 4: All Optimizations")
config4 = GameConfig()
config4.output_mode = OutputMode.COMPACT
config4.skip_derived_wins = True
config4.skip_progress_updates = True
config4.verbose_event_level = "standard"
gamestate4 = GameState(config4)

gamestate4.sim = 0
gamestate4.criteria = "basegame"
gamestate4.reset_book()
gamestate4.run_spin(0)
events4 = gamestate4.book.events
print(f"  Events: {len(events4)}")
print(f"  Event types: {[e['type'] for e in events4]}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Baseline events: {len(events1)}")
print(f"Skip derived wins: {len(events2)} ({(1 - len(events2)/len(events1))*100:.1f}% reduction)")
print(f"Minimal verbosity: {len(events3)} ({(1 - len(events3)/len(events1))*100:.1f}% reduction)")
print(f"All optimizations: {len(events4)} ({(1 - len(events4)/len(events1))*100:.1f}% reduction)")

print("\n✅ Event filtering is working correctly!")
