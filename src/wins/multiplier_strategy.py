"""Global multipliers, symbol multipliers, combined multipliers or no actions.

All functions return [final_win_amount], [applied multiplier].
"""

from src.calculations.board import Board


def apply_multiplier(
    board: Board,
    strategy: str,
    win_amount: float = 0.0,
    global_multiplier: int = 1,
    positions: list = [],
    multiplier_key: str = "multiplier",
):
    """Apply multiplier method to win_amount and winning symbol positions."""
    strategies = {
        "global": apply_global_multiplier(win_amount, global_multiplier),
        "symbol": apply_symbol_multiplier(
            board, win_amount, positions, multiplier_key=multiplier_key
        ),
        "combined": apply_combined_multiplier(
            board,
            win_amount,
            global_multiplier,
            positions,
            multiplier_key=multiplier_key,
        ),
    }
    return strategies[strategy]


def apply_global_multiplier(win_amount: float, global_multiplier: int) -> tuple:
    """Enhance win global multiplier"""
    return (round(win_amount * global_multiplier, 2), global_multiplier)


def apply_symbol_multiplier(
    board: Board, win_amount: float, positions: list[dict], multiplier_key: str
) -> tuple:
    """Get multiplier attribute from all winning positions"""
    symbol_multiplier = 0
    for pos in positions:
        if (
            board[pos["reel"]][pos["row"]].check_attribute(multiplier_key)
            and board[pos["reel"]][pos["row"]].get_attribute(multiplier_key) > 1
        ):
            symbol_multiplier += board[pos["reel"]][pos["row"]].get_attribute(
                multiplier_key
            )
    return (round(win_amount * max(symbol_multiplier, 1), 2), max(symbol_multiplier, 1))


def apply_combined_multiplier(
    board: Board,
    win_amount: float,
    global_multiplier: int,
    positions: list[dict],
    multiplier_key,
) -> tuple:
    """Apply symbol multipliers and then global multiplier"""
    win, symbol_multiplier_total = apply_symbol_multiplier(
        board, win_amount, positions, multiplier_key
    )
    return (win * global_multiplier, symbol_multiplier_total * global_multiplier)
