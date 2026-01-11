"""Cluster-pay calculation for slot games.

This module handles detection and evaluation of symbol clusters (adjacent
matching symbols) for cluster-pay games. Includes neighbor checking,
recursive cluster building, and win calculation with multipliers.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.calculations.symbol import Symbol
    from src.config.config import Config

# Type aliases for clarity
Position = tuple[int, int]
Board = list[list["Symbol"]]
ClusterPositions = list[Position]
Clusters = dict[str, list[ClusterPositions]]


class Cluster:
    """Collection of cluster-evaluation functions.

    Provides static methods for:
    - Finding adjacent matching symbols (clusters)
    - Calculating cluster payouts with multipliers
    - Marking symbols for explosion/cascade
    - Recording wins for optimization tracking
    """

    @staticmethod
    def get_central_cluster_position(
        winning_positions: list[dict[str, int]]
    ) -> Position:
        """Return central position of cluster for overlay display.

        Calculates the average position (reel, row) of all symbols in the cluster.
        Used to determine where to display the win amount on screen.

        Args:
            winning_positions: List of position dicts with "reel" and "row" keys

        Returns:
            Tuple (reel, row) representing the center of the cluster
        """
        all_reels = []
        all_rows = []
        for pos in winning_positions:
            all_reels.append(pos["reel"])
            all_rows.append(pos["row"])

        reel_to_overlay = int(round(sum(all_reels) / len(all_rows)))
        row_to_overlay = int(round(sum(all_rows) / len(all_rows)))

        return (reel_to_overlay, row_to_overlay)

    @staticmethod
    def get_neighbours(
        board: Board, reel: int, row: int, local_checked: list[Position]
    ) -> list[Position]:
        """Get all orthogonally adjacent positions within board boundaries.

        Checks up/down/left/right neighbors (not diagonals) and only returns
        positions that haven't been checked yet.

        Args:
            board: 2D list of Symbol objects [reel][row]
            reel: Current reel index (x-coordinate)
            row: Current row index (y-coordinate)
            local_checked: List of already-checked positions to avoid duplicates

        Returns:
            List of unchecked neighbor positions as (reel, row) tuples
        """
        neighbours = []
        if reel > 0:
            if (reel - 1, row) not in local_checked:
                neighbours += [(reel - 1, row)]
                local_checked += [(reel - 1, row)]
        if reel < len(board) - 1:
            if (reel + 1, row) not in local_checked:
                neighbours += [(reel + 1, row)]
                local_checked += [(reel + 1, row)]
        if row > 0:
            if (reel, row - 1) not in local_checked:
                neighbours += [(reel, row - 1)]
                local_checked += [(reel, row - 1)]
        if row < len(board[reel]) - 1:
            if (reel, row + 1) not in local_checked:
                neighbours += [(reel, row + 1)]
                local_checked += [(reel, row + 1)]
        return neighbours

    @staticmethod
    def in_cluster(
        board: Board, reel: int, row: int, og_symbol: str, wild_key: str = "wild"
    ) -> bool:
        """Check if symbol at position matches cluster type (including wilds).

        Args:
            board: 2D list of Symbol objects [reel][row]
            reel: Reel index to check
            row: Row index to check
            og_symbol: Original symbol name defining the cluster
            wild_key: Attribute name for wild symbols (default: "wild")

        Returns:
            True if symbol matches cluster or is wild, False otherwise
        """
        if (
            board[reel][row].check_attribute(wild_key)
            or og_symbol == board[reel][row].name
        ):
            return True
        return False

    @staticmethod
    def check_all_neighbours(
        board: Board,
        already_checked: list[Position],
        local_checked: list[Position],
        potential_cluster: ClusterPositions,
        reel: int,
        row: int,
        og_symbol: str,
        wild_key: str = "wild",
    ) -> None:
        """Recursively find all adjacent matching symbols (flood fill).

        Performs depth-first search to build a complete cluster starting from
        a position. Modifies already_checked, local_checked, and potential_cluster
        in place.

        Args:
            board: 2D list of Symbol objects [reel][row]
            already_checked: Global list of checked positions (across all clusters)
            local_checked: Local list of checked positions (within this cluster)
            potential_cluster: Growing list of positions in this cluster
            reel: Current reel index
            row: Current row index
            og_symbol: Original symbol name defining the cluster
            wild_key: Attribute name for wild symbols (default: "wild")
        """
        neighbours = Cluster.get_neighbours(board, reel, row, local_checked)
        for reel_, row_ in neighbours:
            if Cluster.in_cluster(board, reel_, row_, og_symbol, wild_key):
                potential_cluster += [(reel_, row_)]
                already_checked += [(reel_, row_)]
                Cluster.check_all_neighbours(
                    board,
                    already_checked,
                    local_checked,
                    potential_cluster,
                    reel_,
                    row_,
                    og_symbol,
                    wild_key,
                )

    @staticmethod
    def get_clusters(board: Board, wild_key: str = "wild") -> Clusters:
        """Find all symbol clusters on the board.

        Scans the entire board to identify groups of adjacent matching symbols.
        Wilds are not treated as cluster initiators but can join existing clusters.

        Args:
            board: 2D list of Symbol objects [reel][row]
            wild_key: Attribute name for wild symbols (default: "wild")

        Returns:
            Dict mapping symbol names to lists of clusters, where each cluster
            is a list of (reel, row) positions. Example:
            {"H1": [[(0,0), (0,1), (1,0)], [(3,2), (4,2)]], "L2": [[(2,1)]]}
        """
        already_checked = []
        clusters = defaultdict(list)
        for reel, _ in enumerate(board):
            for row, _ in enumerate(board[reel]):
                if (reel, row) not in already_checked and not (
                    board[reel][row].check_attribute(wild_key)
                ):
                    potential_cluster = [(reel, row)]
                    already_checked += [(reel, row)]
                    local_checked = [(reel, row)]
                    symbol = board[reel][row].name
                    Cluster.check_all_neighbours(
                        board,
                        already_checked,
                        local_checked,
                        potential_cluster,
                        reel,
                        row,
                        symbol,
                        wild_key,
                    )
                    clusters[symbol].append(potential_cluster)

        return clusters

    @staticmethod
    def evaluate_clusters(
        config: Config,
        board: Board,
        clusters: Clusters,
        global_multiplier: int = 1,
        multiplier_key: str = "multiplier",
        return_data: dict[str, Any] | None = None,
    ) -> tuple[Board, dict[str, Any], float]:
        """Calculate win amounts for all clusters and mark symbols for explosion.

        Evaluates each cluster against the paytable, applies symbol multipliers
        and global multipliers, and marks winning symbols with explode=True
        for cascade mechanics.

        Args:
            config: Game configuration with paytable
            board: 2D list of Symbol objects [reel][row]
            clusters: Dict of symbol clusters from get_clusters()
            global_multiplier: Global win multiplier (default: 1)
            multiplier_key: Attribute name for symbol multipliers (default: "multiplier")
            return_data: Optional dict to accumulate win data

        Returns:
            Tuple of (modified_board, win_data_dict, total_win_amount)
            win_data_dict contains:
                - "totalWin": Total win amount
                - "wins": List of individual cluster wins with metadata
        """
        if return_data is None:
            return_data = {"totalWin": 0, "wins": []}
        exploding_symbols: list[dict[str, int]] = []
        total_win: float = 0.0
        for sym in clusters:
            for cluster in clusters[sym]:
                syms_in_cluster = len(cluster)
                if (syms_in_cluster, sym) in config.paytable:
                    cluster_mult: int = 0
                    for positions in cluster:
                        if board[positions[0]][positions[1]].check_attribute(
                            multiplier_key
                        ):
                            if (
                                int(
                                    board[positions[0]][positions[1]].get_attribute(
                                        multiplier_key
                                    )
                                )
                                > 0
                            ):
                                cluster_mult += board[positions[0]][
                                    positions[1]
                                ].get_attribute(multiplier_key)
                    cluster_mult = max(cluster_mult, 1)
                    sym_win: float = config.paytable[(syms_in_cluster, sym)]
                    symwin_mult: float = sym_win * cluster_mult * global_multiplier
                    total_win += symwin_mult
                    json_positions: list[dict[str, int]] = [
                        {"reel": p[0], "row": p[1]} for p in cluster
                    ]

                    central_pos: Position = Cluster.get_central_cluster_position(
                        json_positions
                    )
                    return_data["wins"] += [
                        {
                            "symbol": sym,
                            "clusterSize": syms_in_cluster,
                            "win": symwin_mult,
                            "positions": json_positions,
                            "meta": {
                                "globalMult": global_multiplier,
                                "clusterMult": cluster_mult,
                                "winWithoutMult": sym_win,
                                "overlay": {
                                    "reel": central_pos[0],
                                    "row": central_pos[1],
                                },
                            },
                        }
                    ]

                    for positions in cluster:
                        board[positions[0]][positions[1]].explode = True  # type: ignore[attr-defined]
                        if {
                            "reel": positions[0],
                            "row": positions[1],
                        } not in exploding_symbols:
                            exploding_symbols.append(
                                {"reel": positions[0], "row": positions[1]}
                            )

        return board, return_data, total_win

    @staticmethod
    def get_cluster_data(
        config: Config,
        board: Board,
        global_multiplier: int,
        multiplier_key: str = "multiplier",
        wild_key: str = "wild",
    ) -> dict[str, Any]:
        """Calculate and return all cluster wins in event-ready format.

        Convenience method that combines get_clusters() and evaluate_clusters()
        to provide complete win information.

        Args:
            config: Game configuration with paytable
            board: 2D list of Symbol objects [reel][row]
            global_multiplier: Global win multiplier
            multiplier_key: Attribute name for symbol multipliers (default: "multiplier")
            wild_key: Attribute name for wild symbols (default: "wild")

        Returns:
            Dict with "totalWin" (float) and "wins" (list of cluster win dicts)
        """
        clusters: Clusters = Cluster.get_clusters(board, wild_key)
        return_data: dict[str, Any] = {
            "totalWin": 0.0,
            "wins": [],
        }
        board, return_data, total_win = Cluster.evaluate_clusters(
            config,
            board,
            clusters,
            global_multiplier=global_multiplier,
            multiplier_key=multiplier_key,
            return_data=return_data,
        )

        return_data["totalWin"] += total_win

        return return_data

    @staticmethod
    def record_cluster_wins(gamestate: Any) -> None:
        """Record cluster wins to force tracking system for optimization.

        Extracts win description keys (cluster size, symbol, multiplier, gametype)
        and records them to the gamestate for distribution optimization.

        Args:
            gamestate: Game state instance with win_data and record() method
        """
        for win in gamestate.win_data["wins"]:
            gamestate.record(
                {
                    "kind": win["clusterSize"],
                    "symbol": win["symbol"],
                    "mult": int(win["meta"]["globalMult"] + win["meta"]["clusterMult"]),
                    "gametype": gamestate.gametype,
                }
            )
