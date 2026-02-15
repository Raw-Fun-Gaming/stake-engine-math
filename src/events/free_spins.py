"""Free spins event functions.

Includes trigger, update, and end free spins events.
"""

from __future__ import annotations

from typing import Any

from src.events.constants import EventConstants
from src.formatter import OutputFormatter


def trigger_free_spins_event(
    game_state: Any,
    include_padding_index: bool = True,
    base_game_trigger: bool | None = None,
    free_game_trigger: bool | None = None,
) -> None:
    """Trigger or retrigger free spins feature.

    Creates either a TRIGGER_FREE_SPINS or RETRIGGER_FREE_SPINS event
    depending on whether it's called from base game or during free spins.

    Args:
        game_state: Current game state with scatter positions
        include_padding_index: Whether to offset row positions by 1 for padding
        base_game_trigger: True if triggering from base game
        free_game_trigger: True if retriggering during free spins

    Raises:
        AssertionError: If both or neither trigger flags are set, or if total_free_spins <= 0
    """
    assert (
        base_game_trigger != free_game_trigger
    ), "must set either base_game_trigger or free_game_trigger to = True"

    # Create OutputFormatter from config settings
    formatter = OutputFormatter(
        output_mode=game_state.config.output_mode,
        compress_positions=game_state.config.compress_positions,
    )

    event: dict[str, Any] = {}
    scatter_positions: list[dict[str, int]] = []
    for reel, _ in enumerate(game_state.special_syms_on_board["scatter"]):
        scatter_positions.append(game_state.special_syms_on_board["scatter"][reel])
    if include_padding_index:
        for pos in scatter_positions:
            pos["row"] += 1

    # Format positions using the formatter
    formatted_positions = formatter.format_position_list(scatter_positions)

    if base_game_trigger:
        event = {
            "index": len(game_state.book.events),
            "type": EventConstants.TRIGGER_FREE_SPINS.value,
            "total": game_state.total_free_spins,
            "positions": formatted_positions,
        }
    elif free_game_trigger:
        event = {
            "index": len(game_state.book.events),
            "type": EventConstants.RETRIGGER_FREE_SPINS.value,
            "total": game_state.total_free_spins,
            "positions": formatted_positions,
        }

    assert (
        game_state.total_free_spins > 0
    ), "total free game (game_state.total_free_spins) must be >0"
    game_state.book.add_event(event)


def update_free_spins_event(game_state: Any) -> None:
    """Update current free spin counter.

    Creates an UPDATE_FREE_SPINS event showing the current spin number
    and total free spins awarded.

    Args:
        game_state: Current game state with free spin counters
    """
    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.UPDATE_FREE_SPINS.value,
        "amount": int(game_state.free_spin_count),
        "total": int(game_state.total_free_spins),
    }
    game_state.book.add_event(event)


def end_free_spins_event(game_state: Any, win_level_key: str = "endFeature") -> None:
    """Signal end of free spins feature.

    Creates an END_FREE_SPINS event with total feature wins and win level.

    Args:
        game_state: Current game state with win manager
        win_level_key: Key for win level configuration (default: "endFeature")
    """
    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.END_FREE_SPINS.value,
        "amount": int(
            min(game_state.win_manager.free_game_wins, game_state.config.win_cap) * 100
        ),
        "winLevel": game_state.config.get_win_level(
            game_state.win_manager.free_game_wins, win_level_key
        ),
    }
    game_state.book.add_event(event)
