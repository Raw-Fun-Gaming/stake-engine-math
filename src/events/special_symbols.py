"""Special symbol event functions.

Includes upgrade, global multiplier, and prize win events.
Only needed by games with these specific mechanics.
"""

from __future__ import annotations

from typing import Any

from src.events.constants import EventConstants
from src.formatter import OutputFormatter


def update_global_mult_event(game_state: Any) -> None:
    """Increment global multiplier display.

    Creates an UPDATE_GLOBAL_MULTIPLIER event showing the current multiplier value.

    Args:
        game_state: Current game state with global_multiplier
    """
    event: dict[str, Any] = {
        "index": len(game_state.book.events),
        "type": EventConstants.UPDATE_GLOBAL_MULTIPLIER.value,
        "globalMultiplier": int(game_state.global_multiplier),
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
