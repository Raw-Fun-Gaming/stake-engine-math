"""Standard game configuration with default values.

This module defines the base Config class that all games inherit from.
Game-specific configurations override these defaults in their game_config.py.
"""

from __future__ import annotations

import os
from typing import Any

from src.config.betmode import BetMode
from src.config.paths import PATH_TO_GAMES
from src.output.output_formatter import OutputMode


class Config:
    """Base configuration class for slot game simulations.

    Defines default values for game parameters, paytables, special symbols,
    reel configurations, and output settings. Game-specific subclasses
    override these values in games/<game_name>/game_config.py.

    Attributes:
        game_id: Unique game identifier
        game_name: Display name for the game
        provider_name: Game provider identifier
        provider_number: Numeric provider ID
        rtp: Target return to player percentage
        wincap: Maximum win cap multiplier
        min_denomination: Minimum bet denomination
        num_reels: Number of reels on the board
        num_rows: Number of rows per reel (can be int or list[int])
        paytable: Symbol payout table {(count, symbol): multiplier}
        special_symbols: Special symbol configurations
        basegame_type: Base game mode name
        freegame_type: Free game mode name
        include_padding: Whether to include padding symbols in display
        freespin_triggers: Free spin trigger requirements
        bet_modes: List of BetMode configurations
        win_levels: Win level thresholds for different contexts
        reels: Reel strip configurations
        padding_reels: Padding symbol configurations
        output_mode: Output format (COMPACT for smaller files, VERBOSE for readability)
        include_losing_boards: Whether to include board reveals for 0-win spins
        compress_positions: Use array format [reel, row] instead of object format
        compress_symbols: Use string "L5" instead of object {"name": "L5"}
        skip_implicit_events: Skip redundant events that can be inferred
    """

    def __init__(self) -> None:
        """Initialize configuration with default values."""
        # Game identification
        self.rtp: float = 0.97
        self.game_id: str = "0_0_asample"
        self.provider_name: str = "sample_provider"
        self.provider_number: int = 1
        self.game_name: str = "sample_lines"
        self.output_regular_json: bool = (
            True  # if True, outputs .json if compression = False. If False, outputs .jsonl
        )

        # Output formatting options (Phase 3.1: Output Optimization)
        self.output_mode: OutputMode = OutputMode.VERBOSE  # compact or verbose format
        self.include_losing_boards: bool = True  # Include board reveals for 0-win spins
        self.compress_positions: bool = False  # Use [reel, row] instead of {reel, row}
        self.compress_symbols: bool = False  # Use "L5" instead of {"name": "L5"}
        self.skip_implicit_events: bool = False  # Skip redundant events (e.g., setFinalWin with 0)

        if self.game_id != "0_0_sample":
            self.construct_paths()

        # Win information
        self.min_denomination: float = 0.1
        self.wincap: float = 5000

        # Game details
        self.num_reels: int = 5  # TODO: Rename from 'reels' in Phase 2
        self.num_rows: int | list[int] = 3  # TODO: Rename from 'row' in Phase 2
        self.paytable: dict[tuple[int, str], float] = (
            {}
        )  # Symbol information assumes (count, symbol_name) format
        self.special_symbols: dict[Any, list[str]] = {None: []}
        self.special_sybol_names: set[str] | list[str] = (
            set()
        )  # TODO: Fix typo in Phase 2
        self.paying_symbol_names: set[str] | list[str] = set()
        self.all_valid_sym_names: set[str] = set()

        # Define special Symbols properties - list all possible symbol states during game-play
        self.basegame_type: str = "basegame"
        self.freegame_type: str = "freegame"

        self.include_padding: bool = True

        # Define the number of scatter-symbols required to award free-spins
        self.freespin_triggers: dict[str, int] = {}

        # Static game files
        self.reel_location: str = ""
        self.reels: dict[str, list[list[str]]] = {}
        self.padding_reels: dict[str, list[list[str]]] = (
            {}
        )  # symbol configuration displayed before the board reveal

        self.write_event_list: bool = True

        self.bet_modes: list[BetMode] = []
        self.opt_params: dict[Any, Any] = {None: None}

        # Define win-levels for each game-mode, returned during win information events
        self.win_levels: dict[str, dict[int, tuple[float, float]]] = {
            "standard": {
                1: (0, 0.1),
                2: (0.1, 1.0),
                3: (1.0, 2.0),
                4: (2.0, 5.0),
                5: (5.0, 15.0),
                6: (15.0, 30.0),
                7: (30.0, 50.0),
                8: (50.0, 100.0),
                9: (100.0, self.wincap),
                10: (self.wincap, float("inf")),
            },
            "endFeature": {
                1: (0.0, 1.0),
                2: (1.0, 5.0),
                3: (5.0, 10.0),
                4: (10.0, 20.0),
                5: (20.0, 50.0),
                6: (50.0, 100.0),
                7: (100.0, 500.0),
                8: (500.0, 2000.0),
                9: (2000.0, self.wincap),
                10: (self.wincap, float("inf")),
            },
        }

        # Path attributes (set by construct_paths)
        self.reels_path: str = ""
        self.library_path: str = ""
        self.publish_path: str = ""

    def get_win_level(self, win_amount: float, winlevel_key: str) -> int:
        """Determine win level tier based on win amount.

        Args:
            win_amount: Win amount multiplier
            winlevel_key: Key for win level configuration ("standard", "endFeature", etc.)

        Returns:
            Integer win level (1-10)

        Raises:
            RuntimeError: If win_amount doesn't fall within any level range
        """
        levels = self.win_levels[winlevel_key]
        for idx, pair in levels.items():
            if win_amount >= pair[0] and win_amount < pair[1]:
                return idx
        raise RuntimeError(f"winLevel not found: {win_amount}")

    def get_special_symbol_names(self) -> None:
        """Extract all special symbol names from special_symbols dict.

        Updates self.special_sybol_names with a list of all unique special
        symbol names found in the special_symbols configuration.
        """
        self.special_sybol_names = set()
        for key in list(self.special_symbols.keys()):
            for sym in self.special_symbols[key]:
                self.special_sybol_names.add(sym)
        self.special_sybol_names = list(self.special_sybol_names)

    def get_paying_symbols(self) -> None:
        """Extract all paying symbol names from paytable.

        Updates self.paying_symbol_names with a list of all unique symbol
        names that appear in the paytable.

        Raises:
            AssertionError: If symbol name in paytable is not a string
        """
        self.paying_symbol_names = set()
        for tup in self.paytable:
            assert type(tup[1]) == str, "symbol name must be a string"
            self.paying_symbol_names.add(tup[1])
        self.payingSymbolnames: list[str] = list(self.paying_symbol_names)

    def validate_reel_symbols(self, reel_strip: list[list[str]]) -> None:
        """Verify that all symbols on the reel strip are valid.

        Args:
            reel_strip: 2D list of symbol names [reel][position]

        Raises:
            RuntimeError: If reel strip contains symbols not in all_valid_sym_names
        """
        uniqueSymbols: set[str] = set()
        for reel in reel_strip:
            for row in reel:
                uniqueSymbols.add(row)

        isSubset = uniqueSymbols.issubset(set(self.all_valid_sym_names))
        if not isSubset:
            raise RuntimeError(
                f"Symbol identified in reel that does not exist in valid symbol names. \n"
                f"Valid Symbols: {self.all_valid_sym_names}\n"
                f"Detected Symbols: {list(uniqueSymbols)}"
            )

    def read_reels_csv(self, file_path: str) -> list[list[str]]:
        """Read reel strip configuration from CSV file.

        CSV format: Each column represents a reel, each row a position.
        Strips out non-alphanumeric characters from symbol names.

        Args:
            file_path: Path to CSV file containing reel strip data

        Returns:
            2D list of symbol names [reel][position]

        Raises:
            AssertionError: If any symbol is empty after stripping
        """
        reelstrips: list[list[str]] = []
        count = 0
        with open(os.path.abspath(file_path), "r", encoding="UTF-8") as file:
            for line in file:
                split_line = line.strip().split(",")
                for reelIndex in range(len(split_line)):
                    if count == 0:
                        reelstrips.append(
                            [
                                "".join(
                                    [
                                        ch
                                        for ch in split_line[reelIndex]
                                        if ch.strip().isalnum()
                                    ]
                                )
                            ]
                        )
                    else:
                        reelstrips[reelIndex].append(
                            "".join(
                                [
                                    ch
                                    for ch in split_line[reelIndex]
                                    if ch.strip().isalnum() and len(ch) > 0
                                ]
                            )
                        )

                    assert len(reelstrips[reelIndex][-1]) > 0, "Symbol is empty."
                count += 1

        return reelstrips

    def construct_paths(self) -> None:
        """Construct all output file paths based on game_id.

        Sets up paths for:
        - reels_path: Reel strip configurations
        - library_path: Simulation output directory
        - publish_path: Published/final output files
        """
        self.reels_path = os.path.join(PATH_TO_GAMES, self.game_id, "reels")
        self.library_path = os.path.join(PATH_TO_GAMES, self.game_id, "library")
        self.publish_path = os.path.join(
            PATH_TO_GAMES, self.game_id, "library", "publish_files"
        )

    def check_folder_exists(self, folder_path: str) -> None:
        """Check if target folder exists, and create if it does not.

        Args:
            folder_path: Path to folder to check/create
        """
        if not (os.path.exists(folder_path)):
            os.makedirs(folder_path)

    def convert_range_table(
        self, pay_group: dict[tuple[tuple[int, int], str], float]
    ) -> dict[tuple[int, str], float]:
        """Convert range-based paytable to individual count paytable.

        Expands pay_group entries with ranges into individual (count, symbol) entries.
        For example, {((5, 7), 'L1'): 0.5} becomes:
        {(5, 'L1'): 0.5, (6, 'L1'): 0.5, (7, 'L1'): 0.5}

        Args:
            pay_group: Dict mapping ((min_count, max_count), symbol) to payout

        Returns:
            Expanded paytable with individual counts

        Example:
            >>> pay_group = {((5, 5), 'L1'): 0.1, ((6, 8), 'H1'): 0.5}
            >>> config.convert_range_table(pay_group)
            {(5, 'L1'): 0.1, (6, 'H1'): 0.5, (7, 'H1'): 0.5, (8, 'H1'): 0.5}
        """
        paytable: dict[tuple[int, str], float] = {}
        for sym_details, payout in pay_group.items():
            min_connections, max_connections = sym_details[0][0], sym_details[0][1]
            symbol = sym_details[1]
            for i in range(min_connections, max_connections + 1):
                paytable[(i, symbol)] = payout

        return paytable
