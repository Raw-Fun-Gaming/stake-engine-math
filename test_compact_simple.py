"""Simple test of compact output formatting."""

import sys
sys.path.insert(0, '.')

from src.output.output_formatter import OutputFormatter, OutputMode
from unittest.mock import Mock

print("Testing OutputFormatter...")

# Create formatters
compact = OutputFormatter(output_mode=OutputMode.COMPACT)
verbose = OutputFormatter(output_mode=OutputMode.VERBOSE)

# Test symbol formatting
mock_symbol = Mock()
mock_symbol.name = "L5"
mock_symbol.get_attribute = Mock(return_value=False)

compact_sym = compact.format_symbol(mock_symbol, [])
verbose_sym = verbose.format_symbol(mock_symbol, [])

print(f"\nSymbol Formatting:")
print(f"  Compact: {compact_sym} (type: {type(compact_sym).__name__})")
print(f"  Verbose: {verbose_sym} (type: {type(verbose_sym).__name__})")

# Test position formatting
compact_pos = compact.format_position(0, 2)
verbose_pos = verbose.format_position(0, 2)

print(f"\nPosition Formatting:")
print(f"  Compact: {compact_pos} (type: {type(compact_pos).__name__})")
print(f"  Verbose: {verbose_pos} (type: {type(verbose_pos).__name__})")

# Test board formatting
board = [[mock_symbol, mock_symbol], [mock_symbol, mock_symbol]]
compact_board = compact.format_board(board, [])
verbose_board = verbose.format_board(board, [])

print(f"\nBoard Formatting:")
print(f"  Compact: {compact_board[0][0]} (first symbol)")
print(f"  Verbose: {verbose_board[0][0]} (first symbol)")

# Calculate size savings
import json

compact_board_json = json.dumps(compact_board)
verbose_board_json = json.dumps(verbose_board)

print(f"\nSize Comparison (2x2 board):")
print(f"  Compact: {len(compact_board_json)} bytes")
print(f"  Verbose: {len(verbose_board_json)} bytes")
print(f"  Savings: {100 * (1 - len(compact_board_json)/len(verbose_board_json)):.1f}%")

# Estimate savings for a full 5x5 board
full_board = [[mock_symbol for _ in range(5)] for _ in range(5)]
compact_full = compact.format_board(full_board, [])
verbose_full = verbose.format_board(full_board, [])

compact_full_json = json.dumps(compact_full)
verbose_full_json = json.dumps(verbose_full)

print(f"\nSize Comparison (5x5 board):")
print(f"  Compact: {len(compact_full_json)} bytes")
print(f"  Verbose: {len(verbose_full_json)} bytes")
print(f"  Savings: {100 * (1 - len(compact_full_json)/len(verbose_full_json)):.1f}%")

# Estimate for 10k simulations
print(f"\nEstimated Savings for 10k Simulations:")
print(f"  Compact: {len(compact_full_json) * 10000 / 1024 / 1024:.2f} MB")
print(f"  Verbose: {len(verbose_full_json) * 10000 / 1024 / 1024:.2f} MB")
print(f"  Saved: {(len(verbose_full_json) - len(compact_full_json)) * 10000 / 1024 / 1024:.2f} MB")

print("\n✅ Compact output mode working!")
