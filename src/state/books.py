"""Handles independent simulation events and details.

This module defines the Book class which stores all events and results
for a single simulation round (spin).
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.output.output_formatter import OutputFormatter


class Book:
    """Stores simulation information for a single spin.

    Tracks all events that occur during a spin, including wins, free spin
    triggers, special symbol activations, etc.

    Attributes:
        id: Unique identifier for this simulation
        payout_multiplier: Final payout multiplier for this spin
        events: List of all events that occurred during the spin
        criteria: Simulation criteria/mode (e.g., "base", "bonus")
        basegame_wins: Total wins from base game
        freegame_wins: Total wins from free spins
    """

    def __init__(self, book_id: int, criteria: str, formatter: OutputFormatter | None = None) -> None:
        """Initialize simulation book.

        Args:
            book_id: Unique identifier for this simulation
            criteria: Simulation criteria/mode
            formatter: Optional OutputFormatter for format versioning
        """
        self.id: int = book_id
        self.payout_multiplier: float = 0.0
        self.events: list[dict[str, Any]] = []
        self.criteria: str = criteria
        self.basegame_wins: float = 0.0
        self.freegame_wins: float = 0.0
        self.formatter: OutputFormatter | None = formatter

    def add_event(self, event: dict[str, Any]) -> None:
        """Append event to book.

        Args:
            event: Event dictionary to add to the book
        """
        self.events.append(deepcopy(event))

    def append_book_items(self, event_id: int, appended_info: dict[str, Any]) -> None:
        """Modify an existing book event at position 'event_id'.

        Args:
            event_id: Index of event to modify
            appended_info: Dictionary of fields to add/update in the event
        """
        for k, v in appended_info.items():
            self.events[event_id][k] = v

    def to_json(self) -> dict[str, Any]:
        """Return JSON-ready object.

        Converts the book to a dictionary suitable for JSON serialization,
        with standardized field names for the RGS.

        Returns:
            Dictionary with id, payoutMultiplier, events, criteria, win totals,
            and format version (if formatter is set)
        """
        json_book: dict[str, Any] = {
            "id": self.id,
            "payoutMultiplier": int(round(self.payout_multiplier * 100, 0)),
            "events": self.events,
            "criteria": self.criteria,
            "baseGameWins": self.basegame_wins,
            "freeGameWins": self.freegame_wins,
        }

        # Add format version if formatter is available
        if self.formatter:
            json_book["formatVersion"] = self.formatter.get_format_version()

        return json_book
