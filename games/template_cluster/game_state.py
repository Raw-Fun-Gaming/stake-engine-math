"""Game state for template_cluster - Cluster-pay slot with tumble mechanics and grid multipliers.

Flattened inheritance structure (Phase 1.3):
- Direct inheritance from Tumble (Board → BaseGameState)
- All game-specific logic consolidated in this single file
"""

from typing import Any

# Import game-specific events
from game_events import update_grid_multiplier_event

from src.calculations.cluster import Cluster
from src.calculations.tumble import Tumble
from src.config.config import Config
from src.events.events import update_free_spins_event
from src.types import Board


class GameState(Tumble):
    """Handles game logic for cluster-pay slot with grid multipliers and tumbles.

    This game implements:
    - Cluster-pay mechanics (adjacent matching symbols)
    - Tumble/cascade mechanics (winning symbols removed and replaced)
    - Grid position multipliers that increase with consecutive wins
    - Free spin mode with persistent grid multipliers
    """

    # =========================================================================
    # SPECIAL SYMBOL HANDLERS
    # =========================================================================

    def assign_special_sym_function(self) -> None:
        """Define special symbol behaviors.

        This game has no special symbol handlers.
        """
        pass

    # =========================================================================
    # STATE MANAGEMENT OVERRIDES
    # =========================================================================

    def reset_book(self) -> None:
        """Reset all state variables for a new simulation.

        Extends base reset_book to include tumble-specific state.
        """
        super().reset_book()
        self.tumble_win = 0

    def reset_free_spin(self) -> None:
        """Reset state for free spin mode.

        Extends base reset to initialize grid multipliers.
        """
        super().reset_free_spin()
        self.reset_grid_multipliers()

    def check_repeat(self) -> None:
        """Check if simulation should be repeated due to unmet criteria.

        Extends base check with additional validation for:
        - Win criteria matching
        - Free game trigger requirement
        - Non-zero win requirement when criteria != "0"
        """
        if self.repeat is False:
            win_criteria = self.get_current_bet_mode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

            if self.get_current_distribution_conditions()["force_free_game"] and not (
                self.triggered_free_game
            ):
                self.repeat = True

            if self.win_manager.running_bet_win == 0 and self.criteria != "0":
                self.repeat = True

    # =========================================================================
    # GRID MULTIPLIER MECHANICS
    # =========================================================================

    def reset_grid_multipliers(self) -> None:
        """Initialize all grid position multipliers to 0."""
        self.position_multipliers = [
            [0 for _ in range(self.config.num_rows[reel])]
            for reel in range(self.config.num_reels)
        ]

    def update_grid_multipliers(self) -> None:
        """Update grid multipliers for winning positions.

        Each position that contributes to a win gets its multiplier increased.
        Positions start at 0, are activated to 1 on first win, then increment
        on subsequent wins up to maximum_board_mult.
        """
        if self.win_data["totalWin"] > 0:
            for win in self.win_data["wins"]:
                for pos in win["positions"]:
                    if self.position_multipliers[pos["reel"]][pos["row"]] == 0:
                        self.position_multipliers[pos["reel"]][pos["row"]] = 1
                    else:
                        self.position_multipliers[pos["reel"]][pos["row"]] += 1
                        self.position_multipliers[pos["reel"]][pos["row"]] = min(
                            self.position_multipliers[pos["reel"]][pos["row"]],
                            self.config.maximum_board_mult,
                        )
            update_grid_multiplier_event(self)

    # =========================================================================
    # WIN EVALUATION
    # =========================================================================

    def evaluate_clusters_with_grid(
        self,
        config: Config,
        board: Board,
        clusters: dict[str, list[list[tuple[int, int]]]],
        pos_mult_grid: list[list[float]],
        global_multiplier: float = 1.0,
        return_data: dict[str, Any] | None = None,
    ) -> tuple[Board, dict[str, Any]]:
        """Evaluate clusters with grid position multipliers.

        Calculates cluster wins while applying position-based multipliers from
        the game grid. Returns the modified board and updated win data.

        Args:
            config: Game configuration with paytable
            board: Current game board
            clusters: Dictionary mapping symbols to their cluster positions
            pos_mult_grid: Grid of position multipliers
            global_multiplier: Global multiplier to apply
            return_data: Existing win data to update (creates new if None)

        Returns:
            Tuple of (modified board, win data dictionary)
        """
        if return_data is None:
            return_data = {"totalWin": 0, "wins": []}

        exploding_symbols = []
        total_win = 0
        for sym in clusters:
            for cluster in clusters[sym]:
                syms_in_cluster = len(cluster)
                if (syms_in_cluster, sym) in config.paytable:
                    board_multiplier = 0
                    for positions in cluster:
                        board_multiplier += pos_mult_grid[positions[0]][positions[1]]
                    board_multiplier = max(board_multiplier, 1)
                    symbol_win = config.paytable[(syms_in_cluster, sym)]
                    symbol_win_multiplier = (
                        symbol_win * board_multiplier * global_multiplier
                    )
                    total_win += symbol_win_multiplier
                    json_positions = [{"reel": p[0], "row": p[1]} for p in cluster]

                    central_pos = Cluster.get_central_cluster_position(json_positions)
                    return_data["wins"] += [
                        {
                            "symbol": sym,
                            "clusterSize": syms_in_cluster,
                            "win": symbol_win_multiplier,
                            "positions": json_positions,
                            "meta": {
                                "globalMult": global_multiplier,
                                "clusterMult": board_multiplier,
                                "winWithoutMult": symbol_win,
                                "overlay": {
                                    "reel": central_pos[0],
                                    "row": central_pos[1],
                                },
                            },
                        }
                    ]

                    for positions in cluster:
                        board[positions[0]][positions[1]].explode = True
                        if {
                            "reel": positions[0],
                            "row": positions[1],
                        } not in exploding_symbols:
                            exploding_symbols.append(
                                {"reel": positions[0], "row": positions[1]}
                            )

        return_data["totalWin"] += total_win

        return board, return_data

    def get_clusters_update_wins(self) -> None:
        """Find clusters on board and update win manager."""
        clusters = Cluster.get_clusters(self.board, "wild")
        return_data = {
            "totalWin": 0,
            "wins": [],
        }
        self.board, self.win_data = self.evaluate_clusters_with_grid(
            config=self.config,
            board=self.board,
            clusters=clusters,
            pos_mult_grid=self.position_multipliers,
            global_multiplier=self.global_multiplier,
            return_data=return_data,
        )

        Cluster.record_cluster_wins(self)
        self.win_manager.update_spin_win(self.win_data["totalWin"])
        self.win_manager.tumble_win = self.win_data["totalWin"]

    # =========================================================================
    # FREE SPIN OVERRIDE
    # =========================================================================

    def update_free_spin(self) -> None:
        """Called before a new reveal during free game.

        Extends base update_free_spin with custom counter increment order.
        """
        self.fs += 1
        update_free_spins_event(self)
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

            self.get_clusters_update_wins()
            self.emit_tumble_win_events()

            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.tumble_game_board()
                self.get_clusters_update_wins()
                self.emit_tumble_win_events()

            self.set_end_tumble_event()
            self.win_manager.update_game_type_wins(self.game_type)

            if self.check_free_spin_condition() and self.check_free_spin_entry():
                self.run_free_spin_from_base()

            self.evaluate_final_win()
            self.check_repeat()

        self.imprint_wins()

    def run_free_spin(self) -> None:
        """Run the free spin game mode.

        Free spins maintain grid multipliers across spins, allowing them to
        accumulate and create larger wins.
        """
        self.reset_free_spin()
        while self.fs < self.tot_fs:
            self.update_free_spin()
            self.draw_board()
            update_grid_multiplier_event(self)

            self.get_clusters_update_wins()
            self.emit_tumble_win_events()
            self.update_grid_multipliers()

            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.tumble_game_board()
                self.get_clusters_update_wins()
                self.emit_tumble_win_events()
                self.update_grid_multipliers()

            self.set_end_tumble_event()
            self.win_manager.update_game_type_wins(self.game_type)

            if self.check_free_spin_condition():
                self.update_free_spin_retrigger_amount()

        self.end_free_spin()
