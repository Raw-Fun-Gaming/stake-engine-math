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


def reveal_event(gamestate: Any) -> None:
    """Display the initial board drawn from reel strips.

    Creates a REVEAL event showing the current board state with all symbols.
    Optionally includes padding symbols (top/bottom) if configured.

    Args:
        gamestate: Current game state with board and configuration
    """
    # Create OutputFormatter from config settings
    formatter = OutputFormatter(
        output_mode=gamestate.config.output_mode,
        include_losing_boards=gamestate.config.include_losing_boards,
        compress_positions=gamestate.config.compress_positions,
        compress_symbols=gamestate.config.compress_symbols,
        skip_implicit_events=gamestate.config.skip_implicit_events,
    )

    # Check if we should skip this reveal (losing board with include_losing_boards=False)
    # Note: We need to check final win, but at reveal time we don't know it yet
    # So we'll always include reveals and let books writing filter them out if needed

    special_attributes = list(gamestate.config.special_symbols.keys())

    # Use formatter to format the board
    board_client: list[list[Any]] = []
    for reel, _ in enumerate(gamestate.board):
        board_client.append([])
        for row in range(len(gamestate.board[reel])):
            board_client[reel].append(
                formatter.format_symbol(gamestate.board[reel][row], special_attributes)
            )

    if gamestate.config.include_padding:
        for reel, _ in enumerate(board_client):
            board_client[reel] = [
                formatter.format_symbol(gamestate.top_symbols[reel], special_attributes)
            ] + board_client[reel]
            board_client[reel].append(
                formatter.format_symbol(gamestate.bottom_symbols[reel], special_attributes)
            )

    event: dict[str, Any] = {
        "index": len(gamestate.book.events),
        "type": EventConstants.REVEAL.value,
        "board": board_client,
        "paddingPositions": gamestate.reel_positions,
        "gameType": gamestate.gametype,
        "anticipation": gamestate.anticipation,
    }
    gamestate.book.add_event(event)


def trigger_free_spins_event(
    gamestate: Any,
    include_padding_index: bool = True,
    basegame_trigger: bool | None = None,
    freegame_trigger: bool | None = None,
) -> None:
    """Trigger or retrigger free spins feature.

    Creates either a TRIGGER_FREE_SPINS or RETRIGGER_FREE_SPINS event
    depending on whether it's called from base game or during free spins.

    Args:
        gamestate: Current game state with scatter positions
        include_padding_index: Whether to offset row positions by 1 for padding
        basegame_trigger: True if triggering from base game
        freegame_trigger: True if retriggering during free spins

    Raises:
        AssertionError: If both or neither trigger flags are set, or if tot_fs <= 0
    """
    assert (
        basegame_trigger != freegame_trigger
    ), "must set either basegame_trigger or freeSpinTrigger to = True"

    # Create OutputFormatter from config settings
    formatter = OutputFormatter(
        output_mode=gamestate.config.output_mode,
        compress_positions=gamestate.config.compress_positions,
    )

    event: dict[str, Any] = {}
    scatter_positions: list[dict[str, int]] = []
    for reel, _ in enumerate(gamestate.special_syms_on_board["scatter"]):
        scatter_positions.append(gamestate.special_syms_on_board["scatter"][reel])
    if include_padding_index:
        for pos in scatter_positions:
            pos["row"] += 1

    # Format positions using the formatter
    formatted_positions = formatter.format_position_list(scatter_positions)

    if basegame_trigger:
        event = {
            "index": len(gamestate.book.events),
            "type": EventConstants.TRIGGER_FREE_SPINS.value,
            "total": gamestate.tot_fs,
            "positions": formatted_positions,
        }
    elif freegame_trigger:
        event = {
            "index": len(gamestate.book.events),
            "type": EventConstants.RETRIGGER_FREE_SPINS.value,
            "total": gamestate.tot_fs,
            "positions": formatted_positions,
        }

    assert gamestate.tot_fs > 0, "total freegame (gamestate.tot_fs) must be >0"
    gamestate.book.add_event(event)


def set_win_event(gamestate: Any, winlevel_key: str = "standard") -> None:
    """Update cumulative win ticker for a single outcome.

    Creates a SET_WIN event showing the current spin win amount and win level.
    Only emitted if win cap hasn't been triggered yet.

    Args:
        gamestate: Current game state with win manager
        winlevel_key: Key for win level configuration (default: "standard")
    """
    if not gamestate.wincap_triggered:
        event: dict[str, Any] = {
            "index": len(gamestate.book.events),
            "type": EventConstants.SET_WIN.value,
            "amount": int(
                min(
                    round(gamestate.win_manager.spin_win * 100, 0),
                    gamestate.config.wincap * 100,
                )
            ),
            "winLevel": gamestate.config.get_win_level(
                gamestate.win_manager.spin_win, winlevel_key
            ),
        }
        gamestate.book.add_event(event)


