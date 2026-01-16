BOARD_MULT_INFO = "boardMultiplierInfo"


def send_multiplier_info_event(
    game_state,
    board_multiplier: int,
    multiplier_info: dict,
    base_win: float,
    updatedWin: float,
):
    multiplier_info, winInfo = {}, {}
    multiplier_info["positions"] = []
    if game_state.config.include_padding:
        for m in range(len(multiplier_info)):
            multiplier_info["positions"].append(
                {
                    "reel": multiplier_info[m]["reel"],
                    "row": multiplier_info[m]["row"] + 1,
                    "multiplier": multiplier_info[m]["value"],
                }
            )
    else:
        for m in range(multiplier_info):
            multiplier_info["positions"].append(
                {
                    "reel": multiplier_info[m]["reel"],
                    "row": multiplier_info[m]["row"],
                    "multiplier": multiplier_info[m]["value"],
                }
            )

    winInfo["tumbleWin"] = int(round(min(base_win, game_state.config.win_cap) * 100))
    winInfo["boardMult"] = board_multiplier
    winInfo["totalWin"] = int(round(min(updatedWin, game_state.config.win_cap) * 100))

    assert round(updatedWin, 1) == round(base_win * board_multiplier, 1)
    event = {
        "index": len(game_state.book.events),
        "type": BOARD_MULT_INFO,
        "multInfo": multiplier_info,
        "winInfo": winInfo,
    }
    game_state.book.add_event(event)
