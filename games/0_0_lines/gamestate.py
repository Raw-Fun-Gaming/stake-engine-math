"""Game state for 0_0_lines - Traditional line-pay slot game.

Flattened inheritance structure (Phase 1.3):
- Direct inheritance from Board (which inherits from BaseGameState)
- All game-specific logic consolidated in this single file
"""

from src.calculations.board import Board
from src.calculations.lines import Lines
from src.calculations.statistics import get_random_outcome


class GameState(Board):
    """Handles game logic and events for a single simulation number/game-round.

    This game implements traditional line-pay mechanics with:
    - 5 reels, 3 rows per reel
    - Defined paylines (from config)
    - Wild symbols with multipliers in free game
    - Free spin triggers on scatter symbols
    """

    # =========================================================================
    # SPECIAL SYMBOL HANDLERS
    # =========================================================================

    def assign_special_sym_function(self) -> None:
        """Define special symbol behaviors.

        Wild symbols ("W") get multiplier attributes in free game mode.
        """
        self.special_symbol_functions = {
            "W": [self.assign_mult_property],
        }

    def assign_mult_property(self, symbol) -> None:
        """Assign multiplier value to Wild symbol in freegame.

        Args:
            symbol: Symbol object to apply multiplier to
        """
        multiplier_value = 1
        if self.gametype == self.config.freegame_type:
            multiplier_value = get_random_outcome(
                self.get_current_distribution_conditions()["mult_values"][self.gametype]
            )
        symbol.assign_attribute({"multiplier": multiplier_value})

    # =========================================================================
    # WIN EVALUATION
    # =========================================================================

    def evaluate_lines_board(self) -> None:
        """Populate win-data, record wins, transmit events."""
        self.win_data = Lines.get_lines(
            self.board, self.config, global_multiplier=self.global_multiplier
        )
        Lines.record_lines_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        Lines.emit_linewin_events(self)

    # =========================================================================
    # GAME LOOP OVERRIDES
    # =========================================================================

    def check_repeat(self) -> None:
        """Check if simulation should be repeated due to unmet criteria.

        Extends base check_repeat with additional validation:
        - Ensures non-zero win when win_criteria is None
        """
        super().check_repeat()
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
                return
            if win_criteria is None and self.final_win == 0:
                self.repeat = True
                return

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
            self.draw_board()

            # Evaluate wins, update wallet, transmit events
            self.evaluate_lines_board()

            self.win_manager.update_gametype_wins(self.gametype)
            if self.check_fs_condition():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self) -> None:
        """Run the free spin game mode.

        Loops through all free spins, evaluating wins and checking for retriggers.
        """
        self.reset_fs_spin()
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board()

            self.evaluate_lines_board()

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

            self.win_manager.update_gametype_wins(self.gametype)

        self.end_freespin()
