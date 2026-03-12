"""Set conditions/parameters for optimization program program"""

from optimization_program.optimization_config import (
    ConstructConditions,
    ConstructParameters,
    ConstructScaling,
    verify_optimization_input,
)


class OptimizationSetup:
    """Template lines optimization setup."""

    def __init__(self, game_config):
        self.game_config = game_config

        rtp = game_config.rtp
        win_cap = game_config.win_cap
        splits = game_config.opt_rtp_splits

        # Base mode RTP splits
        base_splits = splits["base"]
        wincap_rtp = base_splits["wincap"]
        zero_rtp = base_splits["zero"]
        free_game_rtp = base_splits["free_game"]
        base_game_rtp = rtp - wincap_rtp - zero_rtp - free_game_rtp

        # Bonus mode RTP splits
        bonus_splits = splits["bonus"]
        bonus_wincap_rtp = bonus_splits["wincap"]
        bonus_free_game_rtp = rtp - bonus_wincap_rtp

        self.game_config.opt_params = {
            "base": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=wincap_rtp, av_win=win_cap, search_conditions=win_cap
                    ).return_dict(),
                    "0": ConstructConditions(
                        rtp=zero_rtp, av_win=0, search_conditions=0
                    ).return_dict(),
                    "free_game": ConstructConditions(
                        rtp=free_game_rtp,
                        hr=game_config.opt_free_hr,
                        search_conditions={"symbol": "scatter"},
                    ).return_dict(),
                    "base_game": ConstructConditions(
                        hr=game_config.opt_base_hr, rtp=base_game_rtp
                    ).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "base_game",
                            "scale_factor": 1.2,
                            "win_range": (1, 2),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "base_game",
                            "scale_factor": 1.5,
                            "win_range": (10, 20),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "free_game",
                            "scale_factor": 0.8,
                            "win_range": (1000, 2000),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "free_game",
                            "scale_factor": 1.2,
                            "win_range": (3000, 4000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[50, 100, 200],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                ).return_dict(),
            },
            "bonus": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=bonus_wincap_rtp, av_win=win_cap, search_conditions=win_cap
                    ).return_dict(),
                    "free_game": ConstructConditions(
                        rtp=bonus_free_game_rtp, hr="x"
                    ).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "free_game",
                            "scale_factor": 1.2,
                            "win_range": (1, 20),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "free_game",
                            "scale_factor": 0.5,
                            "win_range": (20, 50),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "free_game",
                            "scale_factor": 1.8,
                            "win_range": (50, 100),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "free_game",
                            "scale_factor": 0.8,
                            "win_range": (1000, 2000),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "free_game",
                            "scale_factor": 1.2,
                            "win_range": (3000, 4000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[10, 20, 50],
                    test_weights=[0.6, 0.2, 0.2],
                    score_type="rtp",
                ).return_dict(),
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)
