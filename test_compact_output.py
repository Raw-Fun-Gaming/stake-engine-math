"""Quick test of compact output mode."""

import sys
import os
import importlib.util

sys.path.insert(0, os.path.dirname(__file__))

# Import from 0_0_lines using importlib
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

# Create config with compact output
config = GameConfig()
config.output_mode = OutputMode.COMPACT
config.compress_symbols = True
config.compress_positions = True

print("Testing compact output mode...")
print(f"Output mode: {config.output_mode}")
print(f"Compress symbols: {config.compress_symbols}")
print(f"Compress positions: {config.compress_positions}")

# Create game state (GameState is a singleton)
game = GameState(config)

# Run a single simulation
game.reset_seed(0)
game.reset_book()
game.run_spin(0)

# Check the events
print(f"\nGenerated {len(game.book.events)} events")

# Check reveal event (first event should be reveal)
if len(game.book.events) > 0:
    reveal_event = game.book.events[0]
    print(f"\nFirst event type: {reveal_event['type']}")

    if 'board' in reveal_event:
        board = reveal_event['board']
        print(f"Board has {len(board)} reels")
        if len(board) > 0 and len(board[0]) > 0:
            first_symbol = board[0][0]
            print(f"First symbol: {first_symbol}")
            print(f"First symbol type: {type(first_symbol)}")

            # In compact mode, simple symbols should be strings
            if isinstance(first_symbol, str):
                print("✅ Compact mode working! Symbols are strings.")
            elif isinstance(first_symbol, dict):
                if 'name' in first_symbol:
                    print(f"⚠️  Verbose mode: Symbol is dict with 'name': {first_symbol['name']}")
                else:
                    print(f"⚠️  Unexpected symbol format: {first_symbol}")

# Check for position events
for event in game.book.events:
    if 'positions' in event:
        positions = event['positions']
        if len(positions) > 0:
            first_pos = positions[0]
            print(f"\nFound positions in event type: {event['type']}")
            print(f"First position: {first_pos}")
            print(f"First position type: {type(first_pos)}")

            if isinstance(first_pos, list):
                print("✅ Compact mode working! Positions are arrays.")
            elif isinstance(first_pos, dict):
                print(f"⚠️  Verbose mode: Position is dict")
            break

print("\nTest complete!")
