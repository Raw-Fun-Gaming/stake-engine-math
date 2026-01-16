"""Board generation for slot games.

This module handles creating game boards from reel strips, including random
board generation, forced symbol placement, special symbol tracking, and
anticipation logic for scatter symbols.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

from src.calculations.statistics import get_random_outcome
from src.events.events import reveal_event
from src.exceptions import BoardGenerationError
from src.state.base_game_state import BaseGameState

if TYPE_CHECKING:
    from src.calculations.symbol import Symbol

# Type aliases for clarity
Position = dict[str, int]
SymbolBoard = list[list["Symbol"]]


class Board(BaseGameState):
    """Board generation and manipulation for slot games.

    Provides methods for:
    - Generating random boards from reel strips
    - Forcing specific symbol placements
    - Tracking special symbols (scatters, wilds, etc.)
    - Managing anticipation logic
    - Board display and debugging
    """

    def create_board_reelstrips(self) -> None:
        """Randomly selects stopping positions from reel strips.

        Generates a random board by selecting random stop positions on each reel,
        creating symbols, and tracking special symbols and anticipation logic.
        """
        if self.config.include_padding:
            top_symbols: list[Symbol] = []
            bottom_symbols: list[Symbol] = []
        self.refresh_special_syms()
        self.reelstrip_id: str = get_random_outcome(
            self.get_current_distribution_conditions()["reel_weights"][self.game_type]
        )
        self.reelstrip = self.config.reels[self.reelstrip_id]
        anticipation: list[int] = [0] * self.config.num_reels
        board: Any = [[]] * self.config.num_reels
        for i in range(self.config.num_reels):
            board[i] = [0] * self.config.num_rows[i]
        reel_positions: list[int] = [
            random.randrange(0, len(self.reelstrip[reel]))
            for reel in range(self.config.num_reels)
        ]
        padding_positions: list[int] = [0] * self.config.num_reels
        first_scatter_reel: int = -1
        for reel in range(self.config.num_reels):
            reel_pos: int = reel_positions[reel]
            if self.config.include_padding:
                top_symbols.append(
                    self.create_symbol(
                        self.reelstrip[reel][(reel_pos - 1) % len(self.reelstrip[reel])]
                    )
                )
                bottom_symbols.append(
                    self.create_symbol(
                        self.reelstrip[reel][
                            (reel_pos + len(board[reel])) % len(self.reelstrip[reel])
                        ]
                    )
                )
            for row in range(self.config.num_rows[reel]):
                sym_id: str = self.reelstrip[reel][
                    (reel_pos + row) % len(self.reelstrip[reel])
                ]
                sym: Symbol = self.create_symbol(sym_id)  # type: ignore[assignment]
                board[reel][row] = sym
                if sym.special:
                    for special_symbol in self.special_syms_on_board:
                        for s in self.config.special_symbols[special_symbol]:
                            if board[reel][row].name == s:
                                self.special_syms_on_board[special_symbol] += [
                                    {"reel": reel, "row": row}
                                ]
                                if (
                                    board[reel][row].check_attribute("scatter")
                                    and len(self.special_syms_on_board[special_symbol])
                                    >= self.config.anticipation_triggers[self.game_type]
                                    and first_scatter_reel == -1
                                ):
                                    first_scatter_reel = reel + 1
            padding_positions[reel] = (
                reel_positions[reel] + len(board[reel]) + 1
            ) % len(self.reelstrip[reel])

        if first_scatter_reel > -1 and first_scatter_reel != self.config.num_reels:
            count: int = 1
            for reel in range(first_scatter_reel, self.config.num_reels):
                anticipation[reel] = count
                count += 1

        for r in range(1, self.config.num_reels):
            if anticipation[r - 1] > anticipation[r]:
                raise BoardGenerationError(
                    f"Invalid anticipation sequence at reel {r}: "
                    f"anticipation values must be non-decreasing left-to-right. "
                    f"Found anticipation[{r-1}]={anticipation[r-1]} > anticipation[{r}]={anticipation[r]}. "
                    f"Full anticipation array: {anticipation}. "
                    f"Check scatter symbol placement and anticipation_triggers configuration."
                )

        self.board = board
        self.get_special_symbols_on_board()
        self.reel_positions = reel_positions
        self.padding_position = padding_positions
        self.anticipation = anticipation
        if self.config.include_padding:
            self.top_symbols = top_symbols
            self.bottom_symbols = bottom_symbols

    def force_board_from_reelstrips(
        self, reelstrip_id: str, force_stop_positions: dict[int, int]
    ) -> None:
        """Creates a game board from specified reel stop positions.

        Args:
            reelstrip_id: ID of the reel strip to use
            force_stop_positions: Dict mapping reel index to forced stop position
        """
        if self.config.include_padding:
            top_symbols: list[Symbol] = []
            bottom_symbols: list[Symbol] = []
        self.refresh_special_syms()
        self.reelstrip_id = reelstrip_id
        self.reelstrip = self.config.reels[self.reelstrip_id]
        anticipation: list[int] = [0] * self.config.num_reels
        board: Any = [[]] * self.config.num_reels
        for i in range(self.config.num_reels):
            board[i] = [0] * self.config.num_rows[i]

        reel_positions: list[int | None] = [None] * self.config.num_reels
        for r, s in force_stop_positions.items():
            reel_positions[r] = s - random.randint(0, self.config.num_rows[r] - 1)
        for r, _ in enumerate(reel_positions):
            if reel_positions[r] is None:
                reel_positions[r] = random.randrange(0, len(self.reelstrip[r]))

        padding_positions: list[int] = [0] * self.config.num_reels
        first_scatter_reel: int = -1
        for reel in range(self.config.num_reels):
            reel_pos: int = reel_positions[reel]  # type: ignore[assignment]
            if self.config.include_padding:
                top_symbols.append(
                    self.create_symbol(
                        self.reelstrip[reel][(reel_pos - 1) % len(self.reelstrip[reel])]
                    )
                )
                bottom_symbols.append(
                    self.create_symbol(
                        self.reelstrip[reel][
                            (reel_pos + len(board[reel])) % len(self.reelstrip[reel])
                        ]
                    )
                )
            for row in range(self.config.num_rows[reel]):
                sym_id: str = self.reelstrip[reel][
                    (reel_pos + row) % len(self.reelstrip[reel])
                ]
                sym: Symbol = self.create_symbol(sym_id)  # type: ignore[assignment]
                board[reel][row] = sym

                if sym.special:
                    for special_symbol in self.special_syms_on_board:
                        for s in self.config.special_symbols[special_symbol]:
                            if board[reel][row].name == s:
                                self.special_syms_on_board[special_symbol] += [
                                    {"reel": reel, "row": row}
                                ]
                                if (
                                    board[reel][row].check_attribute("scatter")
                                    and len(self.special_syms_on_board[special_symbol])
                                    >= self.config.anticipation_triggers[self.game_type]
                                    and first_scatter_reel == -1
                                ):
                                    first_scatter_reel = reel + 1
                padding_positions[reel] = (reel_positions[reel] + len(board[reel]) + 1) % len(self.reelstrip[reel])  # type: ignore[index]

        if first_scatter_reel > -1 and first_scatter_reel <= self.config.num_reels:
            count: int = 1
            for reel in range(first_scatter_reel, self.config.num_reels):
                anticipation[reel] = count
                count += 1

        self.board = board
        self.reel_positions = reel_positions
        self.padding_position = padding_positions
        self.anticipation = anticipation
        if self.config.include_padding:
            self.top_symbols = top_symbols
            self.bottom_symbols = bottom_symbols

    def create_symbol(self, name: str) -> Symbol:
        """Create a new symbol and assign relevant attributes.

        Args:
            name: Symbol name to create

        Returns:
            Symbol object with attributes assigned

        Raises:
            ValueError: If symbol name is not registered in symbol storage
        """
        if name not in self.symbol_storage.symbols:
            registered_symbols = list(self.symbol_storage.symbols.keys())
            raise ValueError(
                f"Symbol '{name}' is not registered in symbol storage. "
                f"Registered symbols: {registered_symbols}. "
                f"Add the symbol to your paytable or special_symbols in game_config.py."
            )
        symObject: Symbol = self.symbol_storage.create_symbol_state(name)
        if name in self.special_symbol_functions:
            for func in self.special_symbol_functions[name]:
                func(symObject)

        return symObject

    def refresh_special_syms(self) -> None:
        """Reset recorded special symbols on board."""
        self.special_syms_on_board = {}
        for s in self.config.special_symbols:
            self.special_syms_on_board[s] = []

    def get_special_symbols_on_board(self) -> None:
        """Scans board for any active special symbols."""
        self.refresh_special_syms()
        for reel, _ in enumerate(self.board):
            for row, _ in enumerate(self.board[reel]):
                if self.board[reel][row].special:
                    for specialType in list(self.special_syms_on_board.keys()):
                        if self.board[reel][row].check_attribute(specialType):
                            self.special_syms_on_board[specialType].append(
                                {"reel": reel, "row": row}
                            )

    def transpose_board_string(self, board_string: list[list[str]]) -> list[list[str]]:
        """Transpose symbol names for player-facing display format.

        Args:
            board_string: 2D list of symbol name strings

        Returns:
            Transposed board (rows become columns, columns become rows)
        """
        return [list(row) for row in zip(*board_string)]

    def print_board(self, board: SymbolBoard) -> list[str]:
        """Prints transposed symbol names to the terminal.

        Args:
            board: 2D list of Symbol objects

        Returns:
            List of string rows (transposed board display)
        """
        string_board: list[str] = []
        max_sum_length: int = max(len(sym.name) for row in board for sym in row) + 1
        board_string: list[list[str]] = [
            [sym.name.ljust(max_sum_length) for sym in reel] for reel in board
        ]
        transpose_board: list[list[str]] = self.transpose_board_string(board_string)
        print("\n")
        for row in transpose_board:
            string_board.append("".join(row))
            print("".join(row))
        print("\n")
        return string_board

    def board_string(self, board: SymbolBoard) -> list[list[str]]:
        """Extract symbol names only from board.

        Args:
            board: 2D list of Symbol objects

        Returns:
            2D list of symbol name strings
        """
        board_str: list[list[str]] = []
        for reel in range(len(board)):
            board_str.append([x.name for x in board[reel]])
        return board_str

    def draw_board(
        self, emit_event: bool = True, trigger_symbol: str = "scatter"
    ) -> None:
        """Draw a board, optionally forcing scatter triggers based on bet_mode.

        If bet_mode specifies force_free game, forces a specific number of scatter
        symbols. Otherwise, draws random boards until no unwanted triggers occur.

        Args:
            emit_event: Whether to emit REVEAL event after drawing (default: True)
            trigger_symbol: Special symbol type to check for triggers (default: "scatter")
        """
        if (
            self.get_current_distribution_conditions()["force_free_game"]
            and self.game_type == self.config.base_game_type
        ):
            num_scatters: int = get_random_outcome(
                self.get_current_distribution_conditions()["scatter_triggers"]
            )
            self.force_special_board(trigger_symbol, num_scatters)
        elif (
            not (self.get_current_distribution_conditions()["force_free_game"])
            and self.game_type == self.config.base_game_type
        ):
            self.create_board_reelstrips()
            while self.count_special_symbols(trigger_symbol) >= min(
                self.config.free_spin_triggers[self.game_type].keys()
            ):
                self.create_board_reelstrips()
        else:
            self.create_board_reelstrips()
        if emit_event:
            reveal_event(self)

    def force_special_board(self, force_criteria: str, num_force_syms: int) -> None:
        """Force a board to have a specified number of symbols.
        Set a specific type of special symbol on a given number of reels.
        This function is mostly used to set the board so that there is a given number
        of scatter symbols.

        Args:
            force_criteria: The type of symbol to force on the board. (e.g. "scatter")
            num_force_syms: The number of symbols to force on the board.

        Note: If it is possible for two target symbols to appear on one reel, this method
        will not be able to guarantee an exact number of target symbols or actually random
        reel positions. I.e. Ensure the reels do not have stacked scatter symbols.
        """
        while True:
            self._force_special_board(force_criteria, num_force_syms)
            if (
                force_criteria in self.config.special_symbols
                and self.count_special_symbols(force_criteria) == num_force_syms
            ):
                break
            elif (
                not (force_criteria in self.config.special_symbols)
                and self.count_symbols_on_board(force_criteria) == num_force_syms
            ):
                break

    def _force_special_board(self, force_criteria: str, num_force_syms: int) -> None:
        """Helper function for forcing special (or name-specific) symbols.

        Args:
            force_criteria: Symbol type or name to force on board
            num_force_syms: Number of symbols to force
        """
        reelstrip_id: str = get_random_outcome(
            self.get_current_distribution_conditions()["reel_weights"][self.game_type]
        )
        reelstops: list[list[int]] = self.get_syms_on_reel(reelstrip_id, force_criteria)

        sym_prob: list[float] = []
        for x in range(self.config.num_reels):
            sym_prob.append(len(reelstops[x]) / len(self.config.reels[reelstrip_id][x]))
        force_stop_positions: dict[int, int] = {}
        while len(force_stop_positions) != num_force_syms:
            possible_reels: list[int] = [
                i for i in range(self.config.num_reels) if sym_prob[i] > 0
            ]
            possible_probs: list[float] = [p for p in sym_prob if p > 0]
            chosen_reel: int = random.choices(possible_reels, possible_probs)[0]
            chosen_stop: int = random.choice(reelstops[chosen_reel])
            sym_prob[chosen_reel] = 0
            force_stop_positions[int(chosen_reel)] = int(chosen_stop)

        force_stop_positions = dict(
            sorted(force_stop_positions.items(), key=lambda x: x[0])
        )
        self.force_board_from_reelstrips(reelstrip_id, force_stop_positions)

    def get_syms_on_reel(self, reel_id: str, target_symbol: str) -> list[list[int]]:
        """Return reel stop positions for a specific symbol name.

        Args:
            reel_id: ID of the reel strip to search
            target_symbol: Symbol name or special symbol type to find

        Returns:
            2D list where each inner list contains stop positions for that reel
        """
        reel = self.config.reels[reel_id]
        reelstop_positions: list[list[int]] = [[] for _ in range(self.config.num_reels)]
        for r in range(self.config.num_reels):
            for s in range(len(reel[r])):
                if (
                    target_symbol in self.config.special_symbols
                    and reel[r][s] in self.config.special_symbols[target_symbol]
                ):
                    reelstop_positions[r].append(s)
                elif reel[r][s] == target_symbol:
                    reelstop_positions[r].append(s)

        return reelstop_positions

    def count_special_symbols(self, special_sym_criteria: str) -> int:
        """Returns integer count of active special symbols on board.

        Args:
            special_sym_criteria: Special symbol type to count (e.g., "scatter", "wild")

        Returns:
            Number of special symbols of that type currently on board
        """
        return len(self.special_syms_on_board[special_sym_criteria])

    def count_symbols_on_board(self, symbol_name: str) -> int:
        """Count number of symbols on the board matching the target name.

        Args:
            symbol_name: Symbol name to count (case-insensitive)

        Returns:
            Total count of matching symbols on board
        """
        symbol_count: int = 0
        for idx, _ in enumerate(self.board):
            for idy, _ in enumerate(self.board[idx]):
                if self.board[idx][idy].name.upper() == symbol_name.upper():
                    symbol_count += 1
        return symbol_count
