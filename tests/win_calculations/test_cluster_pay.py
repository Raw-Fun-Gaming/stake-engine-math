"""Test basic cluster-calculation functionality."""

import pytest

from src.calculations.cluster import Cluster
from tests.win_calculations.game_test_config import GameStateTest, create_blank_board


class GameClusterConfig:
    """Testing game functions"""

    def __init__(self):
        self.game_id = "0_test_class"
        self.rtp = 0.9700

        # Game Dimensions
        self.num_reels = 6
        self.num_rows = [6] * self.num_reels
        # Board and Symbol Properties
        t1, t2, t3, t4 = (5, 5), (6, 8), (9, 12), (13, 36)
        pay_group = {
            (t1, "H1"): 5.0,
            (t2, "H1"): 12.5,
            (t3, "H1"): 25.0,
            (t4, "H1"): 60.0,
            (t1, "H2"): 5.0,
            (t2, "H2"): 12.5,
            (t3, "H2"): 25.0,
            (t4, "H2"): 60.0,
        }
        self.paytable = convert_range_table(pay_group)

        self.special_symbols = {
            "wild": ["WM"],
            "scatter": ["S"],
            "multiplier": ["WM"],
            "blank": ["X"],
        }
        self.bet_modes = []
        self.base_game_type = "base_game"
        self.free_game_type = "free_game"


def convert_range_table(pay_group: dict) -> dict:
    paytable = {}
    for sym_details, payout in pay_group.items():
        min_connections, max_connections = sym_details[0][0], sym_details[0][1]
        symbol = sym_details[1]
        for i in range(min_connections, max_connections + 1):
            paytable[(i, symbol)] = payout

    return paytable


def create_test_cluster_game_state():
    """Boilerplate game_state for testing."""
    test_config = GameClusterConfig()
    test_game_state = GameStateTest(test_config)
    test_game_state.create_symbol_map()
    test_game_state.assign_special_sym_function()
    test_game_state.board = create_blank_board(
        test_config.num_reels, test_config.num_rows
    )

    return test_game_state


@pytest.fixture(scope="function")
def game_state():
    return create_test_cluster_game_state()


def test_wild_mult_cluster(game_state):
    for idx, _ in enumerate(game_state.board):
        for idy, _ in enumerate(game_state.board[idx]):
            if idx < 4 and idy < 4:
                game_state.board[idx][idy] = game_state.create_symbol("WM")
            else:
                game_state.board[idx][idy] = game_state.create_symbol("X")
    game_state.board[0][4] = game_state.create_symbol("H1")
    # Expect 10-size wilds with multiplier defaulting to H1 payout

    clusters = Cluster.get_clusters(game_state.board)
    _, win_data, total_win = Cluster.evaluate_clusters(
        config=game_state.config,
        board=game_state.board,
        clusters=clusters,
    )
    assert total_win == (
        game_state.config.paytable[(17, "H1")]
        * sum([3 for _ in range(len(win_data["wins"][0]["positions"]) - 1)])
    )


def test_basic_cluster(game_state):
    for idx, _ in enumerate(game_state.board):
        for idy, _ in enumerate(game_state.board[idx]):
            # 3x3 grid of same symbol
            if idx < 3 and idy < 3:
                game_state.board[idx][idy] = game_state.create_symbol("H1")
            else:
                game_state.board[idx][idy] = game_state.create_symbol("X")

    clusters = Cluster.get_clusters(game_state.board)
    _, _, total_win = Cluster.evaluate_clusters(
        config=game_state.config,
        board=game_state.board,
        clusters=clusters,
    )
    assert total_win == game_state.config.paytable[(9, "H1")]
