from src.calculations.tumble import Tumble
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
from src.state.state_conditions import Conditions


class Executables(Conditions, Tumble):
    """
    The purpose of this Class is to group together common actions which are likely to be reused between games.
    These can be overridden in the GameExecutables or GameCalculations if game-specific alterations are required.
    Generally Executables functions do not return values.
    """

    def tumble_game_board(self):
        "Remove winning symbols from active board and replace."
        self.tumble_board()
        tumble_board_event(self)

    def emit_tumble_win_events(self) -> None:
        """Transmit win and new board information upon tumble."""
        if self.win_data["totalWin"] > 0:
            win_event(self)
            update_tumble_win_event(self)
            self.evaluate_wincap()

    def evaluate_wincap(self) -> None:
        """Indicate spin functions should stop once wincap is reached."""
        if self.win_manager.running_bet_win >= self.config.win_cap and not (
            self.wincap_triggered
        ):
            self.wincap_triggered = True
            win_cap_event(self)
            return True
        return False

    def check_free_spin_condition(self, scatter_key: str = "scatter") -> bool:
        """Check if there are enough active scatters to trigger free spins."""
        if self.count_special_symbols(scatter_key) >= min(
            self.config.free_spin_triggers[self.game_type].keys()
        ) and not (self.repeat):
            return True
        return False

    def check_free_spin_entry(self, scatter_key: str = "scatter") -> bool:
        """Ensure that bet_mode criteria is expecting free_spin trigger."""
        if self.get_current_distribution_conditions()["force_free_game"] and len(
            self.special_syms_on_board[scatter_key]
        ) >= min(self.config.free_spin_triggers[self.game_type].keys()):
            return True
        self.repeat = True
        return False

    def run_free_spin_from_base(self, scatter_key: str = "scatter") -> None:
        """Trigger the free_spin function and update total free spin amount."""
        self.record(
            {
                "kind": self.count_special_symbols(scatter_key),
                "symbol": scatter_key,
                "game_type": self.game_type,
            }
        )
        self.update_free_spin_amount()
        self.run_free_spin()

    def update_free_spin_amount(self, scatter_key: str = "scatter") -> None:
        """Set initial number of spins for a free game and transmit event."""
        self.total_free_spins = self.config.free_spin_triggers[self.game_type][
            self.count_special_symbols(scatter_key)
        ]
        if self.game_type == self.config.base_game_type:
            base_game_trigger, free_game_trigger = True, False
        else:
            base_game_trigger, free_game_trigger = False, True
        trigger_free_spins_event(
            self,
            base_game_trigger=base_game_trigger,
            free_game_trigger=free_game_trigger,
        )

    def update_free_spin_retrigger_amount(self, scatter_key: str = "scatter") -> None:
        """Update total free_spin amount on retrigger."""
        self.total_free_spins += self.config.free_spin_triggers[self.game_type][
            self.count_special_symbols(scatter_key)
        ]
        trigger_free_spins_event(self, free_game_trigger=True, base_game_trigger=False)

    def update_free_spin(self) -> None:
        """Called before a new reveal during free game."""
        update_free_spins_event(self)
        self.free_spin_count += 1
        self.win_manager.reset_spin_win()
        self.win_data = {}

    def end_free_spin(self) -> None:
        """Transmit total amount awarded during free game."""
        end_free_spins_event(self)

    def evaluate_final_win(self) -> None:
        """Check base and free_spin sums, set payout multiplier."""
        self.update_final_win()
        set_final_win_event(self)

    def update_global_mult(self) -> None:
        """Increment multiplier value and emit corresponding event."""
        self.global_multiplier += 1
        update_global_mult_event(self)
