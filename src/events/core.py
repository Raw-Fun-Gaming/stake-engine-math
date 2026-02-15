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
    for idx, w in enumerate(win_data_copy["details"]):
        if include_padding_index:
            new_positions: list[dict[str, int]] = []
            for p in w["positions"]:
                new_positions.append({"reel": p["reel"], "row": p["row"] + 1})
        else:
            new_positions = w["positions"]

        # Format positions using OutputFormatter
        formatted_positions = formatter.format_position_list(new_positions)

        win_data_copy["details"][idx]["amount"] = int(
            round(
                min(win_data_copy["details"][idx]["win"], game_state.config.win_cap)
                * 100,
                0,
            )
        )
        win_data_copy["details"][idx]["positions"] = formatted_positions

        # Convert clusterSize (cluster-pay) or kind (line-pay/ways-pay) to count
        if "clusterSize" in win_data_copy["details"][idx]:
            win_data_copy["details"][idx]["count"] = win_data_copy["details"][idx][
                "clusterSize"
            ]
            del win_data_copy["details"][idx]["clusterSize"]
        elif "kind" in win_data_copy["details"][idx]:
            win_data_copy["details"][idx]["count"] = win_data_copy["details"][idx][
                "kind"
            ]
            del win_data_copy["details"][idx]["kind"]

        # Remove old field names
        del win_data_copy["details"][idx]["win"]

        if "meta" in win_data_copy["details"][idx]:
            win_data_copy["details"][idx]["baseAmount"] = int(
                int(
                    min(
                        win_data_copy["details"][idx]["meta"]["winWithoutMult"] * 100,
                        game_state.config.win_cap * 100,
                    ),
                )
            )
            win_data_copy["details"][idx]["multiplier"] = win_data_copy["details"][idx][
                "meta"
            ]["globalMultiplier"]

            # Include cluster multiplier if present (for cluster-pay games with grid multipliers)
            if "clusterMultiplier" in win_data_copy["details"][idx]["meta"]:
                win_data_copy["details"][idx]["clusterMultiplier"] = win_data_copy[
                    "details"
                ][idx]["meta"]["clusterMultiplier"]

            # Handle overlay if present
            if (
                "overlay" in win_data_copy["details"][idx]["meta"]
                and include_padding_index
            ):
                overlay_data = win_data_copy["details"][idx]["meta"]["overlay"]
                overlay_data["row"] += 1
                win_data_copy["details"][idx]["overlay"] = overlay_data

            # Remove old meta structure
            del win_data_copy["details"][idx]["meta"]

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


def set_win_event(game_state: Any, win_level_key: str = "standard") -> None:
    """Update cumulative win ticker for a single outcome.

    Creates a SET_WIN event showing the current spin win amount and win level.
    Only emitted if win cap hasn't been triggered yet.

    Args:
        game_state: Current game state with win manager
        win_level_key: Key for win level configuration (default: "standard")
    """
    if not game_state.wincap_triggered:
        event: dict[str, Any] = {
            "index": len(game_state.book.events),
            "type": EventConstants.SET_WIN.value,
            "amount": int(
                min(
                    round(game_state.win_manager.spin_win * 100, 0),
                    game_state.config.win_cap * 100,
                )
            ),
            "winLevel": game_state.config.get_win_level(
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
    """Emit event indicating win cap has been reached.

    Creates a WIN_CAP event when the maximum payout limit is hit,
    signaling the end of spin actions.

    Args:
        game_state: Current game state with win manager
    """
    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.WIN_CAP.value,
        "amount": int(
            round(
                min(game_state.win_manager.running_bet_win, game_state.config.win_cap)
                * 100,
                0,
            )
        ),
    }
    game_state.book.add_event(event)
