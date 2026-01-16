"""Template game configuration file, detailing required user-specified inputs."""

import os

from src.config.bet_mode import BetMode
from src.config.config import Config
from src.config.distributions import Distribution


class GameConfig(Config):
    """Template configuration class."""

    def __init__(self):
        super().__init__()
        self.game_id = "template_expanding_wilds"
        self.provider_number = 0
        self.working_name = "Expanding Wilds"
        self.win_cap = 5000
        self.win_type = "lines"
        self.rtp = 0.97
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 5
        self.num_rows = [
            5
        ] * self.num_reels  # Optionally include variable number of rows per reel
        # Board and Symbol Properties
        self.paytable = {
            (5, "W"): 20,
            (4, "W"): 10,
            (3, "W"): 5,
            (5, "H1"): 20,
            (4, "H1"): 10,
            (3, "H1"): 5,
            (5, "H2"): 15,
            (4, "H2"): 5,
            (3, "H2"): 3,
            (5, "H3"): 10,
            (4, "H3"): 3,
            (3, "H3"): 2,
            (5, "H4"): 8,
            (4, "H4"): 2,
            (3, "H4"): 1,
            (5, "L1"): 5,
            (4, "L1"): 1,
            (3, "L1"): 0.5,
            (5, "L2"): 3,
            (4, "L2"): 0.7,
            (3, "L2"): 0.3,
            (5, "L3"): 3,
            (4, "L3"): 0.7,
            (3, "L3"): 0.3,
            (5, "L4"): 2,
            (4, "L4"): 0.5,
            (3, "L4"): 0.2,
            (5, "L5"): 2,
            (4, "L5"): 0.5,
            (3, "L5"): 0.2,
            (99, "X"): 0,  # only included for symbol register
        }
        self.paylines = {
            # horizontal lines
            1: [0, 0, 0, 0, 0],
            2: [1, 1, 1, 1, 1],
            3: [2, 2, 2, 2, 2],
            4: [3, 3, 3, 3, 3],
            5: [4, 4, 4, 4, 4],
            # W and M shaped lines
            6: [0, 1, 0, 1, 0],
            7: [1, 2, 1, 2, 1],
            8: [2, 3, 2, 3, 2],
            9: [3, 4, 3, 4, 3],
            10: [1, 0, 1, 0, 1],
            11: [2, 1, 2, 1, 2],
            12: [3, 2, 3, 2, 3],
            13: [4, 3, 4, 3, 4],
            # diagonal lines
            14: [0, 1, 2, 3, 4],
            15: [4, 3, 2, 1, 0],
        }
        self.include_padding = True
        self.special_symbols = {
            "wild": ["W"],
            "scatter": ["S"],
            "multiplier": ["W"],
            "prize": ["P"],
        }

        self.free_spin_triggers = {
            self.base_game_type: {3: 8, 4: 12, 5: 15}
        }  # No retriggers in free game
        self.anticipation_triggers = {
            self.base_game_type: min(
                self.free_spin_triggers[self.base_game_type].keys()
            )
            - 1,
        }
        # Reels
        reels = {
            "base": "base.csv",
            "free": "free.csv",
            "super_spin": "super_spin.csv",
            "super_spin_wincap": "super_spin_wincap.csv",
        }
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        self.padding_reels = {
            "base_game": self.reels["base"],
            "free_game": self.reels["free"],
            "super_spin": self.reels["super_spin"],
        }

        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.win_cap,
                auto_close_disabled=False,
                is_feature=True,
                is_buy_bonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=self.win_cap,
                        conditions={
                            "reel_weights": {
                                self.base_game_type: {"base": 1},
                                self.free_game_type: {"free": 1},
                            },
                            "multiplier_values": {
                                self.free_game_type: {
                                    2: 200,
                                    3: 80,
                                    4: 40,
                                    5: 30,
                                    10: 10,
                                    20: 5,
                                    50: 1,
                                }
                            },
                            "landing_wilds": {0: 100, 1: 20, 2: 5, 3: 2},
                            "scatter_triggers": {4: 1, 5: 2},
                            "force_wincap": True,
                            "force_free_game": True,
                        },
                    ),
                    Distribution(
                        criteria="free_game",
                        quota=0.1,
                        conditions={
                            "reel_weights": {
                                self.base_game_type: {"base": 1},
                                self.free_game_type: {"free": 1},
                            },
                            "multiplier_values": {
                                self.free_game_type: {
                                    2: 300,
                                    3: 100,
                                    4: 30,
                                    5: 20,
                                    10: 5,
                                    20: 5,
                                    50: 1,
                                }
                            },
                            "landing_wilds": {0: 200, 1: 15, 2: 5, 3: 1},
                            "scatter_triggers": {4: 1, 5: 2},
                            "force_wincap": False,
                            "force_free_game": True,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.4,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.base_game_type: {"base": 1}},
                            "force_wincap": False,
                            "force_free_game": False,
                        },
                    ),
                    Distribution(
                        criteria="base_game",
                        quota=0.5,
                        conditions={
                            "reel_weights": {self.base_game_type: {"base": 1}},
                            "force_wincap": False,
                            "force_free_game": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="bonus",
                cost=200.0,
                rtp=self.rtp,
                max_win=self.win_cap,
                auto_close_disabled=False,
                is_feature=False,
                is_buy_bonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=self.win_cap,
                        conditions={
                            "reel_weights": {
                                self.base_game_type: {"base": 1},
                                self.free_game_type: {"free": 1},
                            },
                            "multiplier_values": {
                                self.free_game_type: {
                                    2: 100,
                                    3: 50,
                                    4: 40,
                                    5: 30,
                                    10: 5,
                                    20: 5,
                                    50: 1,
                                }
                            },
                            "landing_wilds": {0: 100, 1: 15, 2: 10, 3: 2},
                            "scatter_triggers": {4: 1, 5: 2},
                            "force_wincap": True,
                            "force_free_game": True,
                        },
                    ),
                    Distribution(
                        criteria="free_game",
                        quota=0.1,
                        conditions={
                            "reel_weights": {
                                self.base_game_type: {"base": 1},
                                self.free_game_type: {"free": 1},
                            },
                            "multiplier_values": {
                                self.free_game_type: {
                                    2: 500,
                                    3: 100,
                                    4: 80,
                                    5: 60,
                                    10: 5,
                                    20: 2,
                                    50: 1,
                                }
                            },
                            "scatter_triggers": {4: 1, 5: 2},
                            "landing_wilds": {0: 200, 1: 20, 2: 5, 3: 1},
                            "force_wincap": False,
                            "force_free_game": True,
                        },
                    ),
                ],
            ),
            BetMode(
                name="super_spin",
                cost=50,
                rtp=self.rtp,
                max_win=self.win_cap,
                auto_close_disabled=False,
                is_feature=True,
                is_buy_bonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=self.win_cap,
                        conditions={
                            "reel_weights": {
                                self.base_game_type: {
                                    "super_spin": 1,
                                    "super_spin_wincap": 5,
                                },
                            },
                            "prize_values": {
                                1: 10,
                                2: 20,
                                3: 50,
                                5: 50,
                                10: 50,
                                25: 80,
                                50: 30,
                                100: 20,
                                500: 5,
                                10000: 4,
                            },
                            "force_wincap": True,
                            "force_free_game": False,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.1,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.base_game_type: {"super_spin": 1}},
                            "force_wincap": False,
                            "force_free_game": False,
                            "prize_values": {
                                1: 500,
                            },
                        },
                    ),
                    Distribution(
                        criteria="base_game",
                        quota=0.9,
                        conditions={
                            "reel_weights": {
                                self.base_game_type: {"super_spin": 1},
                            },
                            "prize_values": {
                                1: 700,
                                2: 200,
                                3: 50,
                                5: 30,
                                10: 20,
                                25: 10,
                                50: 5,
                                100: 5,
                                500: 2,
                                1000: 1,
                            },
                            "force_wincap": False,
                            "force_free_game": False,
                        },
                    ),
                ],
            ),
        ]
