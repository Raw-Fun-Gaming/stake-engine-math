"""Template game configuration file, detailing required user-specified inputs."""

from src.config.config import BetMode, Config
from src.config.distributions import Distribution


class GameConfig(Config):
    """Template configuration class."""

    def __init__(self):
        super().__init__()
        self.game_id = ""
        self.provider_number = 0
        self.working_name = ""
        self.win_cap = 0
        self.win_type = ""
        self.rtp = 0
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 0
        self.num_rows = [
            0
        ] * self.num_reels  # Optionally include variable number of rows per reel
        # Board and Symbol Properties
        self.paytable = {}

        self.include_padding = True
        self.special_symbols = {"wild": [], "scatter": [], "multiplier": []}

        self.free_spin_triggers = {self.base_game_type: {}, self.free_game_type: {}}
        self.anticipation_triggers = {self.base_game_type: 0, self.free_game_type: 0}
        # Reels
        reels = {"base": "base.csv", "free": "free.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(str.join("/", [self.reels_path, f]))

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
                            "scatter_triggers": {},
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
                            "scatter_triggers": {},
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
        ]
