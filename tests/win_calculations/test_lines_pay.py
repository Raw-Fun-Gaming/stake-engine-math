"""Test basic lines-calculation functionality."""

import pytest

from src.calculations.lines import Lines
from tests.win_calculations.game_test_config import GameStateTest, create_blank_board


class GameLinesConfig:
    """Testing game functions"""

    def __init__(self):
        self.game_id = "0_test_class"
        self.rtp = 0.9700

        # Game Dimensions
        self.num_reels = 5
        self.num_rows = [5] * self.num_reels
        # Board and Symbol Properties
        self.paytable = {
            (5, "W"): 100,
            (4, "W"): 90,
            (3, "W"): 80,
            (5, "H1"): 70,
            (4, "H1"): 60,
            (3, "H1"): 50,
            (5, "WM"): 30,
            (4, "WM"): 20,
            (3, "WM"): 10,
        }

        self.paylines = {
            1: [
                0,
                0,
                0,
                0,
                0,
            ],
            2: [
                0,
                1,
                2,
                1,
                2,
            ],
            3: [
                4,
                3,
                2,
                3,
                4,
            ],
            4: [
                4,
                4,
                4,
                4,
                4,
            ],
        }

        self.special_symbols = {
            "wild": ["W"],
            "scatter": ["S"],
            "multiplier": ["M", "WM"],
            "blank": ["X"],
        }

        self.mult_values = [2, 3, 4, 5]
        self.bet_modes = []
        self.base_game_type = "base_game"
        self.free_game_type = "free_game"


def create_test_lines_game_state():
    """Boilerplate game_state for testing."""
    test_config = GameLinesConfig()
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


def test_linespay_basic(game_state):
    "Basic lines-payout."
    for idx, _ in enumerate(game_state.board):
        for idy, _ in enumerate(game_state.board[idx]):
            if idx != len(game_state.board) - 1:
                game_state.board[idx][idy] = game_state.create_symbol("H1")
            else:
                game_state.board[idx][idy] = game_state.create_symbol("W")

    windata = Lines.get_lines(game_state.board, game_state.config)
    assert windata["totalWin"] == (
        game_state.config.paytable[(5, "H1")] * len(game_state.config.paylines)
    )


def test_linespay_wilds(game_state):
    "Basic lines-payout."
    for idx, _ in enumerate(game_state.board):
        for idy, _ in enumerate(game_state.board[idx]):
            if idx < 4:
                game_state.board[idx][idy] = game_state.create_symbol("W")
            else:
                game_state.board[idx][idy] = game_state.create_symbol("H1")

    windata = Lines.get_lines(game_state.board, game_state.config)
    # 4Kind W pay > 5Kind H1
    assert windata["totalWin"] == (
        game_state.config.paytable[(4, "W")] * len(game_state.config.paylines)
    )


def test_linespay_mult(game_state):
    "Special symbol with multiplier"
    for idx, _ in enumerate(game_state.board):
        for idy, _ in enumerate(game_state.board[idx]):
            if idy == 0:
                game_state.board[idx][idy] = game_state.create_symbol("WM")
            else:
                game_state.board[idx][idy] = game_state.create_symbol("X")

    windata = Lines.get_lines(game_state.board, game_state.config)
    assert windata["totalWin"] == (
        game_state.config.paytable[(5, "WM")] * sum([3, 3, 3, 3, 3])
    )
