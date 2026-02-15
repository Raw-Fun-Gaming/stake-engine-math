"""Tumble/cascade event functions.

Includes tumble, set_tumble_win, update_tumble_win, and reveal_board_multipliers events.
Only needed by games with tumble/cascade mechanics.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from src.events.constants import EventConstants
from src.formatter import OutputFormatter


def tumble_event(game_state: Any, include_padding_index: bool = True) -> None:
    """Create tumble/cascade event showing removed and new symbols.

    Generates a TUMBLE event listing which symbols were removed
    and which new symbols drop in to replace them.

    Args:
        game_state: Current game state with win_data and new_symbols_from_tumble
        include_padding_index: If True, offset row positions by 1 for padding symbols
    """
    # Create OutputFormatter from config settings
    formatter = OutputFormatter(
        output_mode=game_state.config.output_mode,
        compress_positions=game_state.config.compress_positions,
        simple_symbols=game_state.config.simple_symbols,
    )

    special_attributes = list(game_state.config.special_symbols.keys())

    # Build per-reel removed row indexes
    removed_indexes: list[list[int]] = [[] for _ in range(game_state.config.num_reels)]
    for win in game_state.win_data["wins"]:
        for pos in win["positions"]:
            reel = pos["reel"]
            row = pos["row"] + 1 if include_padding_index else pos["row"]
            if row not in removed_indexes[reel]:
                removed_indexes[reel].append(row)

    # Sort row indexes within each reel
    for reel_indexes in removed_indexes:
        reel_indexes.sort()

    new_symbols: list[list[Any]] = [[] for _ in range(game_state.config.num_reels)]
    for r, _ in enumerate(game_state.new_symbols_from_tumble):
        if len(game_state.new_symbols_from_tumble[r]) > 0:
            new_symbols[r] = [
                formatter.format_symbol(s, special_attributes)
                for s in game_state.new_symbols_from_tumble[r]
            ]

    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.TUMBLE.value,
        "newSymbols": new_symbols,
        "removedIndexes": removed_indexes,
    }
    game_state.book.add_event(event)


def set_tumble_win_event(game_state: Any) -> None:
    """Update banner showing wins from successive tumbles.

    Creates a SET_TUMBLE_WIN event displaying accumulated tumble wins.

    Args:
        game_state: Current game state with tumble_win tracking
    """
    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.SET_TUMBLE_WIN.value,
        "amount": int(
            round(min(game_state.tumble_win, game_state.config.win_cap) * 100)
        ),
    }
    game_state.book.add_event(event)


def update_tumble_win_event(game_state: Any) -> None:
    """Update banner to record successive tumble wins.

    Creates an UPDATE_TUMBLE_WIN event showing accumulated wins from cascades.

    Args:
        game_state: Current game state with win manager
    """
    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.UPDATE_TUMBLE_WIN.value,
        "amount": int(
            round(
                min(game_state.win_manager.spin_win, game_state.config.win_cap) * 100, 0
            )
        ),
    }
    game_state.book.add_event(event)


def reveal_board_multipliers_event(game_state: Any) -> None:
    """Reveal the current state of board position multipliers after a win.

    Shows the multiplier value at each board position so the frontend
    can render the multiplier grid overlay.

    Args:
        game_state: Current game state with position_multipliers grid
    """
    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.REVEAL_BOARD_MULTIPLIERS.value,
        "boardMultipliers": deepcopy(game_state.position_multipliers),
    }
    game_state.book.add_event(event)
