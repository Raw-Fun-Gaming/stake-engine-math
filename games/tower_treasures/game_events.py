from copy import deepcopy

from src.events.event_constants import EventConstants


def json_ready_sym(symbol: object, special_attributes: list[str] | None = None):
    """Converts a symbol to dictionary/JSON format."""
    assert special_attributes is not None
    print_sym = {"name": symbol.name}
    attrs = vars(symbol)
    for key, val in attrs.items():
        if key in special_attributes and symbol.get_attribute(key) != False:
            print_sym[key] = val
    return print_sym


def reveal_event(game_state):
    """Display the initial board drawn from reelstrips - Tower Defense custom version without paddingPositions and anticipation."""
    board_client = []
    special_attributes = list(game_state.config.special_symbols.keys())
    for reel, _ in enumerate(game_state.board):
        board_client.append([])
        for row in range(len(game_state.board[reel])):
            board_client[reel].append(
                json_ready_sym(game_state.board[reel][row], special_attributes)
            )

    if game_state.config.include_padding:
        for reel, _ in enumerate(board_client):
            board_client[reel] = [
                json_ready_sym(game_state.top_symbols[reel], special_attributes)
            ] + board_client[reel]
            board_client[reel].append(
                json_ready_sym(game_state.bottom_symbols[reel], special_attributes)
            )

    event = {
        "index": len(game_state.book.events),
        "type": EventConstants.REVEAL.value,
        "board": board_client,
        "gameType": game_state.game_type,
    }
    game_state.book.add_event(event)


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
