"""Cluster game configuration file/setup"""

import os

from src.config.bet_mode import BetMode
from src.config.config import Config
from src.config.distributions import Distribution


class GameConfig(Config):
    """Singleton cluster game configuration class."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "template_cluster"
        self.provider_number = 0
        self.working_name = "Sample Cluster Game"
        self.win_cap = 5000.0
        self.win_type = "cluster"
        self.rtp = 0.9700
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 7
        # Optionally include variable number of rows per reel
        self.num_rows = [7] * self.num_reels
        # Board and Symbol Properties
        t1, t2, t3, t4 = (5, 5), (6, 8), (9, 12), (13, 36)
        pay_group = {
            (t1, "H1"): 5.0,
            (t2, "H1"): 12.5,
            (t3, "H1"): 25.0,
            (t4, "H1"): 60.0,
            (t1, "H2"): 2.0,
            (t2, "H2"): 5.0,
            (t3, "H2"): 10.0,
            (t4, "H2"): 40.0,
            (t1, "H3"): 1.3,
            (t2, "H3"): 3.2,
            (t3, "H3"): 7.0,
            (t4, "H3"): 30.0,
            (t1, "H4"): 1.0,
            (t2, "H4"): 2.5,
            (t3, "H4"): 6.0,
            (t4, "H4"): 20.0,
            (t1, "L1"): 0.6,
            (t2, "L1"): 1.5,
            (t3, "L1"): 4.0,
            (t4, "L1"): 10.0,
            (t1, "L2"): 0.4,
            (t2, "L2"): 1.2,
            (t3, "L2"): 3.5,
            (t4, "L2"): 8.0,
            (t1, "L3"): 0.2,
            (t2, "L3"): 0.8,
            (t3, "L3"): 2.5,
            (t4, "L3"): 5.0,
            (t1, "L4"): 0.1,
            (t2, "L4"): 0.5,
            (t3, "L4"): 1.5,
            (t4, "L4"): 4.0,
        }
        self.paytable = self.convert_range_table(pay_group)

        self.include_padding = True
        self.special_symbols = {"wild": ["W"], "scatter": ["S"]}

        self.free_spin_triggers = {
            self.base_game_type: {4: 10, 5: 12, 6: 15, 7: 18, 8: 20},
            self.free_game_type: {3: 5, 4: 8, 5: 10, 6: 12, 7: 15, 8: 18},
        }
        self.anticipation_triggers = {
            self.base_game_type: min(
                self.free_spin_triggers[self.base_game_type].keys()
            )
            - 1,
            self.free_game_type: min(
                self.free_spin_triggers[self.free_game_type].keys()
            )
            - 1,
        }

        self.maximum_board_multiplier = 512

        reels = {"base": "base.csv", "free": "free.csv", "wincap": "wincap.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

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
                                self.free_game_type: {"free": 1, "wincap": 5},
                            },
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
                            "scatter_triggers": {4: 5, 5: 1},
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
                cost=200,
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
                                self.free_game_type: {"free": 1, "wincap": 5},
                            },
                            "multiplier_values": {
                                self.base_game_type: {
                                    2: 10,
                                    3: 20,
                                    4: 30,
                                    5: 20,
                                    10: 20,
                                    20: 20,
                                    50: 10,
                                },
                                self.free_game_type: {
                                    2: 10,
                                    3: 20,
                                    4: 30,
                                    5: 20,
                                    10: 20,
                                    20: 20,
                                    50: 10,
                                },
                            },
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
                            "scatter_triggers": {4: 5, 5: 1},
                            "force_wincap": False,
                            "force_free_game": True,
                        },
                    ),
                ],
            ),
        ]

        # Optimisation(rtp, avgWin, hit-rate, recordConditions)
