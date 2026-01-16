"""Handle generation configuration files after simulations and optimization process have concluded."""

import json
import os
import shutil
import warnings
from collections import defaultdict

from utils.analysis.distribution_functions import (
    get_distribution_moments,
    get_lookup_length,
    make_win_distribution,
)
from utils.get_file_hash import get_hash


def copy_and_rename_csv(filepath: str) -> None:
    """If no optimization has been run, initialise the lookup table."""
    file_location = os.path.dirname(filepath)
    new_filepath = os.path.join(
        file_location, os.path.splitext(os.path.basename(filepath))[0] + "_0.csv"
    )
    shutil.copy(filepath, new_filepath)


def generate_configs(
    game_state: object, json_padding: bool = True, assign_properties: bool = True
):
    """Construct frontend, backend and optimization-required configuration files."""
    make_fe_config(
        game_state=game_state,
        json_padding=json_padding,
        assign_properties=assign_properties,
    )
    make_be_config(game_state)
    make_temp_math_config(game_state)
    make_index_config(game_state)
    # make_math_config(game_state)


def make_index_config(game_state: object):
    """
    RGS config file list verification
    This file is used to locate all published math files from AWS. Custom directory structures can be uplaoded
    through the ACP, though the new directory structure must be reflected in the manifest.json file.
    """
    manifest_object = defaultdict(list)

    cost_map = {}
    for bclass in game_state.config.bet_modes:
        cost_map[bclass._name] = float(bclass._cost)

    with open(
        game_state.output_files.configs["paths"]["manifest"], "w", encoding="UTF-8"
    ) as f:
        with open(
            game_state.output_files.configs["paths"]["be_config"], "r", encoding="UTF-8"
        ) as f2:
            config_json = json.load(f2)

        for bm in config_json["bookShelfConfig"]:
            mode_obj = defaultdict(str)
            mode_obj["name"] = bm["name"]
            mode_obj["cost"] = cost_map[bm["name"]]
            mode_obj["events"] = bm["booksFile"]["file"]
            mode_obj["weights"] = bm["tables"][0]["file"]

            manifest_object["modes"].append(mode_obj)

        f.write(json.dumps(manifest_object, indent=4))


def pass_fe_bet_mode(bet_mode):
    """Generate frontend configuration json file."""
    mode_info = {}
    mode_info["cost"] = bet_mode.get_cost()
    mode_info["feature"] = bet_mode.get_feature()
    mode_info["buyBonus"] = bet_mode.get_buy_bonus()
    mode_info["rtp"] = bet_mode.get_rtp()
    mode_info["max_win"] = bet_mode.get_win_cap()

    return {bet_mode.get_name(): mode_info}


def make_temp_math_config(game_state):
    """
    This is a temporary function who's only purpose is to generate a math_config.json file
    which is directly compatible with with existing optimization script. Will be reformatted
    when the new algorithm is implemented.
    """
    file = open(
        game_state.output_files.configs["paths"]["math_config"], "w", encoding="UTF-8"
    )
    jsonInfo = {}
    jsonInfo["game_id"] = game_state.config.game_id
    jsonInfo["bet_modes"] = []
    jsonInfo["fences"] = []
    jsonInfo["dresses"] = []
    rust_dict = {}
    rust_dict["game_id"] = jsonInfo["game_id"]
    rust_dict["bet_modes"] = []

    # Separated bet_mode information
    opt_mode = None
    for bet_mode in game_state.config.bet_modes:
        for mode, mode_obj in game_state.config.opt_params.items():
            if mode == bet_mode.get_name():
                opt_mode = mode
                break

        if opt_mode is not None:
            bet_mode_rust = {
                "bet_mode": bet_mode.get_name(),
                "cost": bet_mode.get_cost(),
                "rtp": bet_mode.get_rtp(),
                "max_win": bet_mode.get_win_cap(),
            }
            rust_dict["bet_modes"] += [bet_mode_rust]
            jsonInfo["bet_modes"].append(bet_mode_rust)

            rust_dict["fences"] = []
            rust_fence = {"bet_mode": bet_mode.get_name(), "fences": []}
            fence_info = {}
            for fence, fence_obj in mode_obj["conditions"].items():
                fence_info = {}
                fence_info["name"] = fence
                if fence_obj.get("av_win") is not None:
                    fence_info["avg_win"] = str(fence_obj["av_win"])
                if fence_obj.get("hr") is not None:
                    fence_info["hr"] = str(fence_obj["hr"])
                if fence_obj.get("rtp") is not None:
                    fence_info["rtp"] = str(fence_obj["rtp"])

                fence_info["identity_condition"] = {}
                fence_info["identity_condition"]["search"] = []
                if fence_obj["force_search"] != {}:
                    for search_key, search_val in fence_obj["force_search"].items():
                        fence_info["identity_condition"]["search"].append(
                            {
                                "name": str(search_key),
                                "value": str(search_val),
                            }
                        )
                fence_info["identity_condition"]["win_range_start"] = fence_obj[
                    "search_range"
                ][0]
                fence_info["identity_condition"]["win_range_end"] = fence_obj[
                    "search_range"
                ][1]
                fence_info["identity_condition"]["opposite"] = False

                rust_fence["fences"] += [fence_info]
            rust_dict["fences"] += [rust_fence]
            jsonInfo["fences"].append(rust_fence)

            rust_dict["dresses"] = []
            rust_dress = {"bet_mode": bet_mode.get_name(), "dresses": []}
            for dress_obj in mode_obj["scaling"]:
                dress_info = {}
                dress_info["fence"] = dress_obj["criteria"]
                dress_info["scale_factor"] = str(dress_obj["scale_factor"])
                dress_info["identity_condition_win_range"] = [
                    dress_obj["win_range"][0],
                    dress_obj["win_range"][1],
                ]
                dress_info["prob"] = dress_obj["probability"]

                rust_dress["dresses"].append(dress_info)

            rust_dict["dresses"] += [rust_dress]
            jsonInfo["dresses"].append(rust_dress)

    file.write(json.dumps(jsonInfo, indent=4))
    file.close()


