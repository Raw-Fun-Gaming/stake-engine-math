"""Scatter-pay calculation for slot games.

This module handles detection and evaluation of scatter/pay-anywhere wins.
Symbols pay based on total count anywhere on the board, not requiring
specific positions or adjacency.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.calculations.symbol import Symbol
    from src.config.config import Config

# Type aliases for clarity
Position = dict[str, int]
Board = list[list["Symbol"]]


class Scatter:
    """Collection of scatter-pay functions.

    Provides static methods for:
    - Finding scatter symbols anywhere on the board
    - Calculating payouts based on symbol count
    - Determining overlay display positions
    - Recording wins for optimization tracking
    """

    @staticmethod
    def get_central_scatter_position(
        rows_for_overlay: list[int],
        winning_positions: list[Position],
        max_reels: int,
        max_rows: int,
    ) -> tuple[int, int]:
        """Find optimal position to display scatter win amount.

        Selects position closest to board center that hasn't been used yet
        for overlay display.

        Args:
            rows_for_overlay: List of row indices already used for overlays
            winning_positions: List of position dicts with "reel" and "row" keys
            max_reels: Total number of reels on the board
            max_rows: Total number of rows on the board

        Returns:
            Tuple (reel, row) representing best overlay position
        """
        closest_to_middle: float = 100.0
        reel_to_overlay: int = 0
        row_to_overlay: int = 0
        for pos in winning_positions:
            reel: int = pos["reel"]
            row: int = pos["row"]
            dist_from_middle: float = (reel - max_reels / 2) ** 2 + (
                row - max_rows / 2
            ) ** 2
            if (
                dist_from_middle < closest_to_middle
                and row not in rows_for_overlay
                and len(rows_for_overlay) < max_reels
            ):
                closest_to_middle = dist_from_middle
                reel_to_overlay = reel
                row_to_overlay = row

        return (reel_to_overlay, row_to_overlay)

    @staticmethod
    def get_scatterpay_wins(
        config: Config,
        board: Board,
        wild_key: str = "wild",
        multiplier_key: str = "multiplier",
        global_multiplier: int = 1,
    ) -> dict[str, Any]:
        """Calculate scatter wins for all symbols on the board.

        Counts each symbol type anywhere on the board and pays based on total
        count. Wilds substitute for all symbols and can appear multiple times.

        Args:
            config: Game configuration with paytable and special symbols
            board: 2D list of Symbol objects [reel][row]
            wild_key: Attribute name for wild symbols (default: "wild")
            multiplier_key: Attribute name for symbol multipliers (default: "multiplier")
            global_multiplier: Global win multiplier (default: 1)

        Returns:
            Dict with "totalWin" (float) and "wins" (list of scatter win dicts)
        """
        return_data: dict[str, Any] = {
            "totalWin": 0.0,
            "wins": [],
        }
        rows_for_overlay: list[int] = []
        symbols_on_board: dict[str, list[Position]] = defaultdict(list)
        wild_positions: list[Position] = []
        total_win: float = 0.0
        for reel_idx, reel in enumerate(board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name not in config.special_symbols[wild_key]:  # type: ignore[attr-defined]
                    symbols_on_board[symbol.name].append(
                        {"reel": reel_idx, "row": row_idx}
                    )
                else:
                    wild_positions.append({"reel": reel_idx, "row": row_idx})

        # Update all symbol positions with wilds, as this symbol is shared
        for sym in symbols_on_board:
            if len(wild_positions) > 0:
                symbols_on_board[sym].extend(wild_positions)
            win_size: int = len(symbols_on_board[sym])
            if (win_size, sym) in config.paytable:
                symbol_mult: int = 0
                for p in symbols_on_board[sym]:
                    if board[p["reel"]][p["row"]].check_attribute(multiplier_key):
                        symbol_mult += int(
                            board[p["reel"]][p["row"]].get_attribute(multiplier_key)
                        )

                    board[p["reel"]][p["row"]].assign_attribute({"explode": True})

                symbol_mult = max(symbol_mult, 1)
                overlay_position: tuple[int, int] = (
                    Scatter.get_central_scatter_position(
                        rows_for_overlay,
                        symbols_on_board[sym],
                        len(board),
                        len(board[0]),
                    )
                )
                rows_for_overlay.append(overlay_position[1])
                symbol_win_data: dict[str, Any] = {
                    "symbol": sym,
                    "win": config.paytable[(win_size, sym)]
                    * global_multiplier
                    * symbol_mult,
                    "positions": symbols_on_board[sym],
                    "meta": {
                        "globalMult": global_multiplier,
                        "clusterMult": symbol_mult,
                        "winWithoutMult": config.paytable[(win_size, sym)],
                        "overlay": {
                            "reel": overlay_position[0],
                            "row": overlay_position[1],
                        },
                    },
                }
                total_win += symbol_win_data["win"]
                return_data["wins"].append(symbol_win_data)

        return_data["totalWin"] = total_win

        return return_data

    @staticmethod
    def record_scatter_wins(gamestate: Any) -> None:
        """Record scatter wins to force tracking system for optimization.

        Extracts win description keys (symbol count, symbol, total multiplier, gametype)
        and records them to the gamestate for distribution optimization.

        Args:
            gamestate: Game state instance with win_data and record() method
        """
        for win in gamestate.win_data["wins"]:
            gamestate.record(
                {
                    "kind": len(win["positions"]),
                    "symbol": win["symbol"],
                    "totalMult": int(
                        win["meta"]["globalMult"] + win["meta"]["clusterMult"]
                    ),
                    "gametype": gamestate.gametype,
                }
            )
