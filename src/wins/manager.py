"""Payout wallet manager.

This module manages win tracking at multiple levels:
- Cumulative wins across all simulations
- Per-simulation base game and free game wins
- Per-spin/reveal wins within a simulation
"""

from src.exceptions import SimulationError


class WinManager:
    """Stores all simulation win info at cumulative and individual spin level.

    Tracks win amounts at three levels:
    1. Total cumulative (across all simulations)
    2. Per-simulation (base game vs free game)
    3. Per-spin/reveal (individual actions within a simulation)

    Attributes:
        base_game_mode: Name of the base game mode (e.g., "base")
        free_game_mode: Name of the free game mode (e.g., "bonus")
        total_cumulative_wins: Total wins across all simulations
        cumulative_base_wins: Total base game wins across all simulations
        cumulative_free_wins: Total free game wins across all simulations
        running_bet_win: Current simulation's total win amount
        base_game_wins: Current simulation's base game wins
        free_game_wins: Current simulation's free game wins
        spin_win: Current reveal/spin win amount
        tumble_win: Current tumble win amount
    """

    def __init__(self, base_game_mode: str, free_game_mode: str) -> None:
        """Initialize win manager with game mode names.

        Args:
            base_game_mode: Name of the base game mode (e.g., "base")
            free_game_mode: Name of the free game mode (e.g., "bonus")
        """
        self.base_game_mode: str = base_game_mode
        self.free_game_mode: str = free_game_mode

        # Updates win amounts across all simulations
        self.total_cumulative_wins: float = 0.0
        self.cumulative_base_wins: float = 0.0
        self.cumulative_free_wins: float = 0.0

        # Base-game and free-game wins for a specific simulation
        self.running_bet_win: float = 0.0

        # Controls wins for a specific simulation number
        self.base_game_wins: float = 0.0
        self.free_game_wins: float = 0.0

        # Controls wins for all actions within a 'reveal' event
        self.spin_win: float = 0.0
        self.tumble_win: float = 0.0

    def update_spin_win(self, win_amount: float) -> None:
        """Update win-value associated with a given reveal.

        Adds the win amount to both the current spin win and the running bet win.

        Args:
            win_amount: Amount to add to current spin/reveal win
        """
        self.spin_win += win_amount
        self.running_bet_win += win_amount

    def set_spin_win(self, win_amount: float) -> None:
        """Set the spin win to a specific value instead of updating.

        Useful for end-of-sequence win modification. Replaces the current spin
        win and adjusts the running bet win accordingly.

        Args:
            win_amount: New spin win value to set
        """
        running_diff = win_amount - self.spin_win
        self.spin_win = win_amount
        self.running_bet_win += running_diff

    def reset_spin_win(self) -> None:
        """Reset wins for a given reveal to zero."""
        self.spin_win = 0.0

    def update_game_type_wins(self, game_type: str) -> None:
        """Assign current spin wins to a specific game type.

        Adds the current spin_win to either base_game_wins or free_game_wins
        depending on the game_type.

        Args:
            game_type: Game mode name (should match base_game_mode or free_game_mode)

        Raises:
            RuntimeError: If game_type doesn't match either game mode
        """
        if self.base_game_mode.lower() == game_type.lower():
            self.base_game_wins += self.spin_win
        elif self.free_game_mode.lower() == game_type.lower():
            self.free_game_wins += self.spin_win
        else:
            raise SimulationError(
                f"Invalid game_type '{game_type}'. "
                f"Valid game_types are: '{self.base_game_mode}' (base) or '{self.free_game_mode}' (free). "
                f"Check that your game state's 'game_type' attribute is set correctly."
            )

    def update_end_round_wins(self) -> None:
        """Accumulate total wins for a given betting round.

        Adds the current simulation's base and free game wins to the
        cumulative totals across all simulations.
        """
        self.total_cumulative_wins += self.base_game_wins + self.free_game_wins
        self.cumulative_base_wins += self.base_game_wins
        self.cumulative_free_wins += self.free_game_wins

    def reset_end_round_wins(self) -> None:
        """Reset all wins at end of game round/simulation.

        Clears all per-simulation and per-spin win amounts back to zero,
        ready for the next simulation.
        """
        self.base_game_wins = 0.0
        self.free_game_wins = 0.0

        self.running_bet_win = 0.0
        self.spin_win = 0.0
        self.tumble_win = 0.0
