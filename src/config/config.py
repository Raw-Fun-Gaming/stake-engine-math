"""Standard game configuration with default values.

This module defines the base Config class that all games inherit from.
Game-specific configurations override these defaults in their game_config.py.
"""

from __future__ import annotations

import os
from typing import Any

from src.config.bet_mode import BetMode
from src.config.paths import PATH_TO_GAMES
from src.exceptions import GameConfigError, ReelStripError
from src.formatter import OutputMode


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
        base_game_type: Base game mode name
        free_game_type: Free game mode name
        include_padding: Whether to include top/bottom padding symbols in board display
        output_padding_positions: Whether to output paddingPositions array in reveal events
        free_spin_triggers: Free spin trigger requirements
        bet_modes: List of BetMode configurations
        win_levels: Win level thresholds for different contexts
        reels: Reel strip configurations
        padding_reels: Padding symbol configurations
        output_mode: Output format (COMPACT for smaller files, VERBOSE for readability)
        include_losing_boards: Whether to include board reveals for 0-win spins
        compress_positions: Use array format [reel, row] instead of object format
        simple_symbols: Use string "L5" instead of object {"name": "L5"}
        skip_implicit_events: Skip redundant events that can be inferred
        skip_derived_wins: Skip SET_WIN, SET_TOTAL_WIN (client can sum WIN events)
        skip_progress_updates: Skip UPDATE_FREE_SPINS, UPDATE_TUMBLE_WIN counters
        verbose_event_level: Event verbosity ("full"=all, "standard"=important, "minimal"=required only)
    """

    def __init__(self) -> None:
        """Initialize configuration with default values."""
        # Game identification
        self.rtp: float = 0.97
        self.game_id: str = "template_sample"
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
        self.simple_symbols: bool = True  # Use "L5" instead of {"name": "L5"}
        self.skip_implicit_events: bool = (
            False  # Skip redundant events (e.g., set_final_win with 0)
        )

        # Event filtering options (Phase 3.2: Event Optimization)
        self.skip_derived_wins: bool = (
            False  # Skip SET_WIN, SET_TOTAL_WIN (can sum WIN events)
        )
        self.skip_progress_updates: bool = (
            False  # Skip UPDATE_FREE_SPINS, UPDATE_TUMBLE_WIN
        )
        self.verbose_event_level: str = "full"  # "full", "standard", "minimal"

        if self.game_id != "template_sample":
            self.construct_paths()

        # Win information
        self.min_denomination: float = 0.1
        self.win_cap: float = 5000

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
        self.base_game_type: str = "base_game"
        self.free_game_type: str = "free_game"

        self.include_padding: bool = True
        self.output_padding_positions: bool = (
            True  # Output paddingPositions array in reveal events
        )

        # Define the number of scatter-symbols required to award free-spins
        self.free_spin_triggers: dict[str, dict[int, int]] = {}

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
                9: (100.0, self.win_cap),
                10: (self.win_cap, float("inf")),
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
                9: (2000.0, self.win_cap),
                10: (self.win_cap, float("inf")),
            },
        }

        # Path attributes (set by construct_paths)
        self.reels_path: str = ""
        self.build_path: str = ""
        self.publish_path: str = ""

    def get_win_level(self, win_amount: float, win_level_key: str) -> int:
        """Determine win level tier based on win amount.

        Args:
            win_amount: Win amount multiplier
            win_level_key: Key for win level configuration ("standard", "endFeature", etc.)

        Returns:
            Integer win level (1-10)

        Raises:
            RuntimeError: If win_amount doesn't fall within any level range
        """
        if win_level_key not in self.win_levels:
            raise GameConfigError(
                f"Win level key '{win_level_key}' not found in win_levels configuration. "
                f"Available keys: {list(self.win_levels.keys())}. "
                f"Add this key to self.win_levels in your game_config.py."
            )
        levels = self.win_levels[win_level_key]
        for idx, pair in levels.items():
            if win_amount >= pair[0] and win_amount < pair[1]:
                return idx
        # Show the actual ranges for debugging
        ranges_str = ", ".join(
            [f"Level {k}: [{v[0]}, {v[1]})" for k, v in levels.items()]
        )
        raise GameConfigError(
            f"Win amount {win_amount} does not fall within any win level range for '{win_level_key}'. "
            f"Configured ranges: {ranges_str}. "
            f"Check that win_levels covers all possible win amounts including edge cases."
        )

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
            invalid_symbols = uniqueSymbols - set(self.all_valid_sym_names)
            raise ReelStripError(
                f"Reel strip contains {len(invalid_symbols)} unregistered symbol(s): {sorted(invalid_symbols)}. "
                f"Valid symbols (from paytable + special_symbols): {sorted(self.all_valid_sym_names)}. "
                f"Either add the missing symbols to your paytable/special_symbols in game_config.py, "
                f"or remove them from the reel strip CSV file."
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

                    if len(reelstrips[reelIndex][-1]) == 0:
                        raise ReelStripError(
                            f"Empty symbol found in reel strip at reel {reelIndex}, row {count}. "
                            f"File: {file_path}. "
                            f"Check for empty cells or trailing commas in your CSV file."
                        )
                count += 1

        return reelstrips

    def construct_paths(self) -> None:
        """Construct all output file paths based on game_id.

        Sets up paths for:
        - reels_path: Reel strip configurations
        - build_path: Build output directory (simulation results, configs, etc.)
        - publish_path: Published/final output files
        """
        self.reels_path = os.path.join(PATH_TO_GAMES, self.game_id, "reels")
        self.build_path = os.path.join(PATH_TO_GAMES, self.game_id, "build")
        self.publish_path = os.path.join(
            PATH_TO_GAMES, self.game_id, "build", "publish_files"
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

    def validate_config(self, raise_on_error: bool = True) -> list[str]:
        """Validate configuration for common errors.

        Checks for:
        - Required attributes are set
        - RTP is within valid range (0.0 - 1.0)
        - Paytable is not empty and has valid format
        - Board dimensions are positive integers
        - Win cap is positive
        - Special symbols match paytable
        - Bet modes are configured
        - Reel path exists (if set)

        Args:
            raise_on_error: If True, raise GameConfigError on first error.
                           If False, return list of all error messages.

        Returns:
            List of validation error messages (empty if valid)

        Raises:
            GameConfigError: If raise_on_error=True and validation fails

        Example:
            >>> config = GameConfig()
            >>> config.validate_config()  # Raises if invalid
            >>> errors = config.validate_config(raise_on_error=False)
            >>> if errors:
            ...     print(f"Found {len(errors)} errors")
        """
        errors: list[str] = []

        # Check game identification
        if not self.game_id or self.game_id == "template_sample":
            errors.append(
                "game_id not set. Define a unique game_id in your game_config.py."
            )

        # Check RTP
        if not (0.0 < self.rtp < 1.0):
            errors.append(
                f"RTP {self.rtp} is out of valid range (0.0, 1.0). "
                f"Slot games must have RTP between 0% and 100%."
            )

        # Check win cap
        if self.win_cap <= 0:
            errors.append(f"wincap must be positive, got {self.win_cap}.")

        # Check board dimensions
        if self.num_reels <= 0:
            errors.append(f"num_reels must be positive, got {self.num_reels}.")

        if isinstance(self.num_rows, int):
            if self.num_rows <= 0:
                errors.append(f"num_rows must be positive, got {self.num_rows}.")
        elif isinstance(self.num_rows, list):
            if len(self.num_rows) != self.num_reels:
                errors.append(
                    f"num_rows list length ({len(self.num_rows)}) must match num_reels ({self.num_reels})."
                )
            for i, rows in enumerate(self.num_rows):
                if rows <= 0:
                    errors.append(f"num_rows[{i}] must be positive, got {rows}.")

        # Check paytable
        if not self.paytable:
            errors.append(
                "paytable is empty. Define at least one symbol payout in game_config.py."
            )
        else:
            for key, value in self.paytable.items():
                # Support both standard (count, symbol) and range ((min, max), symbol) formats
                if not isinstance(key, tuple) or len(key) != 2:
                    errors.append(
                        f"Invalid paytable key: {key}. "
                        f"Keys must be tuples of (count, symbol_name) or ((min, max), symbol_name)."
                    )
                elif isinstance(key[0], tuple):
                    # Range format: ((min, max), symbol)
                    if len(key[0]) != 2 or not all(
                        isinstance(x, int) and x > 0 for x in key[0]
                    ):
                        errors.append(
                            f"Invalid range in paytable key {key}. "
                            f"Range must be (min_count, max_count) with positive integers."
                        )
                    if not isinstance(key[1], str):
                        errors.append(
                            f"Invalid symbol in paytable key {key}. "
                            f"Symbol name must be a string."
                        )
                elif not isinstance(key[0], int) or key[0] <= 0:
                    errors.append(
                        f"Invalid count in paytable key {key}. "
                        f"Count must be a positive integer."
                    )
                elif not isinstance(key[1], str):
                    errors.append(
                        f"Invalid symbol in paytable key {key}. "
                        f"Symbol name must be a string."
                    )
                if not isinstance(value, (int, float)) or value < 0:
                    errors.append(
                        f"Invalid payout for {key}: {value}. "
                        f"Payout must be a non-negative number."
                    )

        # Check bet modes
        if not self.bet_modes:
            errors.append(
                "No bet_modes configured. "
                "Define at least one BetMode in game_config.py."
            )

        # Check reels path exists (if set)
        if self.reels_path and not os.path.exists(self.reels_path):
            errors.append(
                f"Reels path does not exist: {self.reels_path}. "
                f"Create the directory and add reel strip CSV files."
            )

        # Check verbose_event_level is valid
        valid_levels = {"full", "standard", "minimal"}
        if self.verbose_event_level not in valid_levels:
            errors.append(
                f"Invalid verbose_event_level: '{self.verbose_event_level}'. "
                f"Must be one of: {valid_levels}."
            )

        # Raise or return errors
        if raise_on_error and errors:
            raise GameConfigError(
                f"Configuration validation failed with {len(errors)} error(s):\n"
                + "\n".join(f"  - {e}" for e in errors)
            )

        return errors