def set_total_win_event(gamestate: Any) -> None:
    """Update win amount for entire betting round.

    Creates a SET_TOTAL_WIN event showing cumulative wins across multiple
    outcomes (e.g., base game + all free spins).

    Args:
        gamestate: Current game state with win manager
    """
    event: dict[str, Any] = {
        "index": len(gamestate.book.events),
        "type": EventConstants.SET_TOTAL_WIN.value,
        "amount": int(
            round(
                min(gamestate.win_manager.running_bet_win, gamestate.config.wincap)
                * 100,
                0,
            )
        ),
    }
    gamestate.book.add_event(event)


def set_tumble_win_event(gamestate: Any) -> None:
    """Update banner showing wins from successive tumbles.

    Creates a SET_TUMBLE_WIN event displaying accumulated tumble wins.

    Args:
        gamestate: Current game state with tumble_win tracking
    """
    event: dict[str, Any] = {
        "index": len(gamestate.book.events),
        "type": EventConstants.SET_TUMBLE_WIN.value,
        "amount": int(round(min(gamestate.tumble_win, gamestate.config.wincap) * 100)),
    }
    gamestate.book.add_event(event)


def win_cap_event(gamestate: Any) -> None:
    """Emit event indicating win cap has been reached.

    Creates a WIN_CAP event when the maximum payout limit is hit,
    signaling the end of spin actions.

    Args:
        gamestate: Current game state with win manager
    """
    event: dict[str, Any] = {
        "index": len(gamestate.book.events),
        "type": EventConstants.WIN_CAP.value,
        "amount": int(
            round(
                min(gamestate.win_manager.running_bet_win, gamestate.config.wincap)
                * 100,
                0,
            )
        ),
    }
    gamestate.book.add_event(event)


def win_event(gamestate: Any, include_padding_index: bool = True) -> None:
    """Create a WIN event with detailed win information.

    Transforms internal win data into client-ready format, handling position
    adjustments for padding, converting field names, and extracting metadata.

    Args:
        gamestate: Current game state with win_data
        include_padding_index: If True, offset row positions by 1 for padding symbols
    """
    win_data_copy: dict[str, Any] = {}
    win_data_copy["details"] = deepcopy(gamestate.win_data["wins"])
    for idx, w in enumerate(win_data_copy["details"]):
        if include_padding_index:
            new_positions: list[dict[str, int]] = []
            for p in w["positions"]:
                new_positions.append({"reel": p["reel"], "row": p["row"] + 1})
        else:
            new_positions = w["positions"]

        win_data_copy["details"][idx]["amount"] = int(
            round(
                min(win_data_copy["details"][idx]["win"], gamestate.config.wincap)
                * 100,
                0,
            )
        )
        win_data_copy["details"][idx]["positions"] = new_positions

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
                        gamestate.config.wincap * 100,
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
        "index": len(gamestate.book.events),
        "type": EventConstants.WIN.value,
        "reason": "cluster",
        "amount": int(
            round(min(gamestate.win_data["totalWin"], gamestate.config.wincap) * 100, 0)
        ),
        "totalAmount": int(
            round(
                min(gamestate.win_manager.running_bet_win, gamestate.config.wincap)
                * 100,
                0,
            )
        ),
        "details": win_data_copy["details"],
    }
    gamestate.book.add_event(event)


def update_tumble_win_event(gamestate: Any) -> None:
    """Update banner to record successive tumble wins.

    Creates an UPDATE_TUMBLE_WIN event showing accumulated wins from cascades.

    Args:
        gamestate: Current game state with win manager
    """
    event: dict[str, Any] = {
        "index": len(gamestate.book.events),
        "type": EventConstants.UPDATE_TUMBLE_WIN.value,
        "amount": int(
            round(min(gamestate.win_manager.spin_win, gamestate.config.wincap) * 100, 0)
        ),
    }
    gamestate.book.add_event(event)


def update_free_spins_event(gamestate: Any) -> None:
    """Update current free spin counter.

    Creates an UPDATE_FREE_SPINS event showing the current spin number
    and total free spins awarded.

    Args:
        gamestate: Current game state with fs and tot_fs counters
    """
    event: dict[str, Any] = {
        "index": len(gamestate.book.events),
        "type": EventConstants.UPDATE_FREE_SPINS.value,
        "amount": int(gamestate.fs),
        "total": int(gamestate.tot_fs),
    }
    gamestate.book.add_event(event)


def end_free_spins_event(gamestate: Any, winlevel_key: str = "endFeature") -> None:
    """Signal end of free spins feature.

    Creates an END_FREE_SPINS event with total feature wins and win level.

    Args:
        gamestate: Current game state with win manager
        winlevel_key: Key for win level configuration (default: "endFeature")
    """
    event: dict[str, Any] = {
        "index": len(gamestate.book.events),
        "type": EventConstants.END_FREE_SPINS.value,
        "amount": int(
            min(gamestate.win_manager.freegame_wins, gamestate.config.wincap) * 100
        ),
        "winLevel": gamestate.config.get_win_level(
            gamestate.win_manager.freegame_wins, winlevel_key
        ),
    }
    gamestate.book.add_event(event)