def make_math_config(game_state):
    """Create configuration file consumed by the optimization algorithm."""
    jsonInfo = {}
    jsonInfo["gameID"] = game_state.config.game_id

    rust_dict = {}
    rust_dict["game_name"] = jsonInfo["gameID"]
    rust_dict["bet_modes"] = []
    for bet_mode in game_state.config.bet_modes:
        bet_mode_rust = {
            "bet_mode": bet_mode.get_name(),
            "cost": bet_mode.get_cost(),
            "rtp": bet_mode.get_rtp(),
            "max_win": bet_mode.get_win_cap(),
        }
        opt_mode = None
        for mode, mode_obj in game_state.config.optimization_params.items():
            if mode == bet_mode.get_name():
                opt_mode = mode
                break
        if opt_mode is not None:

            data = []
            search_data = []
            for cond, opt_obj in mode_obj["conditions"].items():
                opt_dict = opt_obj.to_dict()
                if opt_dict["force_search"] != {}:
                    search_data.append({})
                    search_data[-1]["name"] = str(
                        list(opt_dict["force_search"].keys())[0]
                    )
                    search_data[-1]["value"] = str(
                        list(opt_dict["force_search"].values())[0]
                    )
                else:
                    search_data = []
                data.append(
                    {
                        "criteria": cond,
                        "rtp": opt_dict["rtp"],
                        "avg_win": opt_dict["av_win"],
                        "hr": opt_dict["hr"],
                        "identity_condition": {
                            "search": search_data,
                            "opposite": False,
                            "win_range_start": opt_dict["search_range"][0],
                            "win_range_end": opt_dict["search_range"][1],
                        },
                    }
                )
            bet_mode_rust["opt_conditions"] = data

            bet_mode_rust["scaling"] = []
            for scale in mode_obj["scaling"]:
                bet_mode_rust["scaling"].append(
                    {
                        "criteria": scale["criteria"],
                        "scale_factor": scale["scale_factor"],
                        "identity_condition_win_range": [
                            scale["win_range"][0],
                            scale["win_range"][1],
                        ],
                        "prob": scale["probability"],
                    }
                )

            bet_mode_rust["opt_params"] = mode_obj["parameters"]

            rust_dict["bet_modes"].append(bet_mode_rust)

            file = open(game_state.config.config_path + "/math_config.json", "w")
            file.write(json.dumps(rust_dict, indent=4))
            file.close()


