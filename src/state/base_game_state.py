"""Base game state module for slot game simulations.

This module provides the unified base class for all game implementations,
merging previously separate concerns (GeneralGameState, Conditions, Executables)
into a single cohesive base class.

Phase 1.3 Refactoring: Flattened 6-layer inheritance to 2 layers.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from copy import copy
from typing import TYPE_CHECKING, Any, Callable, Optional
from warnings import warn

from src.calculations.symbol import SymbolStorage
from src.config.output_filenames import OutputFiles
from src.output.output_formatter import OutputFormatter

# Event imports (from Executables)
from src.events.events import (
    end_free_spins_event,
    set_final_win_event,
    trigger_free_spins_event,
    tumble_board_event,
    update_free_spins_event,
    update_global_mult_event,
    update_tumble_win_event,
    win_cap_event,
    win_event,
)
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
    from src.config.betmode import BetMode
    from src.config.config import Config
    from src.config.distributions import Distribution


class BaseGameState(ABC):
    """Unified base class for all slot game simulations.

    This class merges functionality from:
    - GeneralGameState: Core simulation infrastructure
    - Conditions: Game state query methods
    - Executables: Common game actions (freespin, wincap, tumble)

    Provides complete infrastructure for:
    - Random board generation from reel strips
    - Event recording and book management
    - Win calculation and tracking
    - Free spin triggering and management
    - RNG seeding for reproducibility
    - Game state queries
    - Common executable actions

    Games should inherit from this class and implement:
        - run_spin(): Main game logic for a single spin
        - run_freespin(): Free spin game logic
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
        gametype: Current game mode (base/freespin)
        fs: Current free spin number
        tot_fs: Total free spins awarded
    """

    def __init__(self, config: Config) -> None:
        """Initialize game state with configuration.

        Args:
            config: Game configuration object with paytable, reels, etc.
        """
        self.config: Config = config
        self.output_files: OutputFiles = OutputFiles(self.config)
        self.win_manager: WinManager = WinManager(
            self.config.basegame_type, self.config.freegame_type
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
        self.reset_fs_spin()

    # =========================================================================
    # CORE INFRASTRUCTURE (from GeneralGameState)
    # =========================================================================

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
            ...         "M": [self.assign_mult_property],
            ...         "W": [self.apply_wild_expansion]
            ...     }
        """
        warn("No special symbol functions are defined")

    def reset_book(self) -> None:
        """Reset all state variables for a new simulation.

        Clears the board, resets win tracking, free spin counts, and
        prepares a new book for event recording with format versioning.
        """
        self.temp_wins = []
        self.board: Board = [
            [[] for _ in range(self.config.num_rows[x])]  # type: ignore[attr-defined]
            for x in range(self.config.num_reels)  # type: ignore[attr-defined]
        ]
        self.top_symbols = None
        self.bottom_symbols = None
        self.book_id = self.sim + 1

        # Create OutputFormatter from config for format versioning
        formatter = OutputFormatter(
            output_mode=self.config.output_mode,
            include_losing_boards=self.config.include_losing_boards,
            compress_positions=self.config.compress_positions,
            compress_symbols=self.config.compress_symbols,
            skip_implicit_events=self.config.skip_implicit_events,
        )

        self.book = Book(self.book_id, self.criteria, formatter)
        self.win_data = {
            "totalWin": 0,
            "wins": [],
        }
        self.win_manager.reset_end_round_wins()
        self.global_multiplier = 1.0
        self.final_win = 0.0
        self.tot_fs = 0  # TODO: Rename to total_free_spins in Phase 2
        self.fs = 0  # TODO: Rename to free_spin_count in Phase 2
        self.wincap_triggered = False
        self.triggered_freegame = False
        self.gametype = self.config.basegame_type  # type: ignore[attr-defined]
        self.repeat = False
        self.anticipation = [0] * self.config.num_reels  # type: ignore[attr-defined]

    def reset_seed(self, sim: SimulationID = 0) -> None:
        """Reset RNG seed to simulation number for reproducibility.

        Args:
            sim: Simulation ID to use as seed
        """
        random.seed(sim + 1)
        self.sim = sim

    def reset_fs_spin(self) -> None:
        """Reset state for free spin mode.

        Called when transitioning from base game to free spins.
        Sets up free spin tracking and resets spin-specific wins.
        """
        self.triggered_freegame = True
        self.fs = 0
        self.gametype = self.config.freegame_type  # type: ignore[attr-defined]
        self.win_manager.reset_spin_win()

    def get_betmode(self, mode_name: str) -> Optional[BetMode]:
        """Get betmode by name.

        Args:
            mode_name: Name of the betmode (e.g., "base", "bonus")

        Returns:
            BetMode object if found, None otherwise
        """
        for betmode in self.config.bet_modes:
            if betmode.get_name() == mode_name:
                return betmode  # type: ignore[return-value]
        print("\nWarning: betmode couldn't be retrieved\n")
        return None

    def get_current_betmode(self) -> Optional[BetMode]:
        """Get the currently active betmode.

        Returns:
            Current BetMode object if found, None otherwise
        """
        for betmode in self.config.bet_modes:
            if betmode.get_name() == self.betmode:
                return betmode  # type: ignore[return-value]
        return None

    def get_current_betmode_distributions(self) -> Distribution:
        """Get the current betmode's distribution for the active criteria.

        Returns:
            Distribution object matching current criteria

        Raises:
            RuntimeError: If criteria distribution cannot be found
        """
        current_betmode = self.get_current_betmode()
        if current_betmode is None:
            raise RuntimeError("Could not locate current betmode.")
        dist = current_betmode.get_distributions()  # type: ignore[attr-defined]
        for c in dist:
            if c._criteria == self.criteria:
                return c  # type: ignore[return-value]
        raise RuntimeError("Could not locate criteria distribution.")

    def get_current_distribution_conditions(self) -> dict[str, Any]:
        """Get distribution conditions for the current criteria.

        Returns:
            Dictionary of distribution conditions (force_freegame, win_criteria, etc.)

        Raises:
            RuntimeError: If betmode conditions cannot be found
        """
        betmode = self.get_betmode(self.betmode)
        if betmode is None:
            raise RuntimeError("Could not locate betmode")
        for d in betmode.get_distributions():  # type: ignore[attr-defined]
            if d._criteria == self.criteria:
                return d._conditions  # type: ignore[return-value]
        raise RuntimeError("Could not locate betmode conditions")

    def record(self, description: dict[str, Any]) -> None:
        """Record an event for force distribution tracking.

        Force records are used to track specific event occurrences for
        distribution optimization. Common use cases include free spin triggers,
        special symbol appearances, and rare win conditions.

        Args:
            description: Event description dict, e.g.,
                {"kind": "trigger", "symbol": "scatter", "gametype": "basegame"}

        Example:
            >>> self.record({
            ...     "symbol": "scatter",
            ...     "count": 3,
            ...     "gametype": "basegame"
            ... })
        """
        dstr: dict[str, str] = {}
        for k, v in description.items():
            dstr[str(k)] = str(v)
        self.temp_wins.append(dstr)
        self.temp_wins.append(self.book_id)

    def check_force_keys(self, description: tuple[tuple[str, str], ...]) -> None:
        """Check and append unique force-key parameters to betmode.

        Args:
            description: Tuple of key-value pairs representing force keys
        """
        current_betmode = self.get_current_betmode()
        if current_betmode is None:
            return
        current_mode_force_keys = current_betmode.get_force_keys()  # type: ignore[attr-defined]
        for keyValue in description:
            if keyValue[0] not in current_mode_force_keys:
                current_betmode.add_force_key(keyValue[0])  # type: ignore[attr-defined]

    def combine(self, modes: list[list[BetMode]], betmode_name: str) -> None:
        """Combine force record keys across multiple mode configurations.

        Args:
            modes: List of betmode configuration lists
            betmode_name: Name of the betmode to combine keys for
        """
        for modeConfig in modes:
            for betmode in modeConfig:
                if betmode.get_name() == betmode_name:
                    break
            force_keys = betmode.get_force_keys()  # type: ignore[attr-defined]
            target_betmode = self.get_betmode(betmode_name)
            if target_betmode is None:
                continue
            for key in force_keys:
                target_force_keys = target_betmode.get_force_keys()  # type: ignore[attr-defined]
                if key not in target_force_keys:
                    target_betmode.add_force_key(key)  # type: ignore[attr-defined]

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
        final = round(min(self.win_manager.running_bet_win, self.config.wincap), 2)
        basewin = round(min(self.win_manager.basegame_wins, self.config.wincap), 2)
        freewin = round(min(self.win_manager.freegame_wins, self.config.wincap), 2)

        self.final_win = final
        self.book.payout_multiplier = self.final_win
        self.book.basegame_wins = basewin
        self.book.freegame_wins = freewin

        assert min(
            round(self.win_manager.basegame_wins + self.win_manager.freegame_wins, 2),
            self.config.wincap,
        ) == round(
            min(self.win_manager.running_bet_win, self.config.wincap), 2
        ), "Base + Free game payout mismatch!"
        assert min(
            round(self.book.basegame_wins + self.book.freegame_wins, 2),
            self.config.wincap,
        ) == min(
            round(self.book.payout_multiplier, 2), round(self.config.wincap, 2)
        ), "Base + Free game payout mismatch!"

    def check_repeat(self) -> None:
        """Check if simulation should be repeated due to unmet criteria.

        Sets repeat flag if:
        - Win criteria is defined but not met
        - force_freegame is true but free game wasn't triggered
        """
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

            conditions = self.get_current_distribution_conditions()
            if conditions.get("force_freegame") and not self.triggered_freegame:
                self.repeat = True

    # =========================================================================
    # STATE QUERY METHODS (from Conditions)
    # =========================================================================

    def in_criteria(self, *args: str) -> bool:
        """Check if current criteria is within a given list.

        Args:
            *args: Variable number of criteria strings to check against

        Returns:
            True if current criteria matches any of the provided args
        """
        for arg in args:
            if self.criteria == arg:
                return True
        return False

    def in_mode(self, *args: str) -> bool:
        """Check if current bet-mode matches a given list.

        Args:
            *args: Variable number of betmode names to check against

        Returns:
            True if current betmode matches any of the provided args
        """
        for arg in args:
            if self.betmode == arg:
                return True
        return False

    def is_wincap(self) -> bool:
        """Check if current basegame + freegame wins are >= max-win.

        Returns:
            True if wincap has been reached or exceeded
        """
        if self.win_manager.running_bet_win >= self.config.wincap:
            return True
        return False

    def is_in_gametype(self, *args: str) -> bool:
        """Check current gametype against possible list.

        Args:
            *args: Variable number of gametype strings to check against

        Returns:
            True if current gametype matches any of the provided args
        """
        for arg in args:
            if self.gametype == arg:
                return True
        return False

    def get_wincap_triggered(self) -> bool:
        """Check if max-win has been triggered.

        Returns:
            True if wincap flag is set
        """
        if self.wincap_triggered:
            return True
        return False

    # =========================================================================
    # COMMON EXECUTABLE ACTIONS (from Executables)
    # =========================================================================

    def tumble_game_board(self) -> None:
        """Remove winning symbols from active board and replace.

        This method should be overridden by games that use tumble mechanics.
        The default implementation calls tumble_board() from the Tumble class
        if available.
        """
        if hasattr(self, "tumble_board"):
            self.tumble_board()  # type: ignore[attr-defined]
            tumble_board_event(self)
        else:
            raise NotImplementedError(
                "tumble_game_board requires tumble_board method from Tumble class"
            )

    def emit_tumble_win_events(self) -> None:
        """Transmit win and new board information upon tumble."""
        if self.win_data["totalWin"] > 0:
            win_event(self)
            update_tumble_win_event(self)
            self.evaluate_wincap()

    def evaluate_wincap(self) -> bool:
        """Indicate spin functions should stop once wincap is reached.

        Returns:
            True if wincap was triggered, False otherwise
        """
        if self.win_manager.running_bet_win >= self.config.wincap and not (
            self.wincap_triggered
        ):
            self.wincap_triggered = True
            win_cap_event(self)
            return True
        return False

    def check_fs_condition(self, scatter_key: str = "scatter") -> bool:
        """Check if there are enough active scatters to trigger fs.

        Args:
            scatter_key: Key for scatter symbols in special_syms_on_board

        Returns:
            True if free spin trigger condition is met
        """
        if self.count_special_symbols(scatter_key) >= min(
            self.config.freespin_triggers[self.gametype].keys()
        ) and not (self.repeat):
            return True
        return False

    def check_freespin_entry(self, scatter_key: str = "scatter") -> bool:
        """Ensure that betmode criteria is expecting freespin trigger.

        Args:
            scatter_key: Key for scatter symbols in special_syms_on_board

        Returns:
            True if conditions allow free spin entry
        """
        if self.get_current_distribution_conditions()["force_freegame"] and len(
            self.special_syms_on_board[scatter_key]
        ) >= min(self.config.freespin_triggers[self.gametype].keys()):
            return True
        self.repeat = True
        return False

    def run_freespin_from_base(self, scatter_key: str = "scatter") -> None:
        """Trigger the freespin function and update total fs amount.

        Args:
            scatter_key: Key for scatter symbols in special_syms_on_board
        """
        self.record(
            {
                "kind": self.count_special_symbols(scatter_key),
                "symbol": scatter_key,
                "gametype": self.gametype,
            }
        )
        self.update_freespin_amount()
        self.run_freespin()

    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        """Set initial number of spins for a freegame and transmit event.

        Args:
            scatter_key: Key for scatter symbols in special_syms_on_board
        """
        self.tot_fs = self.config.freespin_triggers[self.gametype][
            self.count_special_symbols(scatter_key)
        ]
        if self.gametype == self.config.basegame_type:
            basegame_trigger, freegame_trigger = True, False
        else:
            basegame_trigger, freegame_trigger = False, True
        trigger_free_spins_event(
            self, basegame_trigger=basegame_trigger, freegame_trigger=freegame_trigger
        )

    def update_fs_retrigger_amt(self, scatter_key: str = "scatter") -> None:
        """Update total freespin amount on retrigger.

        Args:
            scatter_key: Key for scatter symbols in special_syms_on_board
        """
        self.tot_fs += self.config.freespin_triggers[self.gametype][
            self.count_special_symbols(scatter_key)
        ]
        trigger_free_spins_event(self, freegame_trigger=True, basegame_trigger=False)

    def update_freespin(self) -> None:
        """Called before a new reveal during freegame."""
        update_free_spins_event(self)
        self.fs += 1
        self.win_manager.reset_spin_win()
        self.win_data = {}

    def end_freespin(self) -> None:
        """Transmit total amount awarded during freegame."""
        end_free_spins_event(self)

    def evaluate_finalwin(self) -> None:
        """Check base and freespin sums, set payout multiplier."""
        self.update_final_win()
        set_final_win_event(self)

    def update_global_mult(self) -> None:
        """Increment multiplier value and emit corresponding event."""
        self.global_multiplier += 1
        update_global_mult_event(self)

    def count_special_symbols(self, special_sym_criteria: str) -> int:
        """Returns integer count of active special symbols on board.

        This method will be properly implemented by Board class.
        Included here as a stub for Executables methods that depend on it.

        Args:
            special_sym_criteria: Special symbol type to count

        Returns:
            Number of special symbols of that type currently on board
        """
        return len(self.special_syms_on_board[special_sym_criteria])

    # =========================================================================
    # ABSTRACT METHODS (must be implemented by games)
    # =========================================================================

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
    def run_freespin(self) -> None:
        """Run the free spin game mode.

        Must be implemented by game-specific subclasses. This method should:
        1. Reset free spin state
        2. Loop through all free spins
        3. Handle retriggers if applicable
        4. Update win totals
        """
        print(
            "gamestate requires def run_freespin(), "
            "currently passing when calling runFreeSpin"
        )

    # =========================================================================
    # SIMULATION RUNNER
    # =========================================================================

    def run_sims(
        self,
        betmode_copy_list: list[list[BetMode]],
        betmode: str,
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
            betmode_copy_list: List to append betmode configurations to
            betmode: Name of the betmode being simulated
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
            self.config.basegame_type, self.config.freegame_type
        )
        self.betmode: str = betmode
        self.num_sims: int = num_sims

        # Calculate simulation range for this thread
        start_sim = thread_index * num_sims + (total_threads * num_sims) * repeat_count
        end_sim = (thread_index + 1) * num_sims + (
            total_threads * num_sims
        ) * repeat_count

        for sim in range(start_sim, end_sim):
            self.criteria = sim_to_criteria[sim]
            self.run_spin(sim)

        current_betmode = self.get_current_betmode()
        if current_betmode is None:
            raise RuntimeError(f"Could not find betmode: {betmode}")
        mode_cost = current_betmode.get_cost()

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
            f"[baseGame: {base_rtp}, freeGame: {free_rtp}]",
            flush=True,
        )

        # Write output files
        write_json(
            self,
            self.output_files.get_temp_multi_thread_name(
                betmode, thread_index, repeat_count, compress
            ),
        )
        print_recorded_wins(
            self,
            self.output_files.get_temp_force_name(betmode, thread_index, repeat_count),
        )
        make_lookup_tables(
            self,
            self.output_files.get_temp_lookup_name(betmode, thread_index, repeat_count),
        )
        make_lookup_pay_split(
            self,
            self.output_files.get_temp_segmented_name(
                betmode, thread_index, repeat_count
            ),
        )

        if write_event_list:
            write_library_events(self, list(self.library.values()), betmode)
        betmode_copy_list.append(self.config.bet_modes)
