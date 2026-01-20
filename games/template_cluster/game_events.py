from copy import deepcopy


def reveal_board_multipliers_event(game_state):
    """Reveal the current state of board position multipliers after a win.

    Shows the multiplier value at each board position after winning symbols
    have had their multipliers incremented. Used by the frontend to display
    the multiplier grid overlay.
    """
    event = {
        "index": len(game_state.book.events),
        "type": "revealBoardMultipliers",
        "boardMultipliers": deepcopy(game_state.position_multipliers),
    }
    game_state.book.add_event(event)
