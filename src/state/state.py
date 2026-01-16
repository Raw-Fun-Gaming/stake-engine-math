"""Base game state module for slot game simulations.

This module provides the abstract base class for all game implementations,
handling core simulation infrastructure including board management, event
recording, win tracking, and RNG seeding.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from copy import copy
from typing import TYPE_CHECKING, Any, Callable, Optional
from warnings import warn

from src.calculations.symbol import SymbolStorage
from src.config.output_filenames import OutputFiles
from src.state.books import Book
from src.types import Board, Event, SimulationID
from src.wins.win_manager import WinManager
from src.write_data.write_data import (
    make_lookup_pay_split,
    make_lookup_tables,
    print_recorded_wins,
    write_json,
    write_library_events,
)

if TYPE_CHECKING:
    from src.config.bet_mode import BetMode
    from src.config.config import Config
    from src.config.distributions import Distribution


class GeneralGameState(ABC):
    """Base game state for all slot game simulations.

    Provides core infrastructure for:
    - Random board generation from reel strips
    - Event recording and book management
    - Win calculation and tracking
    - Free spin triggering and management
    - RNG seeding for reproducibility

    Games should inherit from this class and implement:
        - run_spin(): Main game logic for a single spin
        - run_free_spin(): Free spin game logic
        - assign_special_sym_function(): Special symbol handlers

    Attributes:
        config: Game configuration instance
        output_files: Output file path manager
        win_manager: Win tracking and aggregation
        library: Dictionary of all simulation results
        recorded_events: Force record tracking
        special_symbol_functions: Symbol-specific handlers
        sim: Current simulation ID
        criteria: Current force criteria
        book: Current simulation book
        board: Current board state
        game_mode: Current game mode (base/free_spin)
        free_spin_count: Current free spin number
        total_free_spins: Total free spins awarded
    """

    def __init__(self, config: Config) -> None:
        """Initialize game state with configuration.

        Args:
            config: Game configuration object with paytable, reels, etc.
        """
        self.config: Config = config
        self.output_files: OutputFiles = OutputFiles(self.config)
        self.win_manager: WinManager = WinManager(
            self.config.base_game_type, self.config.free_game_type
        )
        self.library: dict[int, dict[str, Any]] = {}
        self.recorded_events: dict[tuple[tuple[str, str], ...], dict[str, Any]] = {}
        self.special_symbol_functions: dict[str, list[Callable[[Any], None]]] = {}
        self.temp_wins: list[Any] = []
        self.create_symbol_map()
        self.assign_special_sym_function()
        self.sim: SimulationID = 0
        self.criteria: str = ""
        self.book: Book = Book(self.sim, self.criteria)
        self.repeat: bool = True
        self.win_data: dict[str, Any] = {
            "totalWin": 0,
            "wins": [],
        }
        self.reset_seed()
        self.reset_book()
        self.reset_free_spin()

    def create_symbol_map(self) -> None:
        """Construct all valid symbols from config file (from pay-table and special symbols)."""
        all_symbols_set: set[str] = set()
        for key, _ in self.config.paytable.items():
            all_symbols_set.add(key[1])

        for key in self.config.special_symbols:
            for sym in self.config.special_symbols[key]:
                all_symbols_set.add(sym)

        all_symbols_list: list[str] = list(all_symbols_set)
        self.symbol_storage = SymbolStorage(self.config, all_symbols_list)

    @abstractmethod
    def assign_special_sym_function(self) -> None:
        """Define custom symbol functions in game implementation.

        Games should override this method to register special symbol handlers.
        Each handler is called when that symbol appears on the board.

        Example:
            >>> def assign_special_sym_function(self) -> None:
            ...     self.special_symbol_functions = {
            ...         "M": [self.assign_multiplier_property],
            ...         "W": [self.apply_wild_expansion]
            ...     }
        """
        warn("No special symbol functions are defined")

    def reset_book(self) -> None:
        """Reset all state variables for a new simulation.

        Clears the board, resets win tracking, free spin counts, and
        prepares a new book for event recording.
        """
        self.temp_wins = []
        self.board: Board = [
            [[] for _ in range(self.config.num_rows[x])]  # type: ignore[attr-defined]
            for x in range(self.config.num_reels)  # type: ignore[attr-defined]
        ]
        self.top_symbols = None
        self.bottom_symbols = None
        self.book_id = self.sim + 1
        self.book = Book(self.book_id, self.criteria)
        self.win_data = {
            "totalWin": 0,
            "wins": [],
        }
        self.win_manager.reset_end_round_wins()
        self.global_multiplier = 1.0
        self.final_win = 0.0
        self.tot_fs = 0  # TODO: Rename to total_free_spins
        self.fs = 0  # TODO: Rename to free_spin_count
        self.wincap_triggered = False
        self.triggered_free_game = False
        self.game_type = self.config.base_game_type  # type: ignore[attr-defined]
        self.repeat = False
        self.anticipation = [0] * self.config.num_reels  # type: ignore[attr-defined]

    def reset_seed(self, sim: SimulationID = 0) -> None:
        """Reset RNG seed to simulation number for reproducibility.

        Args:
            sim: Simulation ID to use as seed
        """
        random.seed(sim + 1)
        self.sim = sim

    def reset_free_spin(self) -> None:
        """Reset state for free spin mode.

        Called when transitioning from base game to free spins.
        Sets up free spin tracking and resets spin-specific wins.
        """
        self.triggered_free_game = True
        self.fs = 0
        self.game_type = self.config.free_game_type  # type: ignore[attr-defined]
        self.win_manager.reset_spin_win()

    def get_bet_mode(self, mode_name: str) -> Optional[BetMode]:
        """Get bet_mode by name.

        Args:
            mode_name: Name of the bet_mode (e.g., "base", "bonus")

        Returns:
            BetMode object if found, None otherwise
        """
        for bet_mode in self.config.bet_modes:
            if bet_mode.get_name() == mode_name:
                return bet_mode  # type: ignore[return-value]
        print("\nWarning: bet_mode couldn't be retrieved\n")
        return None

    def get_current_bet_mode(self) -> Optional[BetMode]:
        """Get the currently active bet_mode.

        Returns:
            Current BetMode object if found, None otherwise
        """
        for bet_mode in self.config.bet_modes:
            if bet_mode.get_name() == self.bet_mode:
                return bet_mode  # type: ignore[return-value]
        return None

    def get_current_bet_mode_distributions(self) -> Distribution:
        """Get the current bet_mode's distribution for the active criteria.

        Returns:
            Distribution object matching current criteria

        Raises:
            RuntimeError: If criteria distribution cannot be found
        """
        current_bet_mode = self.get_current_bet_mode()
        if current_bet_mode is None:
            raise RuntimeError("Could not locate current bet_mode.")
        dist = current_bet_mode.get_distributions()  # type: ignore[attr-defined]
        for c in dist:
            if c._criteria == self.criteria:
                return c  # type: ignore[return-value]
        raise RuntimeError("Could not locate criteria distribution.")

    def get_current_distribution_conditions(self) -> dict[str, Any]:
        """Get distribution conditions for the current criteria.

        Returns:
            Dictionary of distribution conditions (force_free game, win_criteria, etc.)

        Raises:
            RuntimeError: If bet_mode conditions cannot be found
        """
        bet_mode = self.get_bet_mode(self.bet_mode)
        if bet_mode is None:
            raise RuntimeError("Could not locate bet_mode")
        for d in bet_mode.get_distributions():  # type: ignore[attr-defined]
            if d._criteria == self.criteria:
                return d._conditions  # type: ignore[return-value]
        raise RuntimeError("Could not locate bet_mode conditions")

    def record(self, description: dict[str, Any]) -> None:
        """Record an event for force distribution tracking.

        Force records are used to track specific event occurrences for
        distribution optimization. Common use cases include free spin triggers,
        special symbol appearances, and rare win conditions.

        Args:
            description: Event description dict, e.g.,
                {"kind": "trigger", "symbol": "scatter", "game_type": "base_game"}

        Example:
            >>> self.record({
            ...     "symbol": "scatter",
            ...     "count": 3,
            ...     "game_type": "base_game"
            ... })
        """
        description_str: dict[str, str] = {}
        for k, v in description.items():
            description_str[str(k)] = str(v)
        self.temp_wins.append(description_str)
        self.temp_wins.append(self.book_id)

    def check_force_keys(self, description: tuple[tuple[str, str], ...]) -> None:
        """Check and append unique force-key parameters to bet_mode.

        Args:
            description: Tuple of key-value pairs representing force keys
        """
        current_bet_mode = self.get_current_bet_mode()
        if current_bet_mode is None:
            return
        current_mode_force_keys = current_bet_mode.get_force_keys()  # type: ignore[attr-defined]
        for keyValue in description:
            if keyValue[0] not in current_mode_force_keys:
                current_bet_mode.add_force_key(keyValue[0])  # type: ignore[attr-defined]

    def combine(self, modes: list[list[BetMode]], bet_mode_name: str) -> None:
        """Combine force record keys across multiple mode configurations.

        Args:
            modes: List of bet_mode configuration lists
            bet_mode_name: Name of the bet_mode to combine keys for
        """
        for modeConfig in modes:
            for bet_mode in modeConfig:
                if bet_mode.get_name() == bet_mode_name:
                    break
            force_keys = bet_mode.get_force_keys()  # type: ignore[attr-defined]
            target_bet_mode = self.get_bet_mode(bet_mode_name)
            if target_bet_mode is None:
                continue
            for key in force_keys:
                target_force_keys = target_bet_mode.get_force_keys()  # type: ignore[attr-defined]
                if key not in target_force_keys:
                    target_bet_mode.add_force_key(key)  # type: ignore[attr-defined]

    def imprint_wins(self) -> None:
        """Record all tracked events to library and update win statistics.

        Processes temporary win records, deduplicates events, and stores
        the completed simulation in the library. Also updates cumulative
        win tracking in the win manager.
        """
        for temp_win_index in range(int(len(self.temp_wins) / 2)):
            description = tuple(sorted(self.temp_wins[2 * temp_win_index].items()))
            book_id = self.temp_wins[2 * temp_win_index + 1]
            if description in self.recorded_events and (
                book_id not in self.recorded_events[description]["bookIds"]
            ):
                self.recorded_events[description]["timesTriggered"] += 1
                self.recorded_events[description]["bookIds"] += [book_id]
            elif description not in self.recorded_events:
                self.check_force_keys(description)
                self.recorded_events[description] = {
                    "timesTriggered": 1,
                    "bookIds": [book_id],
                }
        self.temp_wins = []
        self.library[self.sim + 1] = copy(self.book.to_json())
        self.win_manager.update_end_round_wins()

    def update_final_win(self) -> None:
        """Calculate final wins and verify base + free game totals match.

        Applies win cap if necessary and validates that the sum of base game
        and free game wins equals the total payout.

        Raises:
            AssertionError: If win totals don't match between win_manager and book
        """
        final = round(min(self.win_manager.running_bet_win, self.config.win_cap), 2)
        base_win = round(min(self.win_manager.base_game_wins, self.config.win_cap), 2)
        free_win = round(min(self.win_manager.free_game_wins, self.config.win_cap), 2)

        self.final_win = final
        self.book.payout_multiplier = self.final_win
        self.book.base_game_wins = base_win
        self.book.free_game_wins = free_win

        assert min(
            round(self.win_manager.base_game_wins + self.win_manager.free_game_wins, 2),
            self.config.win_cap,
        ) == round(
            min(self.win_manager.running_bet_win, self.config.win_cap), 2
        ), "Base + Free game payout mismatch!"
        assert min(
            round(self.book.base_game_wins + self.book.free_game_wins, 2),
            self.config.win_cap,
        ) == min(
            round(self.book.payout_multiplier, 2), round(self.config.win_cap, 2)
        ), "Base + Free game payout mismatch!"

    def check_repeat(self) -> None:
        """Check if simulation should be repeated due to unmet criteria.

        Sets repeat flag if:
        - Win criteria is defined but not met
        - force_free_game is true but free game wasn't triggered
        """
        if self.repeat is False:
            win_criteria = self.get_current_bet_mode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

            conditions = self.get_current_distribution_conditions()
            if conditions.get("force_free_game") and not self.triggered_free_game:
                self.repeat = True

    @abstractmethod
    def run_spin(self, sim: SimulationID) -> None:
        """Run a single base game spin simulation.

        Must be implemented by game-specific subclasses. This method should:
        1. Reset seed and state
        2. Draw the board
        3. Calculate wins
        4. Check for free spin triggers
        5. Finalize and record results

        Args:
            sim: Simulation ID for this spin
        """
        print(
            "Base Game is not implemented in this game. "
            "Currently passing when calling runSpin."
        )

    @abstractmethod
    def run_free_spin(self) -> None:
        """Run the free spin game mode.

        Must be implemented by game-specific subclasses. This method should:
        1. Reset free spin state
        2. Loop through all free spins
        3. Handle retriggers if applicable
        4. Update win totals
        """
        print(
            "game_state requires def run_free_spin(), "
            "currently passing when calling run_free_spin"
        )

    def run_sims(
        self,
        bet_mode_copy_list: list[list[BetMode]],
        bet_mode: str,
        sim_to_criteria: dict[int, str],
        total_threads: int,
        total_repeats: int,
        num_sims: int,
        thread_index: int,
        repeat_count: int,
        compress: bool = True,
        write_event_list: bool = True,
    ) -> None:
        """Run a batch of simulations for a specific thread.

        Assigns criteria to each simulation and runs them sequentially.
        Results are stored in temporary files to be combined when all
        threads finish.

        Args:
            bet_mode_copy_list: List to append bet_mode configurations to
            bet_mode: Name of the bet_mode being simulated
            sim_to_criteria: Mapping from simulation ID to force criteria
            total_threads: Total number of parallel threads
            total_repeats: Total number of repeat batches
            num_sims: Number of simulations per thread
            thread_index: Index of this thread (0-based)
            repeat_count: Current repeat iteration
            compress: Whether to compress output files
            write_event_list: Whether to write event library

        Note:
            This method is called in parallel across multiple threads.
            Each thread processes a disjoint set of simulation IDs.
        """
        self.win_manager = WinManager(
            self.config.base_game_type, self.config.free_game_type
        )
        self.bet_mode: str = bet_mode
        self.num_sims: int = num_sims

        # Calculate simulation range for this thread
        start_sim = thread_index * num_sims + (total_threads * num_sims) * repeat_count
        end_sim = (thread_index + 1) * num_sims + (
            total_threads * num_sims
        ) * repeat_count

        for sim in range(start_sim, end_sim):
            self.criteria = sim_to_criteria[sim]
            self.run_spin(sim)

        current_bet_mode = self.get_current_bet_mode()
        if current_bet_mode is None:
            raise RuntimeError(f"Could not find bet_mode: {bet_mode}")
        mode_cost = current_bet_mode.get_cost()

        # Calculate and print RTP statistics
        total_rtp = round(
            self.win_manager.total_cumulative_wins / (num_sims * mode_cost), 3
        )
        base_rtp = round(
            self.win_manager.cumulative_base_wins / (num_sims * mode_cost), 3
        )
        free_rtp = round(
            self.win_manager.cumulative_free_wins / (num_sims * mode_cost), 3
        )

        print(
            f"Thread {thread_index} finished with {total_rtp} RTP. "
            f"[Base Game: {base_rtp}, Free Game: {free_rtp}]",
            flush=True,
        )

        # Write output files
        write_json(
            self,
            self.output_files.get_temp_multi_thread_name(
                bet_mode, thread_index, repeat_count, compress
            ),
        )
        print_recorded_wins(
            self,
            self.output_files.get_temp_force_name(bet_mode, thread_index, repeat_count),
        )
        make_lookup_tables(
            self,
            self.output_files.get_temp_lookup_name(
                bet_mode, thread_index, repeat_count
            ),
        )
        make_lookup_pay_split(
            self,
            self.output_files.get_temp_segmented_name(
                bet_mode, thread_index, repeat_count
            ),
        )

        if write_event_list:
            write_library_events(self, list(self.library.values()), bet_mode)
        bet_mode_copy_list.append(self.config.bet_modes)
