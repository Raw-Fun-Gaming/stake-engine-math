"""Test basic ways-calculation functionality."""

import pytest

from src.calculations.ways import Ways
from tests.win_calculations.game_test_config import GameStateTest, create_blank_board


class GameWaysConfig:
    """Testing game functions"""

    def __init__(self):
        self.game_id = "0_test_class"
        self.rtp = 0.9700

        # Game Dimensions
        self.num_reels = 5
        self.num_rows = [3] * self.num_reels
        # Board and Symbol Properties
        self.paytable = {
            (5, "H1"): 70,
            (4, "H1"): 60,
            (3, "H1"): 50,
            (5, "H2"): 30,
            (4, "H2"): 20,
            (3, "H2"): 10,
        }

        self.special_symbols = {"wild": ["W"], "scatter": ["S"], "blank": ["X"]}
        self.bet_modes = []
        self.base_game_type = "base_game"
        self.free_game_type = "free_game"


def create_test_lines_game_state():
    """Boilerplate game_state for testing."""
    test_config = GameWaysConfig()
    test_game_state = GameStateTest(test_config)
    test_game_state.create_symbol_map()
    test_game_state.assign_special_sym_function()
    test_game_state.board = create_blank_board(
        test_config.num_reels, test_config.num_rows
    )

    return test_game_state


@pytest.fixture
def game_state():
    """Initialise test state."""
    return create_test_lines_game_state()


def test_basic_ways(game_state):
    totalWays = len(game_state.board[0]) ** len(
        game_state.board
    )  # Assume all reels have equal rows
    for idx, _ in enumerate(game_state.board):
        for idy, _ in enumerate(game_state.board[idx]):
            if idx < len(game_state.board) - 1:
                game_state.board[idx][idy] = game_state.create_symbol("H1")
            else:
                game_state.board[idx][idy] = game_state.create_symbol("W")

    windata = Ways.get_ways_data(game_state.config, game_state.board)
    assert windata["totalWin"] == totalWays * game_state.config.paytable[(5, "H1")]


def test_mixed_ways(game_state):
    sym1Ways = (len(game_state.board[0]) - 1) ** len(game_state.board)
    sym2Ways = 1
    for idx, _ in enumerate(game_state.board):
        for idy, _ in enumerate(game_state.board[idx]):
            if idy == 0:
                game_state.board[idx][idy] = game_state.create_symbol("H1")
            else:
                game_state.board[idx][idy] = game_state.create_symbol("H2")

    windata = Ways.get_ways_data(game_state.config, game_state.board)
    assert windata["wins"][0]["meta"]["ways"] == sym2Ways
    assert windata["wins"][1]["meta"]["ways"] == sym1Ways
    assert windata["totalWin"] == windata["wins"][0]["win"] + windata["wins"][1]["win"]
