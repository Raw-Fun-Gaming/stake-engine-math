"""Game state for template - Minimal template for creating new slot games.

Inheritance: Board → GameState
All game-specific logic consolidated in this single file.
"""

from typing import Any

from src.calculations.board import Board
from src.calculations.statistics import get_random_outcome


class GameState(Board):
    """Minimal template for creating new slot games.

    This template provides the basic structure for implementing a new game.
    Add your game-specific logic in the appropriate sections below.
    """

    # =========================================================================
    # SPECIAL SYMBOL HANDLERS
    # =========================================================================

    def assign_special_sym_function(self) -> None:
        """Define special symbol behaviors.

        Example: M and W symbols with multiplier attributes.
        """
        self.special_symbol_functions = {
            "M": [self.assign_multiplier_property],
            "W": [self.assign_multiplier_property],
        }

    def assign_multiplier_property(self, symbol: Any) -> None:
        """Assign multiplier attribute to symbol.

        Args:
            symbol: Symbol object to assign multiplier to
        """
        multiplier_value = get_random_outcome(
            self.get_current_distribution_conditions()["multiplier_values"][
                self.game_type
            ]
        )
        symbol.multiplier = multiplier_value

    # =========================================================================
    # STATE MANAGEMENT OVERRIDES
    # =========================================================================

    def reset_book(self) -> None:
        """Reset all state variables for a new simulation.

        Add game-specific state resets here.
        """
        super().reset_book()
        # Add your game-specific reset logic here

    def check_repeat(self) -> None:
        """Check if simulation should be repeated due to unmet criteria.

        Extends base check to validate win criteria matching.
        """
        if self.repeat is False:
            win_criteria = self.get_current_bet_mode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

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
            self.reset_book()

            # Add your game logic here:
            # 1. Draw board: self.draw_board()
            # 2. Evaluate wins: self.evaluate_lines_board() / get_clusters_update_wins() / etc.
            # 3. Check free spin triggers: if self.check_free_spin_condition() and self.check_free_spin_entry()
            # 4. Update win manager: self.win_manager.update_game_type_wins(self.game_type)

            self.evaluate_final_win()

        self.imprint_wins()

    def run_free_spin(self) -> None:
        """Run the free spin game mode.

        Add your free spin logic here.
        """
        self.reset_free_spin()
        while self.free_spin_count < self.total_free_spins:
            self.update_free_spin()

            # Add your free spin logic here:
            # 1. Draw board
            # 2. Evaluate wins
            # 3. Check for retriggers
            # 4. Update win manager

        self.end_free_spin()
