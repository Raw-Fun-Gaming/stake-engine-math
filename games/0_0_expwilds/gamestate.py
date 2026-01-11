"""Game state for 0_0_expwilds - Line-pay slot with expanding wilds and superspin prize mode.

Flattened inheritance structure (Phase 1.3):
- Direct inheritance from Board (which inherits from BaseGameState)
- All game-specific logic consolidated in this single file
"""

import random
from copy import deepcopy
from typing import Any

from src.calculations.board import Board
from src.calculations.lines import Lines
from src.calculations.statistics import get_random_outcome
from src.events.events import (
    reveal_event,
    set_total_win_event,
    set_win_event,
    update_free_spins_event,
)

# Import game-specific events
from game_events import (
    new_expanding_wild_event,
    new_sticky_event,
    reveal_prize_event,
    update_expanding_wild_event,
    win_info_prize_event,
)


class GameState(Board):
    """Handles game logic for line-pay slot with expanding wilds and superspin mode.

    This game implements:
    - Line-pay mechanics (traditional paylines)
    - Expanding wild symbols that persist across free spins
    - Wild symbols with multiplier attributes
    - Superspin mode: respin-style prize collection with sticky symbols
    - Prize symbols with random values
    """

    # =========================================================================
    # SPECIAL SYMBOL HANDLERS
    # =========================================================================

    def assign_special_sym_function(self) -> None:
        """Define special symbol behaviors.

        W symbols get multiplier attributes (in free game only)
        P symbols get prize values
        """
        self.special_symbol_functions = {
            "W": [self.assign_mult_property],
            "P": [self.assign_prize_value],
        }

    def assign_mult_property(self, symbol: Any) -> None:
        """Assign multiplier attribute to wild symbol.

        Only assigned in free game mode.

        Args:
            symbol: Symbol object to assign multiplier to
        """
        if self.gametype != self.config.basegame_type:
            multiplier_value = get_random_outcome(
                self.get_current_distribution_conditions()["mult_values"][
                    self.gametype
                ]
            )
            symbol.assign_attribute({"multiplier": multiplier_value})

    def assign_prize_value(self, symbol: Any) -> None:
        """Assign prize value to prize symbol.

        Args:
            symbol: Symbol object to assign prize to
        """
        multiplier_value = get_random_outcome(
            self.get_current_distribution_conditions()["prize_values"]
        )
        symbol.assign_attribute({"prize": multiplier_value})

    # =========================================================================
    # STATE MANAGEMENT OVERRIDES
    # =========================================================================

    def reset_book(self) -> None:
        """Reset all state variables for a new simulation.

        Extends base reset_book to include expanding wild state.
        """
        super().reset_book()
        self.expanding_wilds = []
        self.avaliable_reels = [i for i in range(self.config.num_reels)]

    def reset_superspin(self) -> None:
        """Initialize superspin mode state."""
        self.tot_fs = 3
        self.fs = 0
        self.sticky_symbols = []
        self.existing_sticky_symbols = []

    def check_repeat(self) -> None:
        """Check if simulation should be repeated due to unmet criteria.

        Extends base check with additional validation for:
        - Win criteria matching
        - Free game trigger requirement
        - Non-zero win requirement when criteria != "0"
        """
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

            if self.get_current_distribution_conditions()[
                "force_freegame"
            ] and not (self.triggered_freegame):
                self.repeat = True

            if self.win_manager.running_bet_win == 0.0 and self.criteria != "0":
                self.repeat = True

    # =========================================================================
    # EXPANDING WILD MECHANICS
    # =========================================================================

    def update_with_existing_wilds(self) -> None:
        """Update existing expanding wilds with new multipliers.

        Each free spin, existing expanding wilds get new random multipliers
        and replace the entire reel.
        """
        updated_exp_wild = []
        for expwild in self.expanding_wilds:
            new_mult_on_reveal = get_random_outcome(
                self.get_current_distribution_conditions()["mult_values"][
                    self.gametype
                ]
            )
            expwild["mult"] = new_mult_on_reveal
            updated_exp_wild.append(
                {"reel": expwild["reel"], "row": 0, "mult": new_mult_on_reveal}
            )
            for row, _ in enumerate(self.board[expwild["reel"]]):
                self.board[expwild["reel"]][row] = self.create_symbol("W")
                self.board[expwild["reel"]][row].assign_attribute(
                    {"multiplier": new_mult_on_reveal}
                )

    def assign_new_wilds(self, max_num_new_wilds: int) -> None:
        """Add new expanding wilds to available reels.

        Args:
            max_num_new_wilds: Maximum number of new wilds to add this spin
        """
        self.new_exp_wilds = []
        for _ in range(max_num_new_wilds):
            if len(self.avaliable_reels) > 0:
                chosen_reel = random.choice(self.avaliable_reels)
                chosen_row = random.choice(
                    [i for i in range(self.config.num_rows[chosen_reel])]
                )
                self.avaliable_reels.remove(chosen_reel)

                wr_mult = get_random_outcome(
                    self.get_current_distribution_conditions()["mult_values"][
                        self.gametype
                    ]
                )
                expwild_details = {"reel": chosen_reel, "row": chosen_row, "mult": wr_mult}
                self.board[expwild_details["reel"]][
                    expwild_details["row"]
                ] = self.create_symbol("W")
                self.board[expwild_details["reel"]][expwild_details["row"]].assign_attribute(
                    {"multiplier": wr_mult}
                )
                self.new_exp_wilds.append(expwild_details)

    # =========================================================================
    # SUPERSPIN PRIZE MECHANICS
    # =========================================================================

    def check_for_new_prize(self) -> list[dict[str, Any]]:
        """Check for prizes landing on most recent reveal.

        Returns:
            List of new sticky symbol details
        """
        new_sticky_symbols = []
        for reel, _ in enumerate(self.board):
            for row, _ in enumerate(self.board[reel]):
                if (
                    self.board[reel][row].check_attribute("prize")
                    and (reel, row) not in self.existing_sticky_symbols
                ):
                    sym_details = {
                        "reel": reel,
                        "row": row,
                        "prize": self.board[reel][row].get_attribute("prize"),
                    }
                    new_sticky_symbols.append(sym_details)
                    self.sticky_symbols.append(deepcopy(sym_details))
                    self.existing_sticky_symbols.append(
                        (sym_details["reel"], sym_details["row"])
                    )

        return new_sticky_symbols

    def replace_board_with_stickys(self) -> None:
        """Replace board positions with sticky prize symbols."""
        for sym in self.sticky_symbols:
            self.board[sym["reel"]][sym["row"]] = self.create_symbol("P")
            self.board[sym["reel"]][sym["row"]].assign_attribute(
                {"prize": sym["prize"]}
            )

    def get_final_board_prize(self) -> dict[str, Any]:
        """Calculate total prize value from all prize symbols on board.

        Returns:
            Dictionary with totalWin and winning positions
        """
        total_win = 0.0
        winning_pos = []
        for reel, _ in enumerate(self.board):
            for row, _ in enumerate(self.board[reel]):
                if self.board[reel][row].check_attribute("prize"):
                    prize_value = self.board[reel][row].get_attribute("prize")
                    total_win += prize_value
                    winning_pos.append(
                        {"reel": reel, "row": row, "value": prize_value}
                    )

        return_data = {"totalWin": total_win, "wins": winning_pos}
        return return_data

    # =========================================================================
    # HELPER FUNCTIONS
    # =========================================================================

    def print_prize_values(self) -> None:
        """Terminal display of prize values for superspin mode (debug utility)."""
        for idx, _ in enumerate(self.board):
            row_str = ""
            for idy, _ in enumerate(self.board[idx]):
                if self.board[idx][idy].name == "P":
                    row_str += str(self.board[idx][idy].prize).ljust(4)
                else:
                    row_str += "X".ljust(4)
            print(row_str)
        print("\n")

    # =========================================================================
    # MAIN GAME LOOPS
    # =========================================================================

    def run_spin(self, sim: int) -> None:
        """Run a single simulation (base game or superspin mode).

        Args:
            sim: Simulation ID for this spin
        """
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            if self.betmode == "superspin":
                self.run_superspin()
            else:
                # Regular base game
                self.draw_board(emit_event=True)

                self.win_data = Lines.get_lines(
                    self.board, self.config, global_multiplier=self.global_multiplier
                )
                Lines.record_lines_wins(self)
                self.win_manager.update_spinwin(self.win_data["totalWin"])
                Lines.emit_linewin_events(self)

                self.win_manager.update_gametype_wins(self.gametype)
                if self.check_fs_condition() and self.check_freespin_entry():
                    self.run_freespin_from_base()

                self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self) -> None:
        """Run the free spin game mode with expanding wilds.

        Free spins feature expanding wilds that persist across spins
        and gain new multipliers each spin.
        """
        self.reset_fs_spin()
        self.expanding_wilds = []
        self.avaliable_reels = [i for i in range(self.config.num_reels)]

        while self.fs < self.tot_fs and not self.wincap_triggered:
            self.update_freespin()
            self.draw_board(emit_event=False)

            # Assign new expanding wilds
            wild_on_reveal = get_random_outcome(
                self.get_current_distribution_conditions()["landing_wilds"]
            )
            self.assign_new_wilds(wild_on_reveal)
            self.update_with_existing_wilds()

            # Emit events
            reveal_event(self)
            if len(self.expanding_wilds) > 0:
                update_expanding_wild_event(self)
            if len(self.new_exp_wilds) > 0:
                new_expanding_wild_event(self)

            # Update expanding wilds list
            for wild in self.new_exp_wilds:
                self.expanding_wilds.append(
                    {"reel": wild["reel"], "row": 0, "mult": wild["mult"]}
                )
            self.expanding_wilds = sorted(self.expanding_wilds, key=lambda x: x["reel"])

            # Evaluate wins
            self.win_data = Lines.get_lines(
                self.board, self.config, global_multiplier=self.global_multiplier
            )
            Lines.record_lines_wins(self)
            self.win_manager.update_spinwin(self.win_data["totalWin"])
            Lines.emit_linewin_events(self)
            self.win_manager.update_gametype_wins(self.gametype)

        self.end_freespin()

    def run_superspin(self) -> None:
        """Run superspin mode (respin-style prize collection).

        Superspin mode features:
        - 3 respins that reset when new prizes land
        - Prize symbols stick to the board
        - Final win is sum of all prize values
        """
        self.repeat = False
        self.reset_superspin()

        while self.fs < self.tot_fs:
            self.update_freespin()
            self.create_board_reelstrips()

            # Force/avoid prizes based on criteria
            if self.criteria == "0":
                while len(self.special_syms_on_board["prize"]) > 0:
                    self.create_board_reelstrips()
            elif (
                self.criteria.upper() == "wincap"
                and self.win_manager.running_bet_win < 0.95 * self.config.wincap
                and self.fs <= 1
            ):
                while len(self.special_syms_on_board["prize"]) == 0:
                    self.create_board_reelstrips()

            self.replace_board_with_stickys()
            reveal_prize_event(self)

            # Check for new prizes
            new_sticky_symbols = self.check_for_new_prize()
            if len(new_sticky_symbols) > 0:
                new_sticky_event(self, new_sticky_symbols)
                self.fs = 0  # Reset respins
                update_free_spins_event(self)

        # Calculate final prize win
        prize_win = self.get_final_board_prize()
        self.win_data = prize_win
        if prize_win["totalWin"] > 0:
            self.win_manager.update_spinwin(prize_win["totalWin"])
            self.win_manager.update_gametype_wins(self.gametype)

        if self.win_manager.spin_win > 0:
            win_info_prize_event(self)
            self.evaluate_wincap()
            set_win_event(self)
        set_total_win_event(self)

        self.evaluate_finalwin()
