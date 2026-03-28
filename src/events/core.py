"""Core event functions used by all game types.

Includes reveal, win, set_win, set_total_win, set_final_win, and win_cap events.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from src.events.constants import EventConstants
from src.events.helpers import to_camel_case
from src.formatter import OutputFormatter


def reveal_event(game_state: Any) -> None:
    """Display the initial board drawn from reel strips.

    Creates a REVEAL event showing the current board state with all symbols.
    Optionally includes padding symbols (top/bottom) if configured.

    Args:
        game_state: Current game state with board and configuration
    """
    # Create OutputFormatter from config settings
    formatter = OutputFormatter(
        output_mode=game_state.config.output_mode,
        include_losing_boards=game_state.config.include_losing_boards,
        compress_positions=game_state.config.compress_positions,
        simple_symbols=game_state.config.simple_symbols,
        skip_implicit_events=game_state.config.skip_implicit_events,
    )

    # Check if we should skip this reveal (losing board with
    # include_losing_boards=False)
    # Note: We need to check final win, but at reveal time we don't know it yet
    # So we'll always include reveals and let books writing filter them out if needed

    special_attributes = list(game_state.config.special_symbols.keys())

    # Use formatter to format the board
    board_client: list[list[Any]] = []
    for reel, _ in enumerate(game_state.board):
        board_client.append([])
        for row in range(len(game_state.board[reel])):
            board_client[reel].append(
                formatter.format_symbol(game_state.board[reel][row], special_attributes)
            )

    if game_state.config.include_padding:
        for reel, _ in enumerate(board_client):
            board_client[reel] = [
                formatter.format_symbol(
                    game_state.top_symbols[reel], special_attributes
                )
            ] + board_client[reel]
            board_client[reel].append(
                formatter.format_symbol(
                    game_state.bottom_symbols[reel], special_attributes
                )
            )

    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.REVEAL.value,
        "board": board_client,
        "gameType": to_camel_case(game_state.game_type),
        "anticipation": game_state.anticipation,
    }

    # Only include paddingPositions if enabled in config
    if game_state.config.output_padding_positions:
        event["paddingPositions"] = game_state.reel_positions

    game_state.book.add_event(event)


def win_event(game_state: Any, include_padding_index: bool = True) -> None:
    """Create a WIN event with detailed win information.

    Transforms internal win data into client-ready format, handling position
    adjustments for padding, converting field names, and extracting metadata.

    Args:
        game_state: Current game state with win_data
        include_padding_index: If True, offset row positions by 1 for padding symbols
    """
    # Create OutputFormatter from config settings
    formatter = OutputFormatter(
        output_mode=game_state.config.output_mode,
        compress_positions=game_state.config.compress_positions,
    )

    win_data_copy: dict[str, Any] = {}
    win_data_copy["details"] = deepcopy(game_state.win_data["wins"])
    for i, win_detail in enumerate(win_data_copy["details"]):
        if include_padding_index:
            new_positions: list[dict[str, int]] = []
            for pos in win_detail["positions"]:
                new_positions.append({"reel": pos["reel"], "row": pos["row"] + 1})
        else:
            new_positions = win_detail["positions"]

        # Format positions using OutputFormatter
        formatted_positions = formatter.format_position_list(new_positions)

        detail = win_data_copy["details"][i]
        detail["amount"] = int(
            round(
                min(detail["win"], game_state.config.win_cap) * 100,
                0,
            )
        )
        detail["positions"] = formatted_positions

        # Convert clusterSize (cluster-pay) or kind (line-pay/ways-pay) to count
        if "clusterSize" in detail:
            detail["count"] = detail["clusterSize"]
            del detail["clusterSize"]
        elif "kind" in detail:
            detail["count"] = detail["kind"]
            del detail["kind"]

        # Remove old field names
        del detail["win"]

        if "meta" in detail:
            detail["baseAmount"] = int(
                int(
                    min(
                        detail["meta"]["winWithoutMult"] * 100,
                        game_state.config.win_cap * 100,
                    ),
                )
            )
            detail["multiplier"] = detail["meta"]["globalMultiplier"]

            # Include cluster multiplier if present (for cluster-pay games with grid multipliers)
            if "clusterMultiplier" in detail["meta"]:
                detail["clusterMultiplier"] = detail["meta"]["clusterMultiplier"]

            # Include cluster increment if present (for cluster-pay games with grid incrementers)
            if "positionIncrements" in detail["meta"]:
                detail["positionIncrements"] = detail["meta"]["positionIncrements"]
                detail["effectiveCount"] = detail["meta"]["effectiveCount"]

            # Handle overlay if present
            if "overlay" in detail["meta"] and include_padding_index:
                overlay_data = detail["meta"]["overlay"]
                overlay_data["row"] += 1
                detail["overlay"] = overlay_data

            # Remove old meta structure
            del detail["meta"]

        # Strip any keys the game config marks as excluded
        for key in game_state.config.exclude_win_detail_keys:
            detail.pop(key, None)

    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.WIN.value,
        "reason": "cluster",
        "amount": int(
            round(
                min(game_state.win_data["totalWin"], game_state.config.win_cap) * 100, 0
            )
        ),
        "totalAmount": int(
            round(
                min(game_state.win_manager.running_bet_win, game_state.config.win_cap)
                * 100,
                0,
            )
        ),
        "details": win_data_copy["details"],
    }
    game_state.book.add_event(event)


def show_win_event(game_state: Any, win_level_key: str = "standard") -> None:
    """Trigger the win celebration display for a single outcome.

    Creates a SHOW_WIN event showing the current spin win amount and win level.
    Only emitted if win cap hasn't been triggered yet.

    Args:
        game_state: Current game state with win manager
        win_level_key: Key for win level configuration (default: "standard")
    """
    if not game_state.wincap_triggered:
        event: dict[str, Any] = {
            "index": len(game_state.book.events),
            "type": EventConstants.SHOW_WIN.value,
            "amount": int(
                min(
                    round(game_state.win_manager.spin_win * 100, 0),
                    game_state.config.win_cap * 100,
                )
            ),
            "level": game_state.config.get_win_level(
                game_state.win_manager.spin_win, win_level_key
            ),
        }
        game_state.book.add_event(event)


def set_total_win_event(game_state: Any) -> None:
    """Update win amount for entire betting round.

    Creates a SET_TOTAL_WIN event showing cumulative wins across multiple
    outcomes (e.g., base game + all free spins).

    Args:
        game_state: Current game state with win manager
    """
    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.SET_TOTAL_WIN.value,
        "amount": int(
            round(
                min(game_state.win_manager.running_bet_win, game_state.config.win_cap)
                * 100,
                0,
            )
        ),
    }
    game_state.book.add_event(event)


def set_final_win_event(game_state: Any) -> None:
    """Assign final payout multiplier for simulation.

    Creates a SET_FINAL_WIN event with the capped total payout.

    Args:
        game_state: Current game state with final_win calculated
    """
    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.SET_FINAL_WIN.value,
        "amount": int(
            round(min(game_state.final_win, game_state.config.win_cap) * 100, 0)
        ),
    }
    game_state.book.add_event(event)


def win_cap_event(game_state: Any) -> None:
    """Emit a showWin event when the win cap is reached.

    Uses SHOW_WIN with the capped amount and max win level to signal
    the maximum payout limit has been hit.

    Args:
        game_state: Current game state with win manager
    """
    win_cap = game_state.config.win_cap
    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.SHOW_WIN.value,
        "amount": int(round(win_cap * 100, 0)),
        "level": game_state.config.get_win_level(win_cap, "standard"),
    }
    game_state.book.add_event(event)
