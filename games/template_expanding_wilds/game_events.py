"""Events specific to new and updating expanding wild symbols."""

from copy import deepcopy

from src.events.event_constants import EventConstants
from src.events.events import json_ready_sym


def new_expanding_wild_event(game_state) -> None:
    """Passed after reveal event"""
    new_exp_wilds = game_state.new_exp_wilds
    if game_state.config.include_padding:
        for ew in new_exp_wilds:
            ew["row"] += 1

    event = {
        "index": len(game_state.book.events),
        "type": EventConstants.NEW_EXPANDING_WILD.value,
        "newWilds": new_exp_wilds,
    }
    game_state.book.add_event(event)


def update_expanding_wild_event(game_state) -> None:
    """On each reveal - the multiplier value on the expanding wild is updated (sent before reveal)"""
    existing_wild_details = deepcopy(game_state.expanding_wilds)
    wild_event = []
    if game_state.config.include_padding:
        for ew in existing_wild_details:
            if len(ew) > 0:
                ew["row"] += 1
                wild_event.append(ew)

    event = {
        "index": len(game_state.book.events),
        "type": EventConstants.UPDATE_EXPANDING_WILD.value,
        "existingWilds": wild_event,
    }
    game_state.book.add_event(event)


def new_sticky_event(game_state, new_sticky_syms: list):
    """Pass details on new prize symbols"""
    if game_state.config.include_padding:
        for sym in new_sticky_syms:
            sym["row"] += 1
            sym["prize"] = int(sym["prize"] * 100)

    event = {
        "index": len(game_state.book.events),
        "type": EventConstants.NEW_STICKY_SYMBOL.value,
        "newPrizes": new_sticky_syms,
    }
    game_state.book.add_event(event)


def win_info_prize_event(game_state, include_padding_index=True):
    """
    include_padding_index: starts winning-symbol positions at row=1, to account for top/bottom symbol inclusion in board
    """
    win_data_copy = {}
    win_data_copy["wins"] = deepcopy(game_state.win_data["wins"])
    prize_details = []
    for _, w in enumerate(win_data_copy["wins"]):
        if include_padding_index:
            prize_details.append(
                {"reel": w["reel"], "row": w["row"] + 1, "prize": int(100 * w["value"])}
            )
        else:
            prize_details.append(
                {"reel": w["reel"], "row": w["row"], "prize": int(100 * w["value"])}
            )

    # Game-specific event type (not standard EventConstants.WIN)
    # Custom format for prize-based game mode
    event = {
        "index": len(game_state.book.events),
        "type": "prizeWinInfo",
        "totalWin": int(
            round(
                min(game_state.win_data["totalWin"], game_state.config.win_cap) * 100, 0
            )
        ),
        "wins": prize_details,
    }
    game_state.book.add_event(event)


def reveal_prize_event(game_state):
    """Display the initial board drawn from reelstrips."""
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

    for idx, _ in enumerate(board_client):
        for idy, _ in enumerate(board_client[idx]):
            if board_client[idx][idy]["name"] != "X":
                board_client[idx][idy]["prize"] = int(
                    board_client[idx][idy]["prize"] * 100
                )

    event = {
        "index": len(game_state.book.events),
        "type": EventConstants.REVEAL.value,
        "board": board_client,
        "paddingPositions": game_state.reel_positions,
        "gameType": "super_spin",
        "anticipation": game_state.anticipation,
    }
    game_state.book.add_event(event)
