"""Game state for template_scatter - Scatter-pay slot with tumble mechanics and multipliers.

Flattened inheritance structure (Phase 1.3):
- Direct inheritance from Tumble (Board → BaseGameState)
- All game-specific logic consolidated in this single file
"""

from copy import copy
from typing import Any

# Import game-specific events
from game_events import send_multiplier_info_event

from src.calculations.scatter import Scatter
from src.calculations.statistics import get_random_outcome
from src.calculations.tumble import Tumble
from src.events.events import (
    set_total_win_event,
    set_win_event,
    trigger_free_spins_event,
    update_free_spins_event,
    update_global_mult_event,
    update_tumble_win_event,
)


class GameState(Tumble):
    """Handles game logic for scatter-pay slot with tumbles and multipliers.

    This game implements:
    - Scatter-pay mechanics (symbols anywhere on board count for wins)
    - Tumble/cascade mechanics (winning symbols removed and replaced)
    - Multiplier symbols with random values
    - Global multiplier that increases with tumbles in free spins
    - Board multipliers applied at end of tumble sequence
    """

    # =========================================================================
    # SPECIAL SYMBOL HANDLERS
    # =========================================================================

    def assign_special_sym_function(self) -> None:
        """Define special symbol behaviors.

        M symbols get assigned random multiplier values from distribution.
        """
        self.special_symbol_functions = {"M": [self.assign_multiplier_property]}

    def assign_multiplier_property(self, symbol: Any) -> None:
        """Assign multiplier attribute to multiplier symbol.

        Args:
            symbol: Symbol object to assign multiplier to
        """
        multiplier_value = get_random_outcome(
            self.get_current_distribution_conditions()["multiplier_values"][
                self.game_type
            ]
        )
        symbol.assign_attribute({"multiplier": multiplier_value})

    # =========================================================================
    # STATE MANAGEMENT OVERRIDES
    # =========================================================================

    def reset_book(self) -> None:
        """Reset all state variables for a new simulation.

        Extends base reset_book to include tumble-specific state.
        """
        super().reset_book()
        self.tumble_win = 0

    def reset_fs_spin(self) -> None:
        """Reset state for free spin mode.

        Extends base reset to initialize global multiplier.
        """
        super().reset_fs_spin()
        self.global_multiplier = 1

    def check_repeat(self) -> None:
        """Check if simulation should be repeated due to unmet criteria.

        Extends base check to validate win criteria matching.
        """
        if self.repeat is False:
            win_criteria = self.get_current_bet_mode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

    # =========================================================================
    # MULTIPLIER CALCULATIONS
    # =========================================================================

    def get_board_multipliers(
        self, multiplier_key: str = "multiplier"
    ) -> tuple[float, list[dict[str, Any]]]:
        """Calculate total board multiplier from multiplier symbols.

        Scans all board positions for symbols with multiplier attributes
        and sums their values.

        Args:
            multiplier_key: Attribute key to check for multiplier values

        Returns:
            Tuple of (total multiplier, list of multiplier position info)
            Multiplier is at minimum 1 (no multiplier means 1x)
        """
        board_multiplier = 0
        multiplier_info = []
        for reel, _ in enumerate(self.board):
            for row, _ in enumerate(self.board[reel]):
                if self.board[reel][row].check_attribute(multiplier_key):
                    multiplier_value = self.board[reel][row].get_attribute(
                        multiplier_key
                    )
                    board_multiplier += multiplier_value
                    multiplier_info.append(
                        {"reel": reel, "row": row, "value": multiplier_value}
                    )

        return max(1, board_multiplier), multiplier_info

    # =========================================================================
    # WIN EVALUATION
    # =========================================================================

    def get_scatterpays_update_wins(self) -> None:
        """Evaluate scatter pays and update win manager.

        Scatter wins are calculated based on symbol counts anywhere on board,
        applied with global multiplier.
        """
        self.win_data = Scatter.get_scatterpay_wins(
            self.config, self.board, global_multiplier=self.global_multiplier
        )
        Scatter.record_scatter_wins(self)
        self.win_manager.tumble_win = self.win_data["totalWin"]
        self.win_manager.update_spin_win(self.win_data["totalWin"])
        self.emit_tumble_win_events()

    def set_end_tumble_event(self) -> None:
        """Handle end of tumble sequence.

        In free spins: Apply board multipliers to tumble win
        Always: Emit win events and update totals
        """
        if self.game_type == self.config.free_game_type:
            board_multiplier, multiplier_info = self.get_board_multipliers()
            base_tumble_win = copy(self.win_manager.spin_win)
            self.win_manager.set_spin_win(base_tumble_win * board_multiplier)

            if self.win_manager.spin_win > 0 and len(multiplier_info) > 0:
                send_multiplier_info_event(
                    self,
                    board_multiplier,
                    multiplier_info,
                    base_tumble_win,
                    self.win_manager.spin_win,
                )
                update_tumble_win_event(self)

        if self.win_manager.spin_win > 0:
            set_win_event(self)
        set_total_win_event(self)

    # =========================================================================
    # FREE SPIN HANDLING
    # =========================================================================

    def update_free_spin_amount(self, scatter_key: str = "scatter") -> None:
        """Update free spin count based on scatter symbols.

        Each scatter symbol awards 2 free spins.

        Args:
            scatter_key: Key for scatter symbol type
        """
        self.tot_fs = self.count_special_symbols(scatter_key) * 2
        if self.game_type == self.config.base_game_type:
            base_game_trigger, free_game_trigger = True, False
        else:
            base_game_trigger, free_game_trigger = False, True
        trigger_free_spins_event(
            self,
            base_game_trigger=base_game_trigger,
            free_game_trigger=free_game_trigger,
        )

    def update_free_spin(self) -> None:
        """Called before a new reveal during free game.

        Resets global multiplier to 1 for each new free spin.
        """
        self.fs += 1
        update_free_spins_event(self)
        self.global_multiplier = 1
        update_global_mult_event(self)
        self.win_manager.reset_spin_win()
        self.tumble_win_multiplier = 0
        self.win_data = {}

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
            self.draw_board()

            self.get_scatterpays_update_wins()
            self.emit_tumble_win_events()

            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.tumble_game_board()
                self.get_scatterpays_update_wins()

            self.set_end_tumble_event()
            self.win_manager.update_game_type_wins(self.game_type)

            if self.check_fs_condition() and self.check_free_spin_entry():
                self.run_free_spin_from_base()

            self.evaluate_final_win()
            self.check_repeat()

        self.imprint_wins()

    def run_free_spin(self) -> None:
        """Run the free spin game mode.

        Free spins have a special mechanic: global multiplier increases
        with each tumble, creating escalating wins.
        """
        self.reset_fs_spin()
        while self.fs < self.tot_fs:
            self.update_free_spin()
            self.draw_board()

            self.get_scatterpays_update_wins()
            self.emit_tumble_win_events()

            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.tumble_game_board()
                self.update_global_mult()  # Increases multiplier with each tumble
                self.get_scatterpays_update_wins()

            self.set_end_tumble_event()
            self.win_manager.update_game_type_wins(self.game_type)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

        self.end_free_spin()
