"""Line-pay calculation for slot games.

This module handles detection and evaluation of winning paylines for
traditional line-pay games. Includes left-to-right symbol matching,
wild substitution, and multiplier application.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.events.events import set_total_win_event, set_win_event, win_event
from src.wins.multiplier_strategy import apply_mult

if TYPE_CHECKING:
    from src.calculations.symbol import Symbol
    from src.config.config import Config

# Type aliases for clarity
Position = dict[str, int]
Board = list[list["Symbol"]]


class Lines:
    """Collection of functions to handle line-win games.

    Provides static methods for:
    - Finding winning symbol combinations on paylines
    - Handling wild substitutions
    - Calculating line payouts with multipliers
    - Recording wins for optimization tracking
    """

    @staticmethod
    def line_win_info(
        symbol: str,
        kind: int,
        win: float,
        positions: list[Position],
        meta_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Construct line-win dictionary for event generation.

        Args:
            symbol: Winning symbol name
            kind: Number of matching symbols
            win: Win amount after multipliers
            positions: List of position dicts with "reel" and "row" keys
            meta_data: Metadata including line index, multipliers, base win

        Returns:
            Dictionary containing all line win information
        """
        return {
            "symbol": symbol,
            "kind": kind,
            "win": win,
            "positions": positions,
            "meta": meta_data,
        }

    @staticmethod
    def get_lines(
        board: Board,
        config: Config,
        wild_key: str = "wild",
        wild_sym: str = "W",
        multiplier_method: str = "symbol",
        global_multiplier: int = 1,
    ) -> dict[str, Any]:
        """Calculate all line wins on the board.

        Scans each payline from left to right, matching symbols with wild
        substitution. Determines whether pure wild wins or symbol wins pay more.

        Args:
            board: 2D list of Symbol objects [reel][row]
            config: Game configuration with paylines and paytable
            wild_key: Attribute name for wild symbols (default: "wild")
            wild_sym: Symbol name for wilds in paytable (default: "W")
            multiplier_method: Method for multiplier application (default: "symbol")
            global_multiplier: Global win multiplier (default: 1)

        Returns:
            Dict with "totalWin" (float) and "wins" (list of line win dicts)
        """
        return_data: dict[str, Any] = {
            "totalWin": 0.0,
            "wins": [],
        }

        for line_index in config.paylines.keys():  # type: ignore[attr-defined]
            line: list[int] = config.paylines[line_index]  # type: ignore[attr-defined]
            first_sym: Symbol = board[0][line[0]]
            finished_wild_win: bool = (
                False if first_sym.check_attribute(wild_key) else True
            )
            first_non_wild: Symbol | None = first_sym if finished_wild_win else None
            potential_line: list[Symbol] = [first_sym]

            wild_matches: int = 0 * (finished_wild_win) + 1 * (not (finished_wild_win))
            matches: int = 1 * (finished_wild_win) + 0 * (not (finished_wild_win))
            base_win: float = 0.0
            wild_win: float = 0.0

            for reel in range(1, len(line)):
                sym: Symbol = board[reel][line[reel]]
                if finished_wild_win:
                    if sym.name == first_non_wild.name or sym.check_attribute(wild_key):
                        matches += 1
                    else:
                        break
                else:
                    if sym.check_attribute(wild_key) and first_non_wild is None:
                        wild_matches += 1
                    elif first_non_wild is None:
                        first_non_wild = sym
                        matches += 1
                        finished_wild_win = True
                    else:
                        break
                potential_line.append(sym)

            if (wild_matches, wild_sym) in config.paytable:
                wild_win = config.paytable[(wild_matches, wild_sym)]
            if first_non_wild is not None:
                if (wild_matches + matches, first_non_wild.name) in config.paytable:
                    base_win = config.paytable[
                        (wild_matches + matches, first_non_wild.name)
                    ]

            if base_win > 0 or wild_win > 0:
                if wild_win > base_win:
                    positions: list[Position] = [
                        {"reel": idx, "row": line[idx]}
                        for idx in range(0, wild_matches)
                    ]
                    line_win: float
                    applied_mult: float
                    line_win, applied_mult = apply_mult(
                        board, multiplier_method, win_amount=wild_win, positions=positions  # type: ignore[arg-type]
                    )
                    win_dict: dict[str, Any] = Lines.line_win_info(
                        potential_line[0].name,
                        wild_matches,
                        line_win,
                        positions,
                        {
                            "lineIndex": line_index,
                            "multiplier": applied_mult,
                            "winWithoutMult": wild_win,
                            "globalMultiplier": int(global_multiplier),
                            "lineMultiplier": int(applied_mult / global_multiplier),
                        },
                    )
                else:
                    positions = [
                        {"reel": idx, "row": line[idx]}
                        for idx in range(0, matches + wild_matches)
                    ]
                    line_win, applied_mult = apply_mult(
                        board, multiplier_method, win_amount=base_win, positions=positions  # type: ignore[arg-type]
                    )
                    win_dict = Lines.line_win_info(
                        first_non_wild.name,
                        matches + wild_matches,
                        line_win,
                        positions,
                        {
                            "lineIndex": line_index,
                            "multiplier": applied_mult,
                            "winWithoutMult": base_win,
                            "globalMultiplier": int(global_multiplier),
                            "lineMultiplier": int(applied_mult / global_multiplier),
                        },
                    )

                return_data["totalWin"] += line_win
                return_data["wins"].append(win_dict)

        return return_data

    @staticmethod
    def emit_linewin_events(game_state: Any) -> None:
        """Emit win events for line wins.

        Creates WIN, SET_WIN, and SET_TOTAL_WIN events based on spin results.
        Only emits WIN event if there are actual line wins.

        Args:
            game_state: Current game state with win_manager and win_data
        """
        if game_state.win_manager.spin_win > 0:
            win_event(game_state)
            game_state.evaluate_wincap()
            set_win_event(game_state)
        set_total_win_event(game_state)

    @staticmethod
    def record_lines_wins(game_state: Any) -> None:
        """Record line wins to force tracking system for optimization.

        Extracts win description keys (line length, symbol, multiplier, game_type)
        and records them to the game_state for distribution optimization.

        Args:
            game_state: Game state instance with win_data and record() method
        """

        def record_line(
            kind: int, symbol: str, multiplier: int, game_type: str
        ) -> None:
            """Record a single line win to force file.

            Args:
                kind: Number of symbols in the winning line
                symbol: Winning symbol name
                multiplier: Applied multiplier value
                game_type: Game mode (base/bonus)
            """
            game_state.record(
                {
                    "kind": kind,
                    "symbol": symbol,
                    "multiplier": multiplier,
                    "game_type": game_type,
                }
            )

        for win in game_state.win_data["wins"]:
            record_line(
                len(win["positions"]),
                win["symbol"],
                win["meta"]["multiplier"],
                game_state.game_type,
            )
