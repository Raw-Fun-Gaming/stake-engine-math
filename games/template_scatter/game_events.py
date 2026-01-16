from src.events.event_constants import EventConstants


def send_multiplier_info_event(
    game_state,
    board_multiplier: int,
    multiplier_info: dict,
    base_win: float,
    updated_win: float,
):
    multiplier_info_formatted, win_info_formatted = {}, {}
    multiplier_info_formatted["positions"] = []
    if game_state.config.include_padding:
        for m in range(len(multiplier_info)):
            multiplier_info_formatted["positions"].append(
                {
                    "reel": multiplier_info[m]["reel"],
                    "row": multiplier_info[m]["row"] + 1,
                    "multiplier": multiplier_info[m]["value"],
                }
            )
    else:
        for m in range(len(multiplier_info)):
            multiplier_info_formatted["positions"].append(
                {
                    "reel": multiplier_info[m]["reel"],
                    "row": multiplier_info[m]["row"],
                    "multiplier": multiplier_info[m]["value"],
                }
            )

    win_info_formatted["tumbleWin"] = int(
        round(min(base_win, game_state.config.win_cap) * 100)
    )
    win_info_formatted["boardMultiplier"] = board_multiplier
    win_info_formatted["totalWin"] = int(
        round(min(updated_win, game_state.config.win_cap) * 100)
    )

    assert round(updated_win, 1) == round(base_win * board_multiplier, 1)
    event = {
        "index": len(game_state.book.events),
        "type": EventConstants.UPDATE_BOARD_MULTIPLIER.value,
        "multiplier": multiplier_info_formatted,
        "win": win_info_formatted,
    }
    game_state.book.add_event(event)
