"""Output formatting for game simulation results.

This module provides the OutputFormatter class for controlling how simulation
results are serialized to books files. Supports both compact (space-efficient)
and verbose (human-readable) output modes.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.calculations.symbol import Symbol


class OutputMode(Enum):
    """Output format modes for simulation results.

    Attributes:
        COMPACT: Space-efficient format (symbols as strings, positions as arrays)
        VERBOSE: Human-readable format (symbols as objects, positions as objects)
    """

    COMPACT = "compact"
    VERBOSE = "verbose"


class OutputFormatter:
    """Formatter for simulation output with configurable compression options.

    Controls how symbols, positions, events, and boards are serialized to
    books files. Supports both compact (space-efficient) and verbose
    (human-readable) output modes.

    Attributes:
        output_mode: Format mode (compact or verbose)
        include_losing_boards: Whether to include board reveals for 0-win spins
        compress_positions: Whether to use array format for positions
        compress_symbols: Whether to use string format for symbols
        skip_implicit_events: Whether to skip redundant/implicit events

    Examples:
        >>> # Compact mode - minimal file size
        >>> formatter = OutputFormatter(output_mode=OutputMode.COMPACT)
        >>> symbol_dict = formatter.format_symbol(my_symbol, [])
        >>> # Returns: "L5" (string)

        >>> # Verbose mode - human readable
        >>> formatter = OutputFormatter(output_mode=OutputMode.VERBOSE)
        >>> symbol_dict = formatter.format_symbol(my_symbol, [])
        >>> # Returns: {"name": "L5"} (object)
    """

    def __init__(
        self,
        output_mode: OutputMode = OutputMode.VERBOSE,
        include_losing_boards: bool = True,
        compress_positions: bool = False,
        compress_symbols: bool = False,
        skip_implicit_events: bool = False,
    ) -> None:
        """Initialize output formatter with configuration options.

        Args:
            output_mode: Format mode (compact or verbose), defaults to verbose
            include_losing_boards: Include board reveals for 0-win spins, defaults to True
            compress_positions: Use [reel, row] instead of {reel, row}, defaults to False
            compress_symbols: Use "L5" instead of {"name": "L5"}, defaults to False
            skip_implicit_events: Skip redundant events that can be inferred, defaults to False
        """
        self.output_mode = output_mode
        self.include_losing_boards = include_losing_boards
        self.compress_positions = (
            compress_positions if output_mode == OutputMode.COMPACT else False
        )
        self.compress_symbols = (
            compress_symbols if output_mode == OutputMode.COMPACT else False
        )
        self.skip_implicit_events = skip_implicit_events

        # Auto-enable compression in compact mode
        if output_mode == OutputMode.COMPACT:
            self.compress_positions = True
            self.compress_symbols = True

    def format_symbol(
        self,
        symbol: Symbol,
        special_attributes: list[str],
    ) -> str | dict[str, Any]:
        """Format a symbol for output.

        Args:
            symbol: Symbol object to format
            special_attributes: List of special attribute names to include

        Returns:
            Compact mode: Symbol name as string (e.g., "L5")
            Verbose mode: Dictionary with name and attributes (e.g., {"name": "L5"})

        Examples:
            >>> formatter = OutputFormatter(OutputMode.COMPACT)
            >>> formatter.format_symbol(symbol, [])
            "L5"

            >>> formatter = OutputFormatter(OutputMode.VERBOSE)
            >>> formatter.format_symbol(symbol, ["multiplier"])
            {"name": "L5", "multiplier": 2}
        """
        if self.compress_symbols:
            # Compact format: just the symbol name
            # If symbol has special attributes, we still need to include them
            if special_attributes:
                has_special = False
                for attr in special_attributes:
                    if (
                        hasattr(symbol, attr)
                        and symbol.get_attribute(attr) is not False
                    ):
                        has_special = True
                        break

                if has_special:
                    # Symbol has special attributes, use object format
                    return self._format_symbol_verbose(symbol, special_attributes)

            # Simple symbol with no special attributes
            return symbol.name
        else:
            # Verbose format: full object
            return self._format_symbol_verbose(symbol, special_attributes)

    def _format_symbol_verbose(
        self,
        symbol: Symbol,
        special_attributes: list[str],
    ) -> dict[str, Any]:
        """Format symbol in verbose mode with all attributes.

        Args:
            symbol: Symbol object to format
            special_attributes: List of special attribute names to include

        Returns:
            Dictionary with symbol name and any special attributes
        """
        result: dict[str, Any] = {"name": symbol.name}

        # Add special attributes if present
        attrs = vars(symbol)
        for key, val in attrs.items():
            if key in special_attributes and symbol.get_attribute(key) is not False:
                result[key] = val

        return result

    def format_position(self, reel: int, row: int) -> list[int] | dict[str, int]:
        """Format a board position for output.

        Args:
            reel: Reel index (0-based)
            row: Row index (0-based)

        Returns:
            Compact mode: Array [reel, row]
            Verbose mode: Object {"reel": reel, "row": row}

        Examples:
            >>> formatter = OutputFormatter(OutputMode.COMPACT)
            >>> formatter.format_position(0, 2)
            [0, 2]

            >>> formatter = OutputFormatter(OutputMode.VERBOSE)
            >>> formatter.format_position(0, 2)
            {"reel": 0, "row": 2}
        """
        if self.compress_positions:
            return [reel, row]
        else:
            return {"reel": reel, "row": row}

    def format_position_list(
        self,
        positions: list[dict[str, int]],
    ) -> list[list[int]] | list[dict[str, int]]:
        """Format a list of positions for output.

        Args:
            positions: List of position dictionaries with "reel" and "row" keys

        Returns:
            List of formatted positions (arrays or objects depending on mode)

        Examples:
            >>> formatter = OutputFormatter(OutputMode.COMPACT)
            >>> positions = [{"reel": 0, "row": 1}, {"reel": 2, "row": 3}]
            >>> formatter.format_position_list(positions)
            [[0, 1], [2, 3]]
        """
        return [self.format_position(pos["reel"], pos["row"]) for pos in positions]

    def should_include_board_reveal(self, final_win: float) -> bool:
        """Determine if board reveal event should be included.

        Args:
            final_win: Final win amount for the spin

        Returns:
            True if board reveal should be included, False otherwise

        Examples:
            >>> formatter = OutputFormatter(include_losing_boards=False)
            >>> formatter.should_include_board_reveal(0.0)
            False

            >>> formatter.should_include_board_reveal(10.5)
            True
        """
        if self.include_losing_boards:
            return True

        # Skip board reveal for losing spins (0 win)
        return final_win > 0

    def should_include_event(self, event_type: str, event_data: dict[str, Any]) -> bool:
        """Determine if an event should be included in output.

        Args:
            event_type: Type of event (e.g., "reveal", "win", "setFinalWin")
            event_data: Event data dictionary

        Returns:
            True if event should be included, False if it can be skipped

        Examples:
            >>> formatter = OutputFormatter(skip_implicit_events=True)
            >>> formatter.should_include_event("setFinalWin", {"amount": 0})
            False  # Implicit - can be inferred from payout_multiplier

            >>> formatter.should_include_event("win", {"amount": 10})
            True  # Actual win, must be included
        """
        if not self.skip_implicit_events:
            return True

        # Skip implicit events based on type and data
        if event_type == "setFinalWin" and event_data.get("amount", 0) == 0:
            # Zero final win is implicit
            return False

        # Add more implicit event detection logic here as needed

        return True

    def format_board(
        self,
        board: list[list[Symbol]],
        special_attributes: list[str],
    ) -> list[list[str | dict[str, Any]]]:
        """Format a board (2D grid of symbols) for output.

        Args:
            board: 2D list of Symbol objects
            special_attributes: List of special attribute names to include

        Returns:
            2D list of formatted symbols (strings or objects depending on mode)

        Examples:
            >>> formatter = OutputFormatter(OutputMode.COMPACT)
            >>> formatted = formatter.format_board(board, [])
            >>> # Returns: [["L5", "H1", ...], ["L3", "H2", ...], ...]
        """
        formatted_board: list[list[str | dict[str, Any]]] = []

        for reel in board:
            formatted_reel: list[str | dict[str, Any]] = []
            for symbol in reel:
                formatted_reel.append(self.format_symbol(symbol, special_attributes))
            formatted_board.append(formatted_reel)

        return formatted_board

    def get_format_version(self) -> str:
        """Get the format version identifier for books files.

        Returns:
            Format version string (e.g., "2.0-compact" or "2.0-verbose")

        Examples:
            >>> formatter = OutputFormatter(OutputMode.COMPACT)
            >>> formatter.get_format_version()
            "2.0-compact"
        """
        return f"2.0-{self.output_mode.value}"
