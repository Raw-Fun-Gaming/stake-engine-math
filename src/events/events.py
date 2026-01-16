"""Event construction functions for slot game simulations.

This module provides functions to construct standardized event dictionaries
that represent game actions like reveals, wins, free spin triggers, and tumbles.
All events follow a consistent structure and use EventConstants for type safety.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from src.events.event_constants import EventConstants
from src.output.output_formatter import OutputFormatter


def json_ready_sym(symbol: Any, special_attributes: list[str]) -> dict[str, Any]:
    """Convert a symbol object to dictionary/JSON format.

    Args:
        symbol: Symbol object with name and optional special attributes
        special_attributes: List of attribute names to include if present

    Returns:
        Dictionary with symbol name and any special attributes
    """
    print_sym: dict[str, Any] = {"name": symbol.name}
    attrs = vars(symbol)
    for key, val in attrs.items():
        if key in special_attributes and symbol.get_attribute(key) is not False:
            print_sym[key] = val
    return print_sym


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
        compress_symbols=game_state.config.compress_symbols,
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
        "paddingPositions": game_state.reel_positions,
        "gameType": game_state.game_type,
        "anticipation": game_state.anticipation,
    }
    game_state.book.add_event(event)


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
        AssertionError: If both or neither trigger flags are set, or if tot_fs <= 0
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
            "total": game_state.tot_fs,
            "positions": formatted_positions,
        }
    elif free_game_trigger:
        event = {
            "index": len(game_state.book.events),
            "type": EventConstants.RETRIGGER_FREE_SPINS.value,
            "total": game_state.tot_fs,
            "positions": formatted_positions,
        }

    assert game_state.tot_fs > 0, "total free game (game_state.tot_fs) must be >0"
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
            ]["globalMult"]

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


def update_free_spins_event(game_state: Any) -> None:
    """Update current free spin counter.

    Creates an UPDATE_FREE_SPINS event showing the current spin number
    and total free spins awarded.

    Args:
        game_state: Current game state with fs and tot_fs counters
    """
    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.UPDATE_FREE_SPINS.value,
        "amount": int(game_state.fs),
        "total": int(game_state.tot_fs),
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


def update_global_mult_event(game_state: Any) -> None:
    """Increment global multiplier display.

    Creates an UPDATE_GLOBAL_MULTIPLIER event showing the current multiplier value.

    Args:
        game_state: Current game state with global_multiplier
    """
    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.UPDATE_GLOBAL_MULTIPLIER.value,
        "globalMult": int(game_state.global_multiplier),
    }

    game_state.book.add_event(event)


def tumble_board_event(game_state: Any) -> None:
    """Create tumble/cascade event showing exploded and new symbols.

    Generates a TUMBLE_BOARD event listing which symbols were removed
    and which new symbols drop in to replace them.

    Args:
        game_state: Current game state with win_data and new_symbols_from_tumble
    """
    # Create OutputFormatter from config settings
    formatter = OutputFormatter(
        output_mode=game_state.config.output_mode,
        compress_positions=game_state.config.compress_positions,
        compress_symbols=game_state.config.compress_symbols,
    )

    special_attributes = list(game_state.config.special_symbols.keys())

    exploding_raw: list[dict[str, int]] = []
    for win in game_state.win_data["wins"]:
        for pos in win["positions"]:
            if game_state.config.include_padding:
                exploding_raw.append({"reel": pos["reel"], "row": pos["row"] + 1})
            else:
                exploding_raw.append({"reel": pos["reel"], "row": pos["row"]})

    exploding_raw = sorted(exploding_raw, key=lambda x: x["reel"])

    # Format positions
    exploding = formatter.format_position_list(exploding_raw)

    new_symbols: list[list[Any]] = [[] for _ in range(game_state.config.num_reels)]
    for r, _ in enumerate(game_state.new_symbols_from_tumble):
        if len(game_state.new_symbols_from_tumble[r]) > 0:
            new_symbols[r] = [
                formatter.format_symbol(s, special_attributes)
                for s in game_state.new_symbols_from_tumble[r]
            ]

    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.TUMBLE_BOARD.value,
        "newSymbols": new_symbols,
        "explodingSymbols": exploding,
    }
    game_state.book.add_event(event)


def upgrade_event(
    game_state: Any,
    win_symbol: str,
    upgrade_position: dict[str, int],
    from_positions: list[dict[str, int]],
) -> None:
    """Generate upgrade event for a winning symbol.

    Creates an UPGRADE event when a symbol is upgraded based on cluster size.
    Only applicable for games with upgrade_config defined.

    Args:
        game_state: Current game state with config
        win_symbol: Symbol name that triggered the upgrade
        upgrade_position: Position where upgraded symbol appears
        from_positions: List of positions in the winning cluster
    """
    # Check if game has upgrade configuration
    if not hasattr(game_state.config, "upgrade_config"):
        return

    upgrade_config = game_state.config.upgrade_config
    symbol_map = upgrade_config["symbol_map"]
    thresholds = upgrade_config["thresholds"]

    # Check if symbol can be upgraded
    if win_symbol not in symbol_map:
        return

    # Determine upgrade target based on cluster count
    cluster_count = len(from_positions)
    if cluster_count >= thresholds["high"]:
        upgrade_target = symbol_map[win_symbol]["H"]
    elif cluster_count >= thresholds["medium"]:
        upgrade_target = symbol_map[win_symbol]["M"]
    else:
        # No upgrade for clusters smaller than medium threshold
        return

    # Create OutputFormatter from config settings
    formatter = OutputFormatter(
        output_mode=game_state.config.output_mode,
        compress_positions=game_state.config.compress_positions,
    )

    # Format positions
    formatted_position = formatter.format_position(
        upgrade_position["reel"], upgrade_position["row"]
    )
    formatted_from_positions = formatter.format_position_list(from_positions)

    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.UPGRADE.value,
        "symbol": {"name": upgrade_target},
        "position": formatted_position,
        "fromPositions": formatted_from_positions,
    }
    game_state.book.add_event(event)


def prize_win_event(game_state: Any, include_padding_index: bool = True) -> None:
    """Generate prize payout events for M and H symbols on the board.

    Creates a WIN event with reason "prize" for all prize symbols found
    on the board. Only applicable for games with prize_config defined.

    Args:
        game_state: Current game state with board and config
        include_padding_index: If True, offset row positions by 1 for padding symbols
    """
    # Check if game has prize configuration
    if not hasattr(game_state.config, "prize_config"):
        return

    # Create OutputFormatter from config settings
    formatter = OutputFormatter(
        output_mode=game_state.config.output_mode,
        compress_positions=game_state.config.compress_positions,
    )

    prize_config = game_state.config.prize_config
    prize_symbols = prize_config["symbols"]
    prize_paytable = prize_config["paytable"]

    # Find all prize symbols on the board
    prize_positions: dict[str, list[dict[str, int]]] = {}

    for reel_idx, reel in enumerate(game_state.board):
        for row_idx, symbol in enumerate(reel):
            if symbol.name in prize_symbols:
                if symbol.name not in prize_positions:
                    prize_positions[symbol.name] = []

                position: dict[str, int] = {"reel": reel_idx, "row": row_idx}
                if include_padding_index:
                    position["row"] += 1
                prize_positions[symbol.name].append(position)

    # Generate prize payout events if any prize symbols found
    if prize_positions:
        total_prize_amount = 0
        details: list[dict[str, Any]] = []

        for symbol_name, positions in prize_positions.items():
            count = len(positions)
            symbol_payout = prize_paytable.get(symbol_name, 0)
            amount = int(round(symbol_payout * count * 100, 0))
            total_prize_amount += amount

            # Format positions
            formatted_positions = formatter.format_position_list(positions)

            details.append(
                {
                    "symbol": symbol_name,
                    "positions": formatted_positions,
                    "amount": amount,
                    "count": count,
                    "baseAmount": amount,
                    "multiplier": 1,
                }
            )

        # Add the prize win to the current spin win and running bet win
        game_state.win_manager.spin_win += total_prize_amount / 100
        game_state.win_manager.running_bet_win += total_prize_amount / 100

        # Create the prize payout event
        event: dict[str, Any] = {
            "index": len(game_state.book.events),
            "type": EventConstants.WIN.value,
            "reason": "prize",
            "amount": total_prize_amount,
            "totalAmount": int(
                round(
                    min(
                        game_state.win_manager.running_bet_win,
                        game_state.config.win_cap,
                    )
                    * 100,
                    0,
                )
            ),
            "details": details,
        }
        game_state.book.add_event(event)