def set_final_win_event(gamestate: Any) -> None:
    """Assign final payout multiplier for simulation.

    Creates a SET_FINAL_WIN event with the capped total payout.

    Args:
        gamestate: Current game state with final_win calculated
    """
    event: dict[str, Any] = {
        "index": len(gamestate.book.events),
        "type": EventConstants.SET_FINAL_WIN.value,
        "amount": int(
            round(min(gamestate.final_win, gamestate.config.wincap) * 100, 0)
        ),
    }
    gamestate.book.add_event(event)


def update_global_mult_event(gamestate: Any) -> None:
    """Increment global multiplier display.

    Creates an UPDATE_GLOBAL_MULT event showing the current multiplier value.

    Args:
        gamestate: Current game state with global_multiplier
    """
    event: dict[str, Any] = {
        "index": len(gamestate.book.events),
        "type": EventConstants.UPDATE_GLOBAL_MULT.value,
        "globalMult": int(gamestate.global_multiplier),
    }

    gamestate.book.add_event(event)


def tumble_board_event(gamestate: Any) -> None:
    """Create tumble/cascade event showing exploded and new symbols.

    Generates a TUMBLE_BOARD event listing which symbols were removed
    and which new symbols drop in to replace them.

    Args:
        gamestate: Current game state with win_data and new_symbols_from_tumble
    """
    special_attributes = list(gamestate.config.special_symbols.keys())

    exploding: list[dict[str, int]] = []
    for win in gamestate.win_data["wins"]:
        for pos in win["positions"]:
            if gamestate.config.include_padding:
                exploding.append({"reel": pos["reel"], "row": pos["row"] + 1})
            else:
                exploding.append({"reel": pos["reel"], "row": pos["row"]})

    exploding = sorted(exploding, key=lambda x: x["reel"])

    new_symbols: list[list[dict[str, Any]]] = [
        [] for _ in range(gamestate.config.num_reels)
    ]
    for r, _ in enumerate(gamestate.new_symbols_from_tumble):
        if len(gamestate.new_symbols_from_tumble[r]) > 0:
            new_symbols[r] = [
                json_ready_sym(s, special_attributes)
                for s in gamestate.new_symbols_from_tumble[r]
            ]

    event: dict[str, Any] = {
        "index": len(gamestate.book.events),
        "type": EventConstants.TUMBLE_BOARD.value,
        "newSymbols": new_symbols,
        "explodingSymbols": exploding,
    }
    gamestate.book.add_event(event)


def upgrade_event(
    gamestate: Any,
    win_symbol: str,
    upgrade_position: dict[str, int],
    from_positions: list[dict[str, int]],
) -> None:
    """Generate upgrade event for a winning symbol.

    Creates an UPGRADE event when a symbol is upgraded based on cluster size.
    Only applicable for games with upgrade_config defined.

    Args:
        gamestate: Current game state with config
        win_symbol: Symbol name that triggered the upgrade
        upgrade_position: Position where upgraded symbol appears
        from_positions: List of positions in the winning cluster
    """
    # Check if game has upgrade configuration
    if not hasattr(gamestate.config, "upgrade_config"):
        return

    upgrade_config = gamestate.config.upgrade_config
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

    event: dict[str, Any] = {
        "index": len(gamestate.book.events),
        "type": EventConstants.UPGRADE.value,
        "symbol": {"name": upgrade_target},
        "position": upgrade_position,
        "fromPositions": from_positions,
    }
    gamestate.book.add_event(event)


def prize_win_event(gamestate: Any, include_padding_index: bool = True) -> None:
    """Generate prize payout events for M and H symbols on the board.

    Creates a WIN event with reason "prize" for all prize symbols found
    on the board. Only applicable for games with prize_config defined.

    Args:
        gamestate: Current game state with board and config
        include_padding_index: If True, offset row positions by 1 for padding symbols
    """
    # Check if game has prize configuration
    if not hasattr(gamestate.config, "prize_config"):
        return

    prize_config = gamestate.config.prize_config
    prize_symbols = prize_config["symbols"]
    prize_paytable = prize_config["paytable"]

    # Find all prize symbols on the board
    prize_positions: dict[str, list[dict[str, int]]] = {}

    for reel_idx, reel in enumerate(gamestate.board):
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

            details.append(
                {
                    "symbol": symbol_name,
                    "positions": positions,
                    "amount": amount,
                    "count": count,
                    "baseAmount": amount,
                    "multiplier": 1,
                }
            )

        # Add the prize win to the current spin win and running bet win
        gamestate.win_manager.spin_win += total_prize_amount / 100
        gamestate.win_manager.running_bet_win += total_prize_amount / 100

        # Create the prize payout event
        event: dict[str, Any] = {
            "index": len(gamestate.book.events),
            "type": EventConstants.WIN.value,
            "reason": "prize",
            "amount": total_prize_amount,
            "totalAmount": int(
                round(
                    min(gamestate.win_manager.running_bet_win, gamestate.config.wincap)
                    * 100,
                    0,
                )
            ),
            "details": details,
        }
        gamestate.book.add_event(event)
