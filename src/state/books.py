"""Handles independent simulation events and details.

This module defines the Book class which stores all events and results
for a single simulation round (spin).
"""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.events.event_filter import EventFilter
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
        base_game_wins: Total wins from base game
        free_game_wins: Total wins from free spins
        formatter: Optional OutputFormatter for format versioning
        event_filter: Optional EventFilter for selective event inclusion
    """

    def __init__(
        self,
        book_id: int,
        criteria: str,
        formatter: OutputFormatter | None = None,
        event_filter: EventFilter | None = None,
    ) -> None:
        """Initialize simulation book.

        Args:
            book_id: Unique identifier for this simulation
            criteria: Simulation criteria/mode
            formatter: Optional OutputFormatter for format versioning
            event_filter: Optional EventFilter for selective event emission
        """
        self.id: int = book_id
        self.payout_multiplier: float = 0.0
        self.events: list[dict[str, Any]] = []
        self.criteria: str = criteria
        self.base_game_wins: float = 0.0
        self.free_game_wins: float = 0.0
        self.formatter: OutputFormatter | None = formatter
        self.event_filter: EventFilter | None = event_filter

    def add_event(self, event: dict[str, Any]) -> None:
        """Append event to book if it passes filtering.

        Args:
            event: Event dictionary to add to the book

        Note:
            If an EventFilter is configured, the event will only be added
            if it passes the filter's should_include_event() check.
        """
        # Apply event filtering if filter is configured
        if self.event_filter is not None:
            event_type = event.get("type")
            if event_type and not self.event_filter.should_include_event(
                event_type, event
            ):
                return  # Skip this event

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
            Dictionary with id, payout_multiplier, events, criteria, win totals,
            and format version (if formatter is set)
        """
        json_book: dict[str, Any] = {
            "id": self.id,
            "payoutMultiplier": int(round(self.payout_multiplier * 100, 0)),
            "events": self.events,
            "criteria": self.criteria,
            "baseGameWins": self.base_game_wins,
            "freeGameWins": self.free_game_wins,
        }

        # Add format version if formatter is available
        if self.formatter:
            json_book["format_version"] = self.formatter.get_format_version()

        return json_book
