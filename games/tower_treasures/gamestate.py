"""Game state for tower_treasures - Cluster-pay slot with upgrades and sticky symbols.

Flattened inheritance structure (Phase 1.3):
- Direct inheritance from Board (which inherits from BaseGameState)
- All game-specific logic consolidated in this single file
"""

import random
from typing import Any

from src.calculations.board import Board
from src.calculations.cluster import Cluster
from src.calculations.statistics import get_random_outcome
from src.events.events import (
    prize_win_event,
    trigger_free_spins_event,
    update_free_spins_event,
    upgrade_event,
    win_event,
)

# Import game-specific events
from game_events import reveal_event


class GameState(Board):
    """Handles game logic for cluster-pay slot with symbol upgrades and sticky mechanics.

    This game implements:
    - Cluster-pay mechanics (adjacent matching symbols)
    - No tumbling - symbols stay on board after winning
    - Symbol upgrade system: L symbols upgrade to M or H based on cluster size
    - Sticky symbols: Upgraded M/H symbols persist across free spins
    - Prize payouts: M and H symbols have prize values
    - Free spin mode with persistent upgraded symbols
    """

    # =========================================================================
    # SPECIAL SYMBOL HANDLERS
    # =========================================================================

    def assign_special_sym_function(self) -> None:
        """Define special symbol behaviors.

        M symbols get multiplier attributes with prize values.
        """
        self.special_symbol_functions = {"M": [self.assign_mult_property]}

    def assign_mult_property(self, symbol: Any) -> None:
        """Assign multiplier attribute to multiplier symbol.

        Args:
            symbol: Symbol object to assign multiplier to
        """
        multiplier_value = get_random_outcome(
            self.get_current_distribution_conditions()["mult_values"][self.gametype]
        )
        symbol.assign_attribute({"multiplier": multiplier_value})

    # =========================================================================
    # STATE MANAGEMENT OVERRIDES
    # =========================================================================

    def reset_book(self) -> None:
        """Reset all state variables for a new simulation.

        Extends base reset_book to include tumble win tracking.
        """
        super().reset_book()
        self.tumble_win = 0

    def reset_fs_spin(self) -> None:
        """Reset state for free spin mode.

        Extends base reset to initialize global multiplier and sticky symbols.
        """
        super().reset_fs_spin()
        self.global_multiplier = 1
        # Initialize sticky symbols tracking, but don't overwrite existing ones
        if not hasattr(self, "sticky_symbols"):
            self.initialize_sticky_symbols()

    def check_repeat(self) -> None:
        """Check if simulation should be repeated due to unmet criteria.

        Extends base check to validate win criteria matching.
        """
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

    # =========================================================================
    # STICKY SYMBOL MECHANICS
    # =========================================================================

    def initialize_sticky_symbols(self) -> None:
        """Initialize sticky symbols tracking for free spins."""
        self.sticky_symbols = []  # List of sticky symbol details
        self.existing_sticky_positions = []  # Track positions that have sticky symbols

    def add_sticky_symbol(self, symbol_name: str, position: dict[str, int]) -> None:
        """Add a new sticky symbol to track during free spins.

        Args:
            symbol_name: Name of the symbol to make sticky
            position: Dictionary with 'reel' and 'row' keys
        """
        if not hasattr(self, "sticky_symbols"):
            self.initialize_sticky_symbols()

        reel, row = position["reel"], position["row"]
        pos_tuple = (reel, row)

        # Check if position already has a sticky symbol
        if pos_tuple not in self.existing_sticky_positions:
            sticky_details = {
                "reel": reel,
                "row": row,
                "symbol": symbol_name,
            }
            self.sticky_symbols.append(sticky_details)
            self.existing_sticky_positions.append(pos_tuple)

    def replace_board_with_stickys(self) -> None:
        """Replace board positions with sticky symbols before each free spin reveal."""
        # Ensure sticky symbols are initialized
        if not hasattr(self, "sticky_symbols"):
            self.initialize_sticky_symbols()

        if not self.sticky_symbols:
            return

        for sticky in self.sticky_symbols:
            # Create the sticky symbol on the board
            self.board[sticky["reel"]][sticky["row"]] = self.create_symbol(
                sticky["symbol"]
            )

    def check_for_new_sticky_symbols(self) -> list[dict[str, Any]]:
        """Check the board for new M and H symbols that should become sticky.

        Returns:
            List of new sticky symbol details
        """
        if not hasattr(self, "sticky_symbols"):
            self.initialize_sticky_symbols()

        new_sticky_symbols = []

        for reel, _ in enumerate(self.board):
            for row, _ in enumerate(self.board[reel]):
                symbol_name = self.board[reel][row].symbol
                pos_tuple = (reel, row)

                # Check if this is an M or H symbol that isn't already sticky
                if (
                    symbol_name.startswith("M") or symbol_name.startswith("H")
                ) and pos_tuple not in self.existing_sticky_positions:
                    sticky_details = {
                        "reel": reel,
                        "row": row,
                        "symbol": symbol_name,
                    }
                    new_sticky_symbols.append(sticky_details)
                    self.sticky_symbols.append(sticky_details)
                    self.existing_sticky_positions.append(pos_tuple)

        return new_sticky_symbols

    # =========================================================================
    # UPGRADE MECHANICS
    # =========================================================================

    def generate_upgrade_events(self) -> None:
        """Generate upgrade events for each winning symbol.

        L symbols with clusters of 5+ upgrade to M or H based on cluster size.
        Upgraded symbols become sticky in free spins.
        """
        for win in self.win_data["wins"]:
            symbol = win["symbol"]
            positions = win["positions"]
            cluster_count = len(positions)

            # Only upgrade L symbols with clusters of 5 or more
            if symbol.startswith("L") and cluster_count >= 5:
                # Pick a random position from the winning cluster
                random_position = random.choice(positions)

                # Determine what symbol it was upgraded to
                if hasattr(self.config, "upgrade_config"):
                    upgrade_config = self.config.upgrade_config
                    symbol_map = upgrade_config["symbol_map"]
                    thresholds = upgrade_config["thresholds"]

                    if symbol in symbol_map:
                        if cluster_count >= thresholds["high"]:
                            upgraded_symbol = symbol_map[symbol]["H"]
                        elif cluster_count >= thresholds["medium"]:
                            upgraded_symbol = symbol_map[symbol]["M"]
                        else:
                            continue

                        # Generate upgrade event
                        upgrade_event(self, symbol, random_position, positions)

                        # Place the upgraded symbol on the board immediately
                        self.board[random_position["reel"]][
                            random_position["row"]
                        ] = self.create_symbol(upgraded_symbol)

                        # Add to sticky symbols during free spins
                        if self.gametype == self.config.freegame_type:
                            if not hasattr(self, "sticky_symbols"):
                                self.initialize_sticky_symbols()
                            self.add_sticky_symbol(upgraded_symbol, random_position)

    # =========================================================================
    # WIN EVALUATION
    # =========================================================================

    def get_clusters_update_wins(self) -> None:
        """Find clusters on board and update win manager.

        Simplified cluster evaluation without tumbling - symbols stay on board.
        """
        clusters = Cluster.get_clusters(self.board, "wild")
        return_data = {
            "totalWin": 0,
            "wins": [],
        }

        # Custom cluster evaluation without exploding symbols (no tumbling)
        total_win = 0
        for sym in clusters:
            for cluster in clusters[sym]:
                syms_in_cluster = len(cluster)
                if (syms_in_cluster, sym) in self.config.paytable:
                    sym_win = self.config.paytable[(syms_in_cluster, sym)]
                    symwin_mult = sym_win * self.global_multiplier
                    total_win += symwin_mult
                    json_positions = [{"reel": p[0], "row": p[1]} for p in cluster]

                    return_data["wins"] += [
                        {
                            "symbol": sym,
                            "clusterSize": syms_in_cluster,
                            "win": symwin_mult,
                            "positions": json_positions,
                            "meta": {
                                "globalMult": self.global_multiplier,
                                "winWithoutMult": sym_win,
                            },
                        }
                    ]
                    # No exploding symbols - clusters stay on board

        return_data["totalWin"] = total_win
        self.win_data = return_data

        # Record wins for statistics
        for win in self.win_data["wins"]:
            self.record(
                {
                    "kind": win["clusterSize"],
                    "symbol": win["symbol"],
                    "mult": int(win["meta"]["globalMult"]),
                    "gametype": self.gametype,
                }
            )

        self.win_manager.update_spinwin(self.win_data["totalWin"])

        # Emit win events if there are any wins
        if self.win_data["totalWin"] > 0:
            win_event(self, include_padding_index=False)
            # Generate upgrade events after win events
            self.generate_upgrade_events()

    def generate_prize_win_events(self) -> None:
        """Generate prize payout events for M and H symbols currently on the board."""
        prize_win_event(self)

    # =========================================================================
    # BOARD DRAWING OVERRIDE
    # =========================================================================

    def draw_board(
        self, emit_event: bool = True, trigger_symbol: str = "scatter"
    ) -> None:
        """Override to handle sticky symbols and use custom reveal_event.

        Args:
            emit_event: Whether to emit the reveal event
            trigger_symbol: Symbol that triggers free spins
        """
        # Call parent draw_board but without emitting the event
        super().draw_board(emit_event=False, trigger_symbol=trigger_symbol)

        # Replace board with sticky symbols if we're in free spins
        if self.gametype == self.config.freegame_type:
            self.replace_board_with_stickys()

        # Emit our custom reveal_event if needed
        if emit_event:
            reveal_event(self)

    # =========================================================================
    # FREE SPIN HANDLING
    # =========================================================================

    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        """Update free spin count based on scatter symbols.

        Each scatter symbol awards 2 free spins.

        Args:
            scatter_key: Key for scatter symbol type
        """
        self.tot_fs = self.count_special_symbols(scatter_key) * 2
        if self.gametype == self.config.basegame_type:
            basegame_trigger, freegame_trigger = True, False
        else:
            basegame_trigger, freegame_trigger = False, True
        trigger_free_spins_event(
            self, basegame_trigger=basegame_trigger, freegame_trigger=freegame_trigger
        )

    def update_freespin(self) -> None:
        """Called before a new reveal during freegame.

        Resets global multiplier to 1 for each new free spin.
        """
        self.fs += 1

        # Initialize sticky symbols tracking only on the very first free spin
        if self.fs == 1 and not hasattr(self, "sticky_symbols"):
            self.initialize_sticky_symbols()

        update_free_spins_event(self)
        self.global_multiplier = 1
        self.win_manager.reset_spin_win()
        self.tumblewin_mult = 0
        self.win_data = {}

    # =========================================================================
    # HELPER FUNCTIONS
    # =========================================================================

    def get_board_multipliers(
        self, multiplier_key: str = "multiplier"
    ) -> tuple[float, list[dict[str, Any]]]:
        """Find multiplier from board using winning positions.

        Args:
            multiplier_key: Attribute key to check for multiplier values

        Returns:
            Tuple of (total multiplier, list of multiplier position info)
        """
        board_mult = 0
        mult_info = []
        for reel, _ in enumerate(self.board):
            for row, _ in enumerate(self.board[reel]):
                if self.board[reel][row].check_attribute(multiplier_key):
                    mult_value = self.board[reel][row].get_attribute(multiplier_key)
                    board_mult += mult_value
                    mult_info.append({"reel": reel, "row": row, "value": mult_value})

        return max(1, board_mult), mult_info

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
            # No tumbling - symbols stay on board after winning

            # Generate prize payout events for M and H symbols on the board
            self.generate_prize_win_events()

            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition() and self.check_freespin_entry():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self) -> None:
        """Run the free spin game mode.

        Free spins feature sticky upgraded symbols that persist across spins.
        """
        self.reset_fs_spin()
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board()

            self.get_clusters_update_wins()
            # No tumbling in free spins either - just cluster detection

            # Generate prize payout events for M and H symbols on the board
            self.generate_prize_win_events()

            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

        self.end_freespin()
