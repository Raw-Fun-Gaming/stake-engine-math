"""Set conditions/parameters for optimization program program"""

from optimization_program.optimization_config import (
    ConstructConditions,
    ConstructParameters,
    ConstructScaling,
    verify_optimization_input,
)


class OptimizationSetup:
    """Farm Pop optimization setup."""

    def __init__(self, game_config):
        self.game_config = game_config

        rtp = game_config.rtp
        win_cap = game_config.win_cap
        splits = game_config.optimization_rtp_splits
        hit_rates = game_config.optimization_hit_rates

        # ── Base mode ──

        base_splits = splits["base"]
        base_wincap_rtp = base_splits["wincap"]
        base_free_game_rtp = base_splits["free_game"]
        base_base_game_rtp = rtp - base_wincap_rtp - base_free_game_rtp

        base_params = {
            "conditions": {
                "wincap": ConstructConditions(
                    rtp=base_wincap_rtp, av_win=win_cap, search_conditions=win_cap
                ).return_dict(),
                "0": ConstructConditions(
                    rtp=0, av_win=0, search_conditions=0
                ).return_dict(),
                "free_game": ConstructConditions(
                    rtp=base_free_game_rtp,
                    hr=hit_rates["base"]["free_game"],
                    search_conditions={"symbol": "scatter"},
                ).return_dict(),
                "base_game": ConstructConditions(
                    hr=hit_rates["base"]["base_game"], rtp=base_base_game_rtp
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
        }

        # ── Ante modes (same structure as base, different free game hit rates) ──

        def build_ante_params(mode_name):
            ante_splits = splits[mode_name]
            ante_wincap_rtp = ante_splits["wincap"]
            ante_free_game_rtp = ante_splits["free_game"]
            ante_base_game_rtp = rtp - ante_wincap_rtp - ante_free_game_rtp

            return {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=ante_wincap_rtp, av_win=win_cap, search_conditions=win_cap
                    ).return_dict(),
                    "0": ConstructConditions(
                        rtp=0, av_win=0, search_conditions=0
                    ).return_dict(),
                    "free_game": ConstructConditions(
                        rtp=ante_free_game_rtp,
                        hr=hit_rates[mode_name]["free_game"],
                        search_conditions={"symbol": "scatter"},
                    ).return_dict(),
                    "base_game": ConstructConditions(
                        hr=hit_rates[mode_name]["base_game"], rtp=ante_base_game_rtp
                    ).return_dict(),
                },
                "scaling": base_params["scaling"],
                "parameters": base_params["parameters"],
            }

        # ── Bonus mode ──

        bonus_splits = splits["bonus"]
        bonus_wincap_rtp = bonus_splits["wincap"]
        bonus_free_game_rtp = rtp - bonus_wincap_rtp

        bonus_params = {
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
                        "scale_factor": 0.9,
                        "win_range": (20, 50),
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
        }

        # ── Assemble all modes ──

        self.game_config.optimization_params = {
            "base": base_params,
            "ante-2x": build_ante_params("ante-2x"),
            "ante-5x": build_ante_params("ante-5x"),
            "ante-10x": build_ante_params("ante-10x"),
            "bonus": bonus_params,
        }

        verify_optimization_input(self.game_config, self.game_config.optimization_params)
