from copy import deepcopy

APPLY_TUMBLE_MULTIPLIER = "applyMultiplierToTumble"
UPDATE_GRID = "updateGrid"


def update_grid_multiplier_event(game_state):
    """Pass updated position multipliers after a win."""
    event = {
        "index": len(game_state.book.events),
        "type": UPDATE_GRID,
        "gridMultipliers": deepcopy(game_state.position_multipliers),
    }
    game_state.book.add_event(event)
