from copy import deepcopy


def update_grid_multiplier_event(game_state):
    """Pass updated position multipliers after a win."""
    # Game-specific event type for cluster game with position multipliers
    event = {
        "index": len(game_state.book.events),
        "type": "updateGrid",
        "gridMultipliers": deepcopy(game_state.position_multipliers),
    }
    game_state.book.add_event(event)
