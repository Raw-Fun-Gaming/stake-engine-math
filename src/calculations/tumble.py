"""Tumble/cascade mechanics for slot games.

This module handles tumble (cascade) mechanics where winning symbols are removed
from the board and new symbols fall down to replace them, potentially creating
additional wins in a single spin.
"""

from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING, Any

from src.calculations.board import Board
from src.events.events import set_total_win_event, set_win_event

if TYPE_CHECKING:
    from src.calculations.symbol import Symbol

# Type aliases
SymbolBoard = list[list["Symbol"]]


class Tumble(Board):
    """Tumble/cascade mechanics for slot games.

    Provides methods for:
    - Removing winning symbols (marked with explode=True)
    - Dropping remaining symbols down
    - Adding new symbols from above to fill gaps
    - Tracking new symbols for each tumble iteration
    - Emitting cumulative tumble win events
    """

    def tumble_board(self) -> None:
        """Remove winning symbols and drop new ones from above.

        Removes all symbols marked with explode=True, shifts remaining symbols
        down, and adds new symbols from the reel strip above. Updates board
        state and tracks new symbols for event generation.

        Raises:
            RuntimeError: If reel length doesn't match expected size after tumble
        """
        self.board_before_tumble = copy(self.board)
        static_board: Any = copy(self.board)
        self.new_symbols_from_tumble: list[list[Symbol]] = [
            [] for _ in range(len(static_board))
        ]

        for reel, _ in enumerate(static_board):
            exploding_symbols: int = 0
            copy_reel: list[Symbol] = static_board[reel]
            exploding_symbols = sum(
                1 for x in static_board[reel] if x.check_attribute("explode")
            )

            for i in range(exploding_symbols):
                reel_pos: int = (self.reel_positions[reel] - 1) % len(
                    self.reelstrip[reel]
                )
                self.reel_positions[reel] = reel_pos
                # Take top symbol if it exists (don't add this to new_symbols_from_tumble)
                if i == 0 and self.config.include_padding:
                    insert_sym: Symbol = self.top_symbols[reel]
                else:
                    nme: str = self.reelstrip[reel][
                        (reel_pos) % len(self.reelstrip[reel])
                    ]
                    insert_sym = self.create_symbol(nme)
                    self.new_symbols_from_tumble[reel].insert(0, insert_sym)
                copy_reel.insert(0, insert_sym)

            copy_reel = [
                sym for sym in copy_reel if not (sym.check_attribute("explode"))
            ]

            if len(copy_reel) != self.config.num_rows[reel]:
                raise RuntimeError(
                    f"new reel length must match expected board size:\n expected: {self.config.num_rows[reel]} \n actual: {len(copy_reel)}"
                )
            static_board[reel] = copy_reel

            if self.config.include_padding and exploding_symbols > 0:
                padding_name: str = str(
                    self.reelstrip[reel][
                        (self.reel_positions[reel] - 1) % len(self.reelstrip[reel])
                    ]
                )
                self.top_symbols[reel] = self.create_symbol(padding_name)
                self.new_symbols_from_tumble[reel].insert(
                    0, self.create_symbol(padding_name)
                )

        self.board = static_board
        self.get_special_symbols_on_board()

    def set_end_tumble_event(self) -> None:
        """Emit win events for cumulative tumble sequence.

        Creates SET_WIN and SET_TOTAL_WIN events based on accumulated wins
        from all tumbles in the current sequence. Only emits SET_WIN if
        there are actual wins.
        """
        if self.win_manager.spin_win > 0:
            set_win_event(self)
        set_total_win_event(self)
