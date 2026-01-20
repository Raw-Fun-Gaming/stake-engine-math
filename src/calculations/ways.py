"""Ways-pay calculation for slot games.

This module handles detection and evaluation of winning ways for ways-pay
games. Counts all possible paths from left to right with matching symbols,
including wild substitutions and symbol multipliers.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any

from src.events.events import set_total_win_event, set_win_event, win_event
from src.wins.multiplier_strategy import apply_mult

if TYPE_CHECKING:
    from src.calculations.symbol import Symbol
    from src.config.config import Config

# Type aliases for clarity
Position = dict[str, int]
Board = list[list["Symbol"]]


class Ways:
    """Collection of ways-win functions.

    Provides static methods for:
    - Counting all possible winning paths (ways)
    - Handling wild substitutions on each reel
    - Calculating payouts with symbol and global multipliers
    - Recording wins for optimization tracking
    """

    @staticmethod
    def get_ways_data(
        config: Config,
        board: Board,
        wild_key: str = "wild",
        multiplier_key: str = "multiplier",
    ) -> dict[str, Any]:
        """Calculate all ways wins on the board.

        Counts all possible winning paths from left to right for each symbol.
        Ways are multiplied by the number of matching symbols on each reel,
        including wilds and symbol multipliers.

        Args:
            config: Game configuration with paytable and special symbols
            board: 2D list of Symbol objects [reel][row]
            wild_key: Attribute name for wild symbols (default: "wild")
            multiplier_key: Attribute name for symbol multipliers (default: "multiplier")

        Returns:
            Dict with "totalWin" (float) and "wins" (list of ways win dicts)
        """
        return_data: dict[str, Any] = {
            "totalWin": 0.0,
            "wins": [],
        }
        potential_wins: dict[str, list[list[Position]]] = defaultdict(
            lambda: [[] for _ in range(len(board))]
        )
        wilds: list[list[Position]] = [[] for _ in range(len(board))]
        for reel, _ in enumerate(board):
            for row, _ in enumerate(board[reel]):
                sym: Symbol = board[reel][row]
                if reel == 0 and sym.name not in potential_wins:
                    potential_wins[sym.name] = [[] for _ in range(len(board))]
                    potential_wins[sym.name][0] = [{"reel": reel, "row": row}]
                elif sym.name in potential_wins:
                    potential_wins[sym.name][reel].append({"reel": reel, "row": row})

                if sym.name in config.special_symbols[wild_key]:  # type: ignore[attr-defined]
                    wilds[reel].append({"reel": reel, "row": row})

        for symbol in potential_wins:
            kind: int = 0
            ways: int = 1
            cumulative_symbol_multiplier: int = 0
            for reel, _ in enumerate(potential_wins[symbol]):
                if len(potential_wins[symbol][reel]) > 0 or len(wilds[reel]) > 0:
                    kind += 1
                    multiplier_enhance: int = 0
                    # Note that here multipliers on subsequent reels multiplier (not add, like in lines games)
                    for s in potential_wins[symbol][reel]:
                        if (
                            board[s["reel"]][s["row"]].check_attribute(multiplier_key)
                            and board[s["reel"]][s["row"]].get_attribute(multiplier_key)
                            > 1
                        ):
                            multiplier_enhance += board[s["reel"]][
                                s["row"]
                            ].get_attribute(multiplier_key)
                    for s in wilds[reel]:
                        if (
                            board[s["reel"]][s["row"]].check_attribute(multiplier_key)
                            and board[s["reel"]][s["row"]].get_attribute(multiplier_key)
                            > 1
                        ):
                            multiplier_enhance += board[s["reel"]][
                                s["row"]
                            ].get_attribute(multiplier_key)

                    ways *= (
                        len(potential_wins[symbol][reel])
                        + len(wilds[reel])
                        + multiplier_enhance
                    )
                    cumulative_symbol_multiplier += multiplier_enhance
                else:
                    break

            if (kind, symbol) in config.paytable:
                positions: list[Position] = []
                for reel in range(kind):
                    for pos in potential_wins[symbol][reel]:
                        positions += [pos]
                    for pos in wilds[reel]:
                        positions += [pos]

                win: float = config.paytable[kind, symbol] * ways
                win_amt: float
                multiplier: float
                win_amt, multiplier = apply_mult(board=board, strategy="global", win_amount=win)  # type: ignore[arg-type]
                return_data["wins"] += [
                    {
                        "symbol": symbol,
                        "kind": kind,
                        "win": win_amt,
                        "positions": positions,
                        "meta": {
                            "ways": ways,
                            "globalMultiplier": multiplier,
                            "winWithoutMult": win,
                            "symbolMult": cumulative_symbol_multiplier,
                        },
                    }
                ]
                return_data["totalWin"] += win

        return return_data

    @staticmethod
    def emit_wayswin_events(game_state: Any) -> None:
        """Emit win events for ways wins.

        Creates WIN, SET_WIN, and SET_TOTAL_WIN events based on spin results.
        Only emits WIN event if there are actual ways wins.

        Args:
            game_state: Current game state with win_manager and win_data
        """
        if game_state.win_manager.spin_win > 0:
            win_event(game_state)
            game_state.evaluate_wincap()
            set_win_event(game_state)
        set_total_win_event(game_state)

    @staticmethod
    def record_ways_wins(game_state: Any) -> None:
        """Record ways wins to force tracking system for optimization.

        Extracts win description keys (symbol count, symbol, ways, game_type)
        and records them to the game_state for distribution optimization.

        Args:
            game_state: Game state instance with win_data and record() method
        """
        for win in game_state.win_data["wins"]:
            game_state.record(
                {
                    "kind": len(win["positions"]),
                    "symbol": win["symbol"],
                    "ways": win["meta"]["ways"],
                    "game_type": game_state.game_type,
                }
            )
