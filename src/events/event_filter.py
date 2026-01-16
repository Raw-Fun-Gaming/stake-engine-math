"""Event filtering system for controlling event emission verbosity.

This module provides the EventFilter class for selective event filtering
based on configuration options, enabling fine-grained control over which
events are included in books output.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from src.config.config import Config

from src.events.event_constants import EventConstants


class EventFilter:
    """Controls which events should be included in books output.

    The EventFilter class provides methods to determine whether specific
    events should be emitted based on configuration settings. It supports
    multiple filtering strategies:
    - Skipping derived/redundant events
    - Skipping progress update events
    - Verbosity level filtering (full/standard/minimal)
    - Custom predicates

    Attributes:
        config: Configuration object with filtering settings
        skip_derived_wins: Whether to skip SET_WIN, SET_TOTAL_WIN events
        skip_progress_updates: Whether to skip UPDATE_FREE_SPINS, UPDATE_TUMBLE_WIN
        verbose_event_level: Event verbosity level ("full", "standard", "minimal")
    """

    # Event categories for verbosity filtering
    REQUIRED_EVENTS = {
        EventConstants.REVEAL.value,
        EventConstants.WIN.value,
        EventConstants.TRIGGER_FREE_SPINS.value,
        EventConstants.RETRIGGER_FREE_SPINS.value,
        EventConstants.TUMBLE_BOARD.value,
        EventConstants.UPDATE_GLOBAL_MULTIPLIER.value,
        EventConstants.UPGRADE.value,
        EventConstants.REVEAL_EXPANDING_WILDS.value,
        EventConstants.UPDATE_EXPANDING_WILDS.value,
        EventConstants.ADD_STICKY_SYMBOLS.value,
        # SET_FINAL_WIN moved to STANDARD (contextually required)
    }

    STANDARD_EVENTS = {
        EventConstants.SET_WIN.value,
        EventConstants.SET_TOTAL_WIN.value,
        EventConstants.WIN_CAP.value,
        EventConstants.END_FREE_SPINS.value,
        EventConstants.SET_FINAL_WIN.value,  # Required only when win cap applied
    }

    VERBOSE_EVENTS = {
        EventConstants.UPDATE_FREE_SPINS.value,
        EventConstants.UPDATE_TUMBLE_WIN.value,
        EventConstants.SET_TUMBLE_WIN.value,
    }

    def __init__(self, config: Config) -> None:
        """Initialize event filter with configuration.

        Args:
            config: Game configuration with filtering settings
        """
        self.config = config
        self.skip_derived_wins = config.skip_derived_wins
        self.skip_progress_updates = config.skip_progress_updates
        self.verbose_event_level = config.verbose_event_level

    def should_include_event(
        self, event_type: str, event_data: dict[str, Any] | None = None
    ) -> bool:
        """Determine if an event should be included in output.

        Args:
            event_type: Event type constant (e.g., EventConstants.WIN.value)
            event_data: Optional event data for context-based filtering

        Returns:
            True if event should be included, False otherwise

        Examples:
            >>> filter = EventFilter(config)
            >>> filter.should_include_event(EventConstants.WIN.value)
            True
            >>> filter.should_include_event(EventConstants.SET_WIN.value)
            False  # if skip_derived_wins=True
        """
        # Always include required events
        if event_type in self.REQUIRED_EVENTS:
            return True

        # Check derived wins filtering
        if self.skip_derived_wins and self._is_derived_win_event(event_type):
            return False

        # Check progress updates filtering
        if self.skip_progress_updates and self._is_progress_update_event(event_type):
            return False

        # Check verbosity level
        if not self._passes_verbosity_filter(event_type):
            return False

        # Context-based filtering (if event_data provided)
        if event_data is not None:
            if not self._passes_context_filter(event_type, event_data):
                return False

        return True

    def _is_derived_win_event(self, event_type: str) -> bool:
        """Check if event is a derived win event (can be calculated from WIN events).

        Args:
            event_type: Event type constant

        Returns:
            True if event is derived win (SET_WIN, SET_TOTAL_WIN)
        """
        return event_type in {
            EventConstants.SET_WIN.value,
            EventConstants.SET_TOTAL_WIN.value,
        }

    def _is_progress_update_event(self, event_type: str) -> bool:
        """Check if event is a progress update event.

        Args:
            event_type: Event type constant

        Returns:
            True if event is progress update (UPDATE_FREE_SPINS, UPDATE_TUMBLE_WIN)
        """
        return event_type in {
            EventConstants.UPDATE_FREE_SPINS.value,
            EventConstants.UPDATE_TUMBLE_WIN.value,
            EventConstants.SET_TUMBLE_WIN.value,
        }

    def _passes_verbosity_filter(self, event_type: str) -> bool:
        """Check if event passes verbosity level filter.

        Args:
            event_type: Event type constant

        Returns:
            True if event should be included based on verbosity level

        Verbosity Levels:
            - "minimal": Only REQUIRED_EVENTS
            - "standard": REQUIRED_EVENTS + STANDARD_EVENTS
            - "full": All events (REQUIRED + STANDARD + VERBOSE)
        """
        if self.verbose_event_level == "minimal":
            return event_type in self.REQUIRED_EVENTS

        if self.verbose_event_level == "standard":
            return event_type in (self.REQUIRED_EVENTS | self.STANDARD_EVENTS)

        # "full" or any other value: include all events
        return True

    def _passes_context_filter(
        self, event_type: str, event_data: dict[str, Any]
    ) -> bool:
        """Check if event passes context-based filters.

        Args:
            event_type: Event type constant
            event_data: Event data for context

        Returns:
            True if event should be included based on context

        Context Filters:
            - Skip SET_FINAL_WIN if amount equals SET_TOTAL_WIN (no win cap)
            - Skip END_FREE_SPINS if implicit from spin count
            - Skip events with zero amounts if skip_implicit_events=True
        """
        # Skip SET_FINAL_WIN if it's the same as SET_TOTAL_WIN (no cap applied)
        if event_type == EventConstants.SET_FINAL_WIN.value:
            # If win_cap field is missing or False, this is redundant
            if not event_data.get("winCap"):
                return not self.config.skip_implicit_events

        # Skip events with zero amounts if configured
        if self.config.skip_implicit_events:
            amount = event_data.get("amount", 0)
            if isinstance(amount, (int, float)) and amount == 0:
                # Don't skip SET_TUMBLE_WIN with 0 (it's an initializer)
                if event_type != EventConstants.SET_TUMBLE_WIN.value:
                    return False

        return True

    def filter_events(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter a list of events based on configuration.

        Args:
            events: List of event dictionaries with "type" field

        Returns:
            Filtered list of events that should be included

        Examples:
            >>> filter = EventFilter(config)
            >>> events = [
            ...     {"type": "win", "amount": 10},
            ...     {"type": "setWin", "amount": 10},
            ...     {"type": "updateFreeSpins", "remaining": 5}
            ... ]
            >>> filtered = filter.filter_events(events)
            >>> len(filtered)  # May be less if filtering enabled
            2
        """
        filtered = []
        for event in events:
            event_type = event.get("type")
            if event_type and self.should_include_event(event_type, event):
                filtered.append(event)
        return filtered

    def create_custom_filter(
        self, predicate: Callable[[dict[str, Any]], bool]
    ) -> Callable[[list[dict[str, Any]]], list[dict[str, Any]]]:
        """Create a custom event filter with a predicate function.

        Args:
            predicate: Function that takes an event dict and returns True to include

        Returns:
            Filter function that can be applied to event lists

        Examples:
            >>> filter = EventFilter(config)
            >>> # Only include events with amount > 10
            >>> custom_filter = filter.create_custom_filter(
            ...     lambda e: e.get("amount", 0) > 10
            ... )
            >>> filtered = custom_filter(events)
        """

        def custom_filter(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
            return [e for e in events if predicate(e)]

        return custom_filter

    def get_event_category(self, event_type: str) -> str:
        """Get the category of an event type.

        Args:
            event_type: Event type constant

        Returns:
            Category name: "required", "standard", "verbose", or "unknown"

        Examples:
            >>> filter = EventFilter(config)
            >>> filter.get_event_category(EventConstants.WIN.value)
            'required'
            >>> filter.get_event_category(EventConstants.SET_WIN.value)
            'standard'
        """
        if event_type in self.REQUIRED_EVENTS:
            return "required"
        if event_type in self.STANDARD_EVENTS:
            return "standard"
        if event_type in self.VERBOSE_EVENTS:
            return "verbose"
        return "unknown"

    def estimate_reduction(self, total_events: int) -> dict[str, float]:
        """Estimate event count reduction based on current settings.

        Args:
            total_events: Total number of events before filtering

        Returns:
            Dictionary with estimated counts and percentages

        Examples:
            >>> filter = EventFilter(config)
            >>> stats = filter.estimate_reduction(1000)
            >>> print(f"Estimated {stats['percentage_reduced']:.1f}% reduction")
        """
        # Rough estimates based on typical event distribution
        derived_win_ratio = 0.12  # SET_WIN, SET_TOTAL_WIN ~12% of events
        progress_update_ratio = 0.08  # UPDATE_* events ~8% of events
        verbose_ratio = 0.10  # Verbose-only events ~10% of events

        reduction = 0.0

        if self.skip_derived_wins:
            reduction += derived_win_ratio

        if self.skip_progress_updates:
            reduction += progress_update_ratio

        if self.verbose_event_level == "minimal":
            reduction += 0.25  # ~25% are non-required
        elif self.verbose_event_level == "standard":
            reduction += verbose_ratio

        # Cap at reasonable maximum
        reduction = min(reduction, 0.35)  # Max ~35% reduction

        events_reduced = int(total_events * reduction)
        events_remaining = total_events - events_reduced

        return {
            "total_events": total_events,
            "events_remaining": events_remaining,
            "events_reduced": events_reduced,
            "percentage_reduced": reduction * 100,
        }
