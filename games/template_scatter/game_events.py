def send_multiplier_info_event(
    game_state,
    board_multiplier: int,
    multiplier_info: dict,
    base_win: float,
    updated_win: float,
):
    mult_info, win_info = {}, {}
    mult_info["positions"] = []
    if game_state.config.include_padding:
        for m in range(len(multiplier_info)):
            mult_info["positions"].append(
                {
                    "reel": multiplier_info[m]["reel"],
                    "row": multiplier_info[m]["row"] + 1,
                    "multiplier": multiplier_info[m]["value"],
                }
            )
    else:
        for m in range(len(multiplier_info)):
            mult_info["positions"].append(
                {
                    "reel": multiplier_info[m]["reel"],
                    "row": multiplier_info[m]["row"],
                    "multiplier": multiplier_info[m]["value"],
                }
            )

    win_info["tumbleWin"] = int(round(min(base_win, game_state.config.win_cap) * 100))
    win_info["boardMult"] = board_multiplier
    win_info["totalWin"] = int(round(min(updated_win, game_state.config.win_cap) * 100))

    assert round(updated_win, 1) == round(base_win * board_multiplier, 1)
    # Game-specific event type for board multiplier information
    event = {
        "index": len(game_state.book.events),
        "type": "boardMultiplierInfo",
        "multInfo": mult_info,
        "winInfo": win_info,
    }
    game_state.book.add_event(event)