def make_fe_config(game_state, json_padding=True, assign_properties=True, **kwargs):
    """
    json_padding formats symbols the same as the board {'name': symbol} (default), alternatively an array of strings ['H1',...] is passed
    assign_properties will invoke a symbol attribute
    """
    if assign_properties:
        assert (
            json_padding is True
        ), "json_padding must be `True` to invoke symbol properties in padding"

    json_info = {}
    json_info["providerName"] = str(game_state.config.provider_name)
    json_info["gameName"] = str(game_state.config.game_name)
    json_info["gameID"] = game_state.config.game_id
    json_info["rtp"] = game_state.config.rtp
    json_info["numReels"] = game_state.config.num_reels
    json_info["numRows"] = game_state.config.num_rows

    json_info["betModes"] = {}
    for bet_mode in game_state.config.bet_modes:
        bm_info = pass_fe_bet_mode(bet_mode)
        m_name = next(iter(bm_info))
        json_info["betModes"][m_name] = bm_info[m_name]

    # Optionally include any custom information
    for key, val in kwargs:
        json_info[key] = val

    if hasattr(game_state.config, "pay_lines") or hasattr(
        game_state.config, "paylines"
    ):
        json_info["paylines"] = game_state.config.paylines

    symbols = {}
    for sym in game_state.symbol_storage.symbols.values():
        symbols[sym.name] = {}
        special_properties = []
        for prop in game_state.config.special_symbols:
            if sym.name in game_state.config.special_symbols[prop]:
                special_properties.append(prop)

        if hasattr(sym, "paytable"):
            symbols[sym.name]["paytable"] = sym.paytable

        if len(special_properties) > 0:
            symbols[sym.name]["special_properties"] = special_properties

    json_info["symbols"] = []
    for key, val in symbols.items():
        json_info["symbols"].append({key: val})

    reelstrip_json = {}
    if json_padding:
        for idx, reels in game_state.config.padding_reels.items():
            reelstrip_json[idx] = [[] for _ in range(game_state.config.num_reels)]
            for c, _ in enumerate(reels):
                column = reels[c]
                for i, _ in enumerate(column):
                    reelstrip_json[idx][c].append({"name": column[i]})

        json_info["paddingReels"] = reelstrip_json
    elif not json_padding:
        json_info["paddingReels"] = game_state.config.paddingReels

    f_name = os.path.join(
        game_state.output_files.config_path,
        f"config_fe_{game_state.config.game_id}.json",
    )
    fe_json = open(f_name, "w", encoding="UTF-8")
    fe_json.write(json.dumps(json_info, indent=4))
    fe_json.close()


def make_be_config(game_state):
    """ "Generate config.json for RGS to retrieve game details and hash-values."""
    config = game_state.config

    fe_config_sha = get_hash(game_state.output_files.configs["paths"]["fe_config"])
    available_bm = game_state.config.bet_modes

    # General game data
    be_info = {}
    be_info["workingName"] = config.working_name
    be_info["frontendConfig"] = {
        "file": game_state.output_files.configs["names"]["fe_config"],
        "sha256": fe_config_sha,
    }
    be_info["workingName"] = str(config.working_name)
    be_info["gameID"] = config.game_id
    if config.rtp < 1:
        be_info["rtp"] = config.rtp * 100  # RGS expects RTP as a %
    else:
        be_info["rtp"] = config.rtp
    be_info["betDenomination"] = int(config.min_denomination * 100 * 100)
    be_info["minDenomination"] = int(config.min_denomination * 100)
    be_info["providerNumber"] = int(config.provider_number)
    be_info["standardForceFile"] = {
        "file": "force.json",
        "sha256": get_hash(
            os.path.join(game_state.output_files.force_path, "force.json")
        ),
    }

    # Bet mode specific data
    be_info["bookShelfConfig"] = []
    for bet in available_bm:
        lut_table = game_state.output_files.lookups[bet.get_name()]["paths"][
            "optimized_lookup"
        ]
        if not (os.path.exists(lut_table)):
            print(f"File does not exist: {lut_table}, \n Generating lut_0 file.")
            base_table = game_state.output_files.lookups[bet.get_name()]["paths"][
                "base_lookup"
            ]
            copy_and_rename_csv(base_table)

        lut_sha_value = get_hash(lut_table)
        dist = make_win_distribution(lut_table)
        _, std_val, _, _ = get_distribution_moments(dist)
        std_val = round(std_val / bet.get_cost(), 2)
        booklength = get_lookup_length(lut_table)

        _, lut_nme = os.path.split(lut_table)
        dic = {
            "name": bet.get_name(),
            "tables": [{"file": lut_nme, "sha256": lut_sha_value}],
            "cost": bet.get_cost(),
            "rtp": bet.get_rtp(),
            "std": std_val,
            "bookLength": booklength,
            "feature": bet.get_feature(),
            "autoEndRoundDisabled": bet.get_auto_close_disabled(),
            "buyBonus": bet.get_buy_bonus(),
            "maxWin": bet.get_win_cap(),
        }
        data_loc = game_state.output_files.books[bet.get_name()]["paths"][
            "books_compressed"
        ]
        try:
            data_sha = get_hash(data_loc)
        except FileNotFoundError:
            data_sha = ""
            warnings.warn("Compressed books file not found. Hash is empty.")

        force_loc = game_state.output_files.force[bet.get_name()]["paths"][
            "force_record"
        ]
        force_sha = get_hash(force_loc)

        dic["booksFile"] = {
            "file": game_state.output_files.books[bet.get_name()]["names"][
                "books_compressed"
            ],
            "sha256": data_sha,
        }
        dic["forceFile"] = {
            "file": game_state.output_files.force[bet.get_name()]["names"][
                "force_record"
            ],
            "sha256": force_sha,
        }
        be_info["bookShelfConfig"].append(dic)

    file = open(
        game_state.output_files.configs["paths"]["be_config"], "w", encoding="UTF-8"
    )
    file.write(json.dumps(be_info, indent=4))
    file.close()
