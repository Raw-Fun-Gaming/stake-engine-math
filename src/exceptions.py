"""Custom exception classes for the slot game engine.

This module defines a hierarchy of exceptions specific to the game engine,
providing clearer error messages and better error handling than generic
Python exceptions.

Example:
    >>> from src.exceptions import GameConfigError
    >>> if not config.paytable:
    ...     raise GameConfigError("Paytable is required for win calculations")
"""

from __future__ import annotations

__all__ = [
    "GameEngineError",
    "GameConfigError",
    "ReelStripError",
    "WinCalculationError",
    "SimulationError",
    "BoardGenerationError",
    "EventError",
    "OptimizationError",
]


class GameEngineError(Exception):
    """Base exception for all game engine errors.

    All custom exceptions in the game engine inherit from this class,
    making it easy to catch all engine-specific errors.

    Example:
        >>> try:
        ...     game_state.run_spin(0)
        ... except GameEngineError as e:
        ...     print(f"Game engine error: {e}")
    """

    pass


class GameConfigError(GameEngineError):
    """Raised when game configuration is invalid or incomplete.

    This exception indicates issues with:
    - Missing required configuration fields
    - Invalid paytable definitions
    - Incorrect reel strip references
    - Malformed betmode configurations
    - Invalid RTP or wincap settings

    Example:
        >>> if not self.config.paytable:
        ...     raise GameConfigError(
        ...         f"Game '{self.config.game_id}' missing paytable definition. "
        ...         "Please define paytable in game_config.py"
        ...     )
    """

    pass


class ReelStripError(GameEngineError):
    """Raised when reel strip files are missing, malformed, or invalid.

    This exception indicates issues with:
    - Missing reel strip CSV files
    - Invalid CSV format
    - Empty or malformed reel strips
    - Mismatched reel lengths
    - Unknown symbols in reel strips

    Example:
        >>> if not reel_file.exists():
        ...     raise ReelStripError(
        ...         f"Reel strip file not found: {reel_file}. "
        ...         f"Expected in games/{game_id}/reels/"
        ...     )
    """

    pass


class WinCalculationError(GameEngineError):
    """Raised when win calculation fails or produces invalid results.

    This exception indicates issues with:
    - Invalid win type (cluster/lines/ways/scatter)
    - Missing paytable entries
    - Negative win amounts
    - Win calculation logic errors
    - Multiplier calculation failures

    Example:
        >>> if win_amount < 0:
        ...     raise WinCalculationError(
        ...         f"Win calculation produced negative amount: {win_amount}. "
        ...         f"Check paytable and multiplier logic."
        ...     )
    """

    pass


class SimulationError(GameEngineError):
    """Raised when simulation fails or encounters invalid state.

    This exception indicates issues with:
    - Infinite loops in game logic
    - Invalid simulation parameters
    - Repeat condition failures
    - State corruption
    - RNG seeding errors

    Example:
        >>> if repeat_count > MAX_REPEATS:
        ...     raise SimulationError(
        ...         f"Simulation stuck in repeat loop after {repeat_count} attempts. "
        ...         f"Check repeat conditions and win criteria."
        ...     )
    """

    pass


class BoardGenerationError(GameEngineError):
    """Raised when board generation fails.

    This exception indicates issues with:
    - Invalid board dimensions
    - Empty reel strips
    - Symbol generation failures
    - Force file conflicts
    - Anticipation logic errors

    Example:
        >>> if not self.board or len(self.board) == 0:
        ...     raise BoardGenerationError(
        ...         "Board generation produced empty board. "
        ...         "Check reel strips and generation logic."
        ...     )
    """

    pass


class EventError(GameEngineError):
    """Raised when event recording or emission fails.

    This exception indicates issues with:
    - Invalid event types
    - Missing required event fields
    - Event format errors
    - Book recording failures
    - Event constant mismatches

    Example:
        >>> if event_type not in EventConstants:
        ...     raise EventError(
        ...         f"Unknown event type: {event_type}. "
        ...         f"Use EventConstants for valid event types."
        ...     )
    """

    pass


class OptimizationError(GameEngineError):
    """Raised when optimization process fails.

    This exception indicates issues with:
    - Invalid optimization parameters
    - Rust optimization binary errors
    - Setup file generation failures
    - RTP calculation errors
    - Convergence failures

    Example:
        >>> if target_rtp < MIN_RTP or target_rtp > MAX_RTP:
        ...     raise OptimizationError(
        ...         f"Target RTP {target_rtp} out of valid range [{MIN_RTP}, {MAX_RTP}]. "
        ...         f"Adjust optimization parameters."
        ...     )
    """

    pass
