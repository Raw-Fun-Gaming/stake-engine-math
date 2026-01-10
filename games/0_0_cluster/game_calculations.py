from typing import Any

from src.calculations.cluster import Cluster
from src.config.config import Config
from src.executables.executables import Executables
from src.types import Board


class GameCalculations(Executables):
    """Override cluster evaluation to account for grid position multipliers.

    This class customizes the cluster evaluation logic to include position-based
    multipliers on the game grid.
    """

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
                    board_mult = 0
                    for positions in cluster:
                        board_mult += pos_mult_grid[positions[0]][positions[1]]
                    board_mult = max(board_mult, 1)
                    sym_win = config.paytable[(syms_in_cluster, sym)]
                    symwin_mult = sym_win * board_mult * global_multiplier
                    total_win += symwin_mult
                    json_positions = [{"reel": p[0], "row": p[1]} for p in cluster]

                    central_pos = Cluster.get_central_cluster_position(json_positions)
                    return_data["wins"] += [
                        {
                            "symbol": sym,
                            "clusterSize": syms_in_cluster,
                            "win": symwin_mult,
                            "positions": json_positions,
                            "meta": {
                                "globalMult": global_multiplier,
                                "clusterMult": board_mult,
                                "winWithoutMult": sym_win,
                                "overlay": {"reel": central_pos[0], "row": central_pos[1]},
                            },
                        }
                    ]

                    for positions in cluster:
                        board[positions[0]][positions[1]].explode = True
                        if {
                            "reel": positions[0],
                            "row": positions[1],
                        } not in exploding_symbols:
                            exploding_symbols.append({"reel": positions[0], "row": positions[1]})

        return_data["totalWin"] += total_win

        return board, return_data
