"""Type aliases and common types used throughout the SDK.

This module defines type aliases to improve code readability and type safety.
"""

from typing import TYPE_CHECKING, Any, TypeAlias, Union

if TYPE_CHECKING:
    from src.calculations.symbol import Symbol

# Symbol representation
SymbolName: TypeAlias = str

# Board representation - 2D array of symbols
# Board[reel][row] = Symbol
# Using Any instead of Symbol to avoid circular imports at runtime
Board: TypeAlias = list[list[Any]]

# Position on the board (reel_index, row_index)
Position: TypeAlias = tuple[int, int]

# List of positions
PositionList: TypeAlias = list[Position]

# Distribution - mapping from outcome to weight/probability
Distribution: TypeAlias = dict[Union[str, int, float], float]

# Win details dictionary
WinDetails: TypeAlias = dict[
    str, Union[str, int, float, list[Position], list[dict[str, int]]]
]

# Event dictionary
Event: TypeAlias = dict[str, Union[str, int, float, list, dict]]

# Game mode types
GameModeType: TypeAlias = str  # Will become enum later

# Simulation ID
SimulationID: TypeAlias = int

# RTP value (0.0 to 1.0)
RTP: TypeAlias = float

# Win amount/multiplier
WinAmount: TypeAlias = float

# Bet amount
BetAmount: TypeAlias = float
