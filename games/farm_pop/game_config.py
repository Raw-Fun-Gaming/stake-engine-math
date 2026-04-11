"""Farm Pop game configuration file/setup"""

import os

from src.config.bet_mode import BetMode
from src.config.config import Config
from src.config.distribution import Distribution


class GameConfig(Config):
    """Singleton Farm Pop game configuration class."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "farm_pop"
        self.provider_number = 0
        self.working_name = "Farm Pop"
        self.win_cap = 10000.0
        self.win_type = "cluster"
        self.rtp = 0.96
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 7
        # Optionally include variable number of rows per reel
        self.num_rows = [7] * self.num_reels
        # Board and Symbol Properties
        t1 = (5, 5)
        t2 = (6, 6)
        t3 = (7, 8)
        t4 = (9, 10)
        t5 = (11, 13)
        t6 = (14, 16)
        t7 = (17, 20)
        t8 = (21, 24)
        t9 = (25, 29)
        t10 = (30, 34)
        t11 = (35, 40)
        t12 = (41, 46)
        t13 = (47, 53)
        t14 = (54, 60)
        pay_group = {
            # H1 - Premium (e.g. Golden Chicken)
            (t1, "H1"): 1.0,
            (t2, "H1"): 1.5,
            (t3, "H1"): 2.5,
            (t4, "H1"): 4.0,
            (t5, "H1"): 6.5,
            (t6, "H1"): 10.0,
            (t7, "H1"): 15.0,
            (t8, "H1"): 22.0,
            (t9, "H1"): 35.0,
            (t10, "H1"): 55.0,
            (t11, "H1"): 85.0,
            (t12, "H1"): 135.0,
            (t13, "H1"): 225.0,
            (t14, "H1"): 400.0,
            # H2
            (t1, "H2"): 0.7,
            (t2, "H2"): 1.0,
            (t3, "H2"): 1.8,
            (t4, "H2"): 2.8,
            (t5, "H2"): 4.5,
            (t6, "H2"): 7.0,
            (t7, "H2"): 10.0,
            (t8, "H2"): 15.0,
            (t9, "H2"): 24.0,
            (t10, "H2"): 38.0,
            (t11, "H2"): 58.0,
            (t12, "H2"): 90.0,
            (t13, "H2"): 150.0,
            (t14, "H2"): 275.0,
            # H3
            (t1, "H3"): 0.5,
            (t2, "H3"): 0.7,
            (t3, "H3"): 1.2,
            (t4, "H3"): 2.0,
            (t5, "H3"): 3.2,
            (t6, "H3"): 5.0,
            (t7, "H3"): 7.5,
            (t8, "H3"): 11.0,
            (t9, "H3"): 17.0,
            (t10, "H3"): 27.0,
            (t11, "H3"): 42.0,
            (t12, "H3"): 65.0,
            (t13, "H3"): 100.0,
            (t14, "H3"): 185.0,
            # H4
            (t1, "H4"): 0.4,
            (t2, "H4"): 0.5,
            (t3, "H4"): 0.9,
            (t4, "H4"): 1.5,
            (t5, "H4"): 2.5,
            (t6, "H4"): 3.8,
            (t7, "H4"): 5.5,
            (t8, "H4"): 8.0,
            (t9, "H4"): 13.0,
            (t10, "H4"): 20.0,
            (t11, "H4"): 30.0,
            (t12, "H4"): 46.0,
            (t13, "H4"): 72.0,
            (t14, "H4"): 130.0,
            # L1
            (t1, "L1"): 0.25,
            (t2, "L1"): 0.35,
            (t3, "L1"): 0.6,
            (t4, "L1"): 1.0,
            (t5, "L1"): 1.6,
            (t6, "L1"): 2.5,
            (t7, "L1"): 3.8,
            (t8, "L1"): 5.5,
            (t9, "L1"): 8.5,
            (t10, "L1"): 13.0,
            (t11, "L1"): 20.0,
            (t12, "L1"): 30.0,
            (t13, "L1"): 48.0,
            (t14, "L1"): 80.0,
            # L2
            (t1, "L2"): 0.2,
            (t2, "L2"): 0.3,
            (t3, "L2"): 0.5,
            (t4, "L2"): 0.8,
            (t5, "L2"): 1.3,
            (t6, "L2"): 2.0,
            (t7, "L2"): 3.0,
            (t8, "L2"): 4.5,
            (t9, "L2"): 7.0,
            (t10, "L2"): 10.0,
            (t11, "L2"): 15.0,
            (t12, "L2"): 24.0,
            (t13, "L2"): 36.0,
            (t14, "L2"): 55.0,
            # L3
            (t1, "L3"): 0.15,
            (t2, "L3"): 0.2,
            (t3, "L3"): 0.35,
            (t4, "L3"): 0.6,
            (t5, "L3"): 1.0,
            (t6, "L3"): 1.5,
            (t7, "L3"): 2.2,
            (t8, "L3"): 3.5,
            (t9, "L3"): 5.0,
            (t10, "L3"): 7.5,
            (t11, "L3"): 11.0,
            (t12, "L3"): 17.0,
            (t13, "L3"): 26.0,
            (t14, "L3"): 40.0,
            # L4
            (t1, "L4"): 0.1,
            (t2, "L4"): 0.15,
            (t3, "L4"): 0.25,
            (t4, "L4"): 0.4,
            (t5, "L4"): 0.6,
            (t6, "L4"): 1.0,
            (t7, "L4"): 1.5,
            (t8, "L4"): 2.5,
            (t9, "L4"): 4.0,
            (t10, "L4"): 6.0,
            (t11, "L4"): 9.0,
            (t12, "L4"): 13.0,
            (t13, "L4"): 20.0,
            (t14, "L4"): 28.0,
        }
        self.paytable = self.convert_range_table(pay_group)

        # Include top/bottom padding symbols in board display
        self.include_padding = False
        # Output paddingPositions array in reveal events
        self.output_padding_positions = False
        self.special_symbols = {"wild": ["W"], "scatter": ["S"]}
        self.exclude_win_detail_keys = {"baseAmount", "multiplier"}
        self.include_board_in_tumble = False

        self.free_spin_triggers = {
            self.base_game_type: {
                4: 10, 5: 12, 6: 15, 7: 18, 8: 20, 9: 22, 10: 25,
                11: 25, 12: 25, 13: 25, 14: 25, 15: 25,
            },
            self.free_game_type: {
                3: 5, 4: 8, 5: 10, 6: 12, 7: 15, 8: 18, 9: 20, 10: 22,
                11: 22, 12: 22, 13: 22, 14: 22, 15: 22,
            },
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

        reels = {
            "base": "base.csv",
            "free": "free.csv",
            "wincap": "wincap.csv",
            "ante_2x": "ante_2x.csv",
            "ante_5x": "ante_5x.csv",
            "ante_10x": "ante_10x.csv",
            "super": "ante_10x.csv",
        }
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
            # Ante modes: graduated value — higher cost = better HR per bet
            # Cost per trigger: 2x*90=180x, 5x*33=165x, 10x*15=150x (vs base 1x*200=200x)
            BetMode(
                name="ante-2x",
                cost=2.0,
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
                                self.base_game_type: {"ante_2x": 1},
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
                                self.base_game_type: {"ante_2x": 1},
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
                            "reel_weights": {self.base_game_type: {"ante_2x": 1}},
                            "force_wincap": False,
                            "force_free_game": False,
                        },
                    ),
                    Distribution(
                        criteria="base_game",
                        quota=0.5,
                        conditions={
                            "reel_weights": {self.base_game_type: {"ante_2x": 1}},
                            "force_wincap": False,
                            "force_free_game": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="ante-5x",
                cost=5.0,
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
                                self.base_game_type: {"ante_5x": 1},
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
                                self.base_game_type: {"ante_5x": 1},
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
                            "reel_weights": {self.base_game_type: {"ante_5x": 1}},
                            "force_wincap": False,
                            "force_free_game": False,
                        },
                    ),
                    Distribution(
                        criteria="base_game",
                        quota=0.5,
                        conditions={
                            "reel_weights": {self.base_game_type: {"ante_5x": 1}},
                            "force_wincap": False,
                            "force_free_game": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="ante-10x",
                cost=10.0,
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
                                self.base_game_type: {"ante_10x": 1},
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
                                self.base_game_type: {"ante_10x": 1},
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
                            "reel_weights": {self.base_game_type: {"ante_10x": 1}},
                            "force_wincap": False,
                            "force_free_game": False,
                        },
                    ),
                    Distribution(
                        criteria="base_game",
                        quota=0.5,
                        conditions={
                            "reel_weights": {self.base_game_type: {"ante_10x": 1}},
                            "force_wincap": False,
                            "force_free_game": False,
                        },
                    ),
                ],
            ),
            # Bonus: guaranteed free spins (100x cost, HR 1:1)
            BetMode(
                name="bonus",
                cost=100,
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
                            "scatter_triggers": {4: 1},
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
                            "scatter_triggers": {4: 1},
                            "force_wincap": False,
                            "force_free_game": True,
                        },
                    ),
                ],
            ),
            # Super: guaranteed 7 scatters → 18 free spins (300x cost)
            BetMode(
                name="super",
                cost=300,
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
                                self.base_game_type: {"super": 1},
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
                            "scatter_triggers": {7: 1},
                            "force_wincap": True,
                            "force_free_game": True,
                        },
                    ),
                    Distribution(
                        criteria="free_game",
                        quota=0.1,
                        conditions={
                            "reel_weights": {
                                self.base_game_type: {"super": 1},
                                self.free_game_type: {"free": 1},
                            },
                            "scatter_triggers": {7: 1},
                            "force_wincap": False,
                            "force_free_game": True,
                        },
                    ),
                ],
            ),
        ]

        # ── Optimization: RTP splits (must sum to self.rtp per mode) ──

        self.optimization_rtp_splits = {
            # Base: standard play
            "base": {
                "wincap": 0.01,
                "free_game": 0.37,
                # base_game is the remainder: rtp - wincap - free_game
            },
            # Ante modes: progressively shift RTP toward free_game
            "ante-2x": {
                "wincap": 0.01,
                "free_game": 0.45,
            },
            "ante-5x": {
                "wincap": 0.01,
                "free_game": 0.55,
            },
            "ante-10x": {
                "wincap": 0.01,
                "free_game": 0.65,
            },
            # Bonus: guaranteed free spins
            "bonus": {
                "wincap": 0.01,
                # free_game is the remainder: rtp - wincap
            },
            # Super: guaranteed free spins (same split as bonus)
            "super": {
                "wincap": 0.01,
                # free_game is the remainder: rtp - wincap
            },
        }

        # ── Optimization: hit rate targets per mode ──

        self.optimization_hit_rates = {
            # Base: 1x cost, 200x per trigger
            "base": {
                "base_game": 3.5,
                "free_game": 200,
            },
            # Ante: graduated value — higher cost = better cost-per-trigger
            "ante-2x": {
                "base_game": 3.5,
                "free_game": 90,     # 2x * 90 = 180x per trigger (10% better)
            },
            "ante-5x": {
                "base_game": 3.5,
                "free_game": 33,     # 5x * 33 = 165x per trigger (17% better)
            },
            "ante-10x": {
                "base_game": 3.5,
                "free_game": 15,     # 10x * 15 = 150x per trigger (25% better)
            },
            # Bonus: 100x cost, guaranteed (HR not used — always triggers)
        }
