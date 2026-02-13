"""Single class containing all reuseable event `type` constants."""

from enum import Enum


class EventConstants(Enum):
    """Define all standard event 'type' keys."""

    # Reveal events
    REVEAL = "reveal"

    # Win events
    WIN = "win"
    SET_FINAL_WIN = "setFinalWin"
    SET_WIN = "setWin"
    SET_TOTAL_WIN = "setTotalWin"
    WIN_CAP = "winCap"

    # Free spins events
    UPDATE_FREE_SPINS = "updateFreeSpins"
    TRIGGER_FREE_SPINS = "triggerFreeSpins"
    RETRIGGER_FREE_SPINS = "retriggerFreeSpins"
    END_FREE_SPINS = "endFreeSpins"

    # Tumble events
    TUMBLE = "tumble"
    SET_TUMBLE_WIN = "setTumbleWin"
    UPDATE_TUMBLE_WIN = "updateTumbleWin"

    # Special symbol events
    UPDATE_GLOBAL_MULTIPLIER = "updateGlobalMultiplier"
    UPDATE_BOARD_MULTIPLIER = "updateBoardMultiplier"
    UPGRADE = "upgrade"
    REVEAL_EXPANDING_WILDS = "revealExpandingWilds"
    UPDATE_EXPANDING_WILDS = "updateExpandingWilds"
    ADD_STICKY_SYMBOLS = "addStickySymbols"
