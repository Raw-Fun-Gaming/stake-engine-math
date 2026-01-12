"""Constants and enumerations used throughout the slot game engine.

This module defines common constants, enums, and magic numbers to improve code
readability and maintainability. Using these constants instead of hardcoded
strings/numbers makes the codebase more resistant to typos and easier to refactor.

Example:
    >>> from src.constants import GameMode, WinType
    >>> if game_state.game_mode == GameMode.FREE_SPIN:
    ...     calculate_free_spin_wins()
"""

from __future__ import annotations

from enum import Enum

__all__ = [
    "GameMode",
    "WinType",
    "DEFAULT_NUM_REELS",
    "DEFAULT_NUM_ROWS",
    "MAX_FREE_SPINS",
    "DEFAULT_RTP",
    "MAX_REELS",
    "MAX_ROWS_PER_REEL",
]


# =============================================================================
# ENUMERATIONS
# =============================================================================


class GameMode(str, Enum):
    """Game mode types for different phases of gameplay.

    String enum to maintain backward compatibility with existing code that
    compares game modes as strings.

    Attributes:
        BASE: Standard base game mode
        FREE_SPIN: Free spin/bonus game mode
        BONUS: Generic bonus game mode
        SUPER_SPIN: Special superspin/respin mode (e.g., hold-and-spin)
    """

    BASE = "basegame"
    FREE_SPIN = "freegame"
    BONUS = "bonus"
    SUPER_SPIN = "superspin"


class WinType(str, Enum):
    """Win calculation method types.

    String enum to maintain backward compatibility with existing code that
    compares win types as strings.

    Attributes:
        CLUSTER: Cluster-pay (adjacent matching symbols)
        LINES: Line-pay (traditional paylines)
        WAYS: Ways-pay (left-to-right symbol combinations)
        SCATTER: Scatter-pay (symbols anywhere on board)
    """

    CLUSTER = "cluster"
    LINES = "lines"
    WAYS = "ways"
    SCATTER = "scatter"


# =============================================================================
# DEFAULT CONFIGURATION VALUES
# =============================================================================

# Board dimensions
DEFAULT_NUM_REELS: int = 5
"""Default number of reels (columns) on the game board."""

DEFAULT_NUM_ROWS: int = 3
"""Default number of rows on the game board."""

MAX_REELS: int = 10
"""Maximum supported number of reels."""

MAX_ROWS_PER_REEL: int = 10
"""Maximum supported rows per reel."""

# Free spin limits
MAX_FREE_SPINS: int = 100
"""Maximum number of free spins that can be awarded/triggered."""

# RTP (Return To Player)
DEFAULT_RTP: float = 0.96
"""Default return-to-player percentage (96%)."""

MIN_RTP: float = 0.80
"""Minimum acceptable RTP (80%)."""

MAX_RTP: float = 0.99
"""Maximum acceptable RTP (99%)."""

# Win cap
DEFAULT_WIN_CAP_MULTIPLIER: float = 10000.0
"""Default win cap as multiplier of base bet."""

# Simulation
DEFAULT_SIMULATION_COUNT: int = 1000000
"""Default number of simulations to run."""

MIN_SIMULATION_COUNT: int = 1000
"""Minimum number of simulations for statistical validity."""

# Random seed
DEFAULT_SEED_OFFSET: int = 0
"""Default offset for random number generator seeding."""
