"""Game state for 0_0_ways - Standard ways-pay slot game.

Flattened inheritance structure (Phase 1.3):
- Direct inheritance from Board (which inherits from BaseGameState)
- All game-specific logic consolidated in this single file
"""

from typing import Any

from src.calculations.board import Board
from src.calculations.statistics import get_random_outcome
from src.calculations.ways import Ways


class GameState(Board):
    """Handles game logic for ways-pay slot with fixed board size.

    This game implements:
    - Ways-pay mechanics (left-to-right symbol combinations)
    - Wild symbols with multiplier attributes
    - Free spin mode triggered by scatter symbols
    """

    # =========================================================================
    # SPECIAL SYMBOL HANDLERS
    # =========================================================================

    def assign_special_sym_function(self) -> None:
        """Define special symbol behaviors.

        W symbols get assigned random multiplier values from distribution.
        """
        self.special_symbol_functions = {"W": [self.assign_mult_property]}

    def assign_mult_property(self, symbol: Any) -> None:
        """Assign multiplier attribute to wild symbol.

        Args:
            symbol: Symbol object to assign multiplier to
        """
        multiplier_value = get_random_outcome(
            self.get_current_distribution_conditions()["mult_values"]
        )
        symbol.assign_attribute({"multiplier": multiplier_value})

    # =========================================================================
    # STATE MANAGEMENT OVERRIDES
    # =========================================================================

    def reset_book(self) -> None:
        """Reset all state variables for a new simulation.

        Extends base reset_book (no additional state for this game).
        """
        super().reset_book()

    def check_repeat(self) -> None:
        """Check if simulation should be repeated due to unmet criteria.

        Extends base check to validate win criteria matching.
        """
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

    # =========================================================================
    # WIN EVALUATION
    # =========================================================================

    def evaluate_ways_board(self) -> None:
        """Evaluate ways wins and update win manager.

        Calculates all ways wins on the board, records them,
        updates win manager, and emits events.
        """
        self.win_data = Ways.get_ways_data(self.config, self.board)
        if self.win_data["totalWin"] > 0:
            Ways.record_ways_wins(self)
            self.win_manager.update_spinwin(self.win_data["totalWin"])
        Ways.emit_wayswin_events(self)

    # =========================================================================
    # MAIN GAME LOOPS
    # =========================================================================

    def run_spin(self, sim: int) -> None:
        """Run a single base game spin simulation.

        Args:
            sim: Simulation ID for this spin
        """
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            # Reset simulation variables and draw a new board
            self.reset_book()
            self.draw_board(emit_event=True)

            # Evaluate ways wins on base-game board
            self.evaluate_ways_board()

            self.win_manager.update_gametype_wins(self.gametype)

            # Check scatter condition and trigger free spins
            if self.check_fs_condition() and self.check_freespin_entry():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self) -> None:
        """Run the free spin game mode.

        Free spins can retrigger if scatter condition is met again.
        """
        self.reset_fs_spin()
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board(emit_event=True)

            self.evaluate_ways_board()

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

            self.win_manager.update_gametype_wins(self.gametype)

        self.end_freespin()
