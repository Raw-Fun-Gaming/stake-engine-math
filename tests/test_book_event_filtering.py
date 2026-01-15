"""Tests for Book class integration with EventFilter."""

from src.config.config import Config
from src.events.event_constants import EventConstants
from src.events.event_filter import EventFilter
from src.state.books import Book


class TestBookEventFiltering:
    """Test Book class with EventFilter integration."""

    def test_book_without_filter_adds_all_events(self):
        """Test that Book without filter adds all events."""
        book = Book(book_id=1, criteria="base")

        # Add events of various types
        book.add_event({"type": EventConstants.WIN.value, "amount": 10})
        book.add_event({"type": EventConstants.SET_WIN.value, "amount": 10})
        book.add_event(
            {"type": EventConstants.UPDATE_FREE_SPINS.value, "remaining": 5}
        )

        assert len(book.events) == 3

    def test_book_with_filter_respects_filtering(self):
        """Test that Book with filter applies filtering logic."""
        config = Config()
        config.skip_derived_wins = True  # Skip SET_WIN, SET_TOTAL_WIN

        event_filter = EventFilter(config)
        book = Book(book_id=1, criteria="base", event_filter=event_filter)

        # Add events - WIN should be included, SET_WIN should be filtered
        book.add_event({"type": EventConstants.WIN.value, "amount": 10})
        book.add_event({"type": EventConstants.SET_WIN.value, "amount": 10})
        book.add_event({"type": EventConstants.REVEAL.value, "board": []})

        # Only WIN and REVEAL should be added (SET_WIN is filtered)
        assert len(book.events) == 2
        assert book.events[0]["type"] == EventConstants.WIN.value
        assert book.events[1]["type"] == EventConstants.REVEAL.value

    def test_book_filter_progress_updates(self):
        """Test filtering progress update events."""
        config = Config()
        config.skip_progress_updates = True

        event_filter = EventFilter(config)
        book = Book(book_id=1, criteria="base", event_filter=event_filter)

        # Add events
        book.add_event({"type": EventConstants.WIN.value, "amount": 10})
        book.add_event(
            {"type": EventConstants.UPDATE_FREE_SPINS.value, "remaining": 5}
        )
        book.add_event(
            {"type": EventConstants.UPDATE_TUMBLE_WIN.value, "amount": 10}
        )
        book.add_event({"type": EventConstants.TRIGGER_FREE_SPINS.value, "count": 10})

        # Only WIN and TRIGGER_FREE_SPINS should be added (updates are filtered)
        assert len(book.events) == 2
        assert book.events[0]["type"] == EventConstants.WIN.value
        assert book.events[1]["type"] == EventConstants.TRIGGER_FREE_SPINS.value

    def test_book_filter_verbosity_minimal(self):
        """Test minimal verbosity filtering."""
        config = Config()
        config.verbose_event_level = "minimal"

        event_filter = EventFilter(config)
        book = Book(book_id=1, criteria="base", event_filter=event_filter)

        # Add events of different categories
        book.add_event({"type": EventConstants.WIN.value, "amount": 10})  # REQUIRED
        book.add_event(
            {"type": EventConstants.SET_WIN.value, "amount": 10}
        )  # STANDARD
        book.add_event(
            {"type": EventConstants.UPDATE_FREE_SPINS.value, "remaining": 5}
        )  # VERBOSE

        # Only REQUIRED event should be added
        assert len(book.events) == 1
        assert book.events[0]["type"] == EventConstants.WIN.value

    def test_book_filter_verbosity_standard(self):
        """Test standard verbosity filtering."""
        config = Config()
        config.verbose_event_level = "standard"

        event_filter = EventFilter(config)
        book = Book(book_id=1, criteria="base", event_filter=event_filter)

        # Add events of different categories
        book.add_event({"type": EventConstants.WIN.value, "amount": 10})  # REQUIRED
        book.add_event(
            {"type": EventConstants.SET_WIN.value, "amount": 10}
        )  # STANDARD
        book.add_event(
            {"type": EventConstants.UPDATE_FREE_SPINS.value, "remaining": 5}
        )  # VERBOSE

        # REQUIRED and STANDARD should be added, VERBOSE filtered
        assert len(book.events) == 2
        assert book.events[0]["type"] == EventConstants.WIN.value
        assert book.events[1]["type"] == EventConstants.SET_WIN.value

    def test_book_filter_context_zero_amounts(self):
        """Test context-based filtering of zero amounts.

        Note: REQUIRED events like WIN are always included even with zero amounts.
        Only STANDARD/VERBOSE events with zero amounts are filtered.
        """
        config = Config()
        config.skip_implicit_events = True

        event_filter = EventFilter(config)
        book = Book(book_id=1, criteria="base", event_filter=event_filter)

        # Add events with different amounts
        book.add_event({"type": EventConstants.WIN.value, "amount": 10})
        book.add_event(
            {"type": EventConstants.WIN.value, "amount": 0}
        )  # REQUIRED, always included
        book.add_event(
            {"type": EventConstants.SET_WIN.value, "amount": 0}
        )  # STANDARD, filtered when zero

        # Both WIN events should be added (REQUIRED), SET_WIN with zero filtered
        assert len(book.events) == 2
        assert book.events[0]["type"] == EventConstants.WIN.value
        assert book.events[0]["amount"] == 10
        assert book.events[1]["type"] == EventConstants.WIN.value
        assert book.events[1]["amount"] == 0

    def test_book_filter_combined_filters(self):
        """Test multiple filters working together."""
        config = Config()
        config.skip_derived_wins = True
        config.skip_progress_updates = True
        config.verbose_event_level = "standard"

        event_filter = EventFilter(config)
        book = Book(book_id=1, criteria="base", event_filter=event_filter)

        # Add various events
        book.add_event({"type": EventConstants.WIN.value, "amount": 10})  # Include
        book.add_event(
            {"type": EventConstants.SET_WIN.value, "amount": 10}
        )  # Filtered (derived)
        book.add_event(
            {"type": EventConstants.UPDATE_FREE_SPINS.value, "remaining": 5}
        )  # Filtered (progress)
        book.add_event(
            {"type": EventConstants.REVEAL.value, "board": []}
        )  # Include (required)
        book.add_event(
            {"type": EventConstants.END_FREE_SPINS.value, "win": 50}
        )  # Include (standard)

        # Only WIN, REVEAL, and END_FREE_SPINS should be added
        assert len(book.events) == 3
        assert book.events[0]["type"] == EventConstants.WIN.value
        assert book.events[1]["type"] == EventConstants.REVEAL.value
        assert book.events[2]["type"] == EventConstants.END_FREE_SPINS.value

    def test_book_to_json_includes_filtered_events(self):
        """Test that to_json() returns only filtered events."""
        config = Config()
        config.skip_derived_wins = True

        event_filter = EventFilter(config)
        book = Book(book_id=1, criteria="base", event_filter=event_filter)

        # Add events
        book.add_event({"type": EventConstants.WIN.value, "amount": 10})
        book.add_event({"type": EventConstants.SET_WIN.value, "amount": 10})

        book.payout_multiplier = 0.10

        json_output = book.to_json()

        # JSON should only have 1 event (WIN)
        assert len(json_output["events"]) == 1
        assert json_output["events"][0]["type"] == EventConstants.WIN.value
