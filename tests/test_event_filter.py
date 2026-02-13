"""Tests for EventFilter class."""

from src.config.config import Config
from src.events.event_constants import EventConstants
from src.events.event_filter import EventFilter


class TestEventFilter:
    """Test suite for EventFilter functionality."""

    def test_init_default_values(self):
        """Test EventFilter initialization with default config."""
        config = Config()
        filter = EventFilter(config)

        assert filter.skip_derived_wins is False
        assert filter.skip_progress_updates is False
        assert filter.verbose_event_level == "full"

    def test_init_with_custom_config(self):
        """Test EventFilter initialization with custom config."""
        config = Config()
        config.skip_derived_wins = True
        config.skip_progress_updates = True
        config.verbose_event_level = "minimal"

        filter = EventFilter(config)

        assert filter.skip_derived_wins is True
        assert filter.skip_progress_updates is True
        assert filter.verbose_event_level == "minimal"

    def test_required_events_always_included(self):
        """Test that required events are always included regardless of settings."""
        config = Config()
        config.skip_derived_wins = True
        config.skip_progress_updates = True
        config.verbose_event_level = "minimal"

        filter = EventFilter(config)

        # All required events should be included
        assert filter.should_include_event(EventConstants.REVEAL.value) is True
        assert filter.should_include_event(EventConstants.WIN.value) is True
        assert (
            filter.should_include_event(EventConstants.TRIGGER_FREE_SPINS.value) is True
        )
        assert filter.should_include_event(EventConstants.TUMBLE.value) is True
        assert filter.should_include_event(EventConstants.UPGRADE.value) is True

    def test_skip_derived_wins(self):
        """Test skipping derived win events."""
        config = Config()
        config.skip_derived_wins = True

        filter = EventFilter(config)

        # Derived win events should be skipped
        assert filter.should_include_event(EventConstants.SET_WIN.value) is False
        assert filter.should_include_event(EventConstants.SET_TOTAL_WIN.value) is False

        # But WIN events should still be included (required)
        assert filter.should_include_event(EventConstants.WIN.value) is True

    def test_skip_progress_updates(self):
        """Test skipping progress update events."""
        config = Config()
        config.skip_progress_updates = True

        filter = EventFilter(config)

        # Progress update events should be skipped
        assert (
            filter.should_include_event(EventConstants.UPDATE_FREE_SPINS.value) is False
        )
        assert (
            filter.should_include_event(EventConstants.UPDATE_TUMBLE_WIN.value) is False
        )
        assert filter.should_include_event(EventConstants.SET_TUMBLE_WIN.value) is False

    def test_verbosity_level_minimal(self):
        """Test minimal verbosity level (only required events)."""
        config = Config()
        config.verbose_event_level = "minimal"

        filter = EventFilter(config)

        # Required events included
        assert filter.should_include_event(EventConstants.WIN.value) is True
        assert filter.should_include_event(EventConstants.REVEAL.value) is True

        # Standard events excluded
        assert filter.should_include_event(EventConstants.SET_WIN.value) is False
        assert filter.should_include_event(EventConstants.END_FREE_SPINS.value) is False

        # Verbose events excluded
        assert (
            filter.should_include_event(EventConstants.UPDATE_FREE_SPINS.value) is False
        )

    def test_verbosity_level_standard(self):
        """Test standard verbosity level (required + standard events)."""
        config = Config()
        config.verbose_event_level = "standard"

        filter = EventFilter(config)

        # Required events included
        assert filter.should_include_event(EventConstants.WIN.value) is True

        # Standard events included
        assert filter.should_include_event(EventConstants.SET_WIN.value) is True
        assert filter.should_include_event(EventConstants.END_FREE_SPINS.value) is True

        # Verbose events excluded
        assert (
            filter.should_include_event(EventConstants.UPDATE_FREE_SPINS.value) is False
        )

    def test_verbosity_level_full(self):
        """Test full verbosity level (all events)."""
        config = Config()
        config.verbose_event_level = "full"

        filter = EventFilter(config)

        # All event types should be included
        assert filter.should_include_event(EventConstants.WIN.value) is True
        assert filter.should_include_event(EventConstants.SET_WIN.value) is True
        assert (
            filter.should_include_event(EventConstants.UPDATE_FREE_SPINS.value) is True
        )

    def test_context_filter_skip_zero_amounts(self):
        """Test context-based filtering of zero amount events."""
        config = Config()
        config.skip_implicit_events = True

        filter = EventFilter(config)

        # Event with zero amount should be skipped
        event_data = {"amount": 0}
        assert (
            filter.should_include_event(EventConstants.SET_WIN.value, event_data)
            is False
        )

        # Event with non-zero amount should be included
        event_data = {"amount": 10}
        assert (
            filter.should_include_event(EventConstants.SET_WIN.value, event_data)
            is True
        )

    def test_context_filter_final_win_without_cap(self):
        """Test filtering SET_FINAL_WIN when no win cap applied."""
        config = Config()
        config.skip_implicit_events = True

        filter = EventFilter(config)

        # SET_FINAL_WIN without win_cap flag should be skipped
        event_data = {"amount": 100}
        assert (
            filter.should_include_event(EventConstants.SET_FINAL_WIN.value, event_data)
            is False
        )

        # SET_FINAL_WIN with winCap flag should be included
        event_data = {"amount": 100, "winCap": True}
        assert (
            filter.should_include_event(EventConstants.SET_FINAL_WIN.value, event_data)
            is True
        )

    def test_filter_events_list(self):
        """Test filtering a list of events."""
        config = Config()
        config.skip_derived_wins = True

        filter = EventFilter(config)

        events = [
            {"type": EventConstants.WIN.value, "amount": 10},
            {"type": EventConstants.SET_WIN.value, "amount": 10},
            {"type": EventConstants.REVEAL.value, "board": [[]]},
            {"type": EventConstants.SET_TOTAL_WIN.value, "amount": 10},
        ]

        filtered = filter.filter_events(events)

        # Should only include WIN and REVEAL (not derived wins)
        assert len(filtered) == 2
        assert filtered[0]["type"] == EventConstants.WIN.value
        assert filtered[1]["type"] == EventConstants.REVEAL.value

    def test_get_event_category(self):
        """Test event category detection."""
        config = Config()
        filter = EventFilter(config)

        assert filter.get_event_category(EventConstants.WIN.value) == "required"
        assert filter.get_event_category(EventConstants.SET_WIN.value) == "standard"
        assert (
            filter.get_event_category(EventConstants.UPDATE_FREE_SPINS.value)
            == "verbose"
        )
        assert filter.get_event_category("unknown_event") == "unknown"

    def test_estimate_reduction(self):
        """Test event reduction estimation."""
        config = Config()
        config.skip_derived_wins = True
        config.skip_progress_updates = True

        filter = EventFilter(config)

        stats = filter.estimate_reduction(1000)

        assert stats["total_events"] == 1000
        assert stats["events_remaining"] > 0
        assert stats["events_reduced"] > 0
        assert stats["percentage_reduced"] > 0
        assert stats["events_remaining"] + stats["events_reduced"] == 1000

    def test_custom_filter(self):
        """Test custom filter creation."""
        config = Config()
        filter = EventFilter(config)

        # Create custom filter: only include events with amount > 5
        custom = filter.create_custom_filter(lambda e: e.get("amount", 0) > 5)

        events = [
            {"type": "win", "amount": 3},
            {"type": "win", "amount": 10},
            {"type": "win", "amount": 1},
            {"type": "win", "amount": 20},
        ]

        filtered = custom(events)

        assert len(filtered) == 2
        assert filtered[0]["amount"] == 10
        assert filtered[1]["amount"] == 20

    def test_combined_filters(self):
        """Test multiple filters applied together."""
        config = Config()
        config.skip_derived_wins = True
        config.skip_progress_updates = True
        config.verbose_event_level = "standard"

        filter = EventFilter(config)

        # Derived wins excluded
        assert filter.should_include_event(EventConstants.SET_WIN.value) is False

        # Progress updates excluded
        assert (
            filter.should_include_event(EventConstants.UPDATE_FREE_SPINS.value) is False
        )

        # Standard events included
        assert filter.should_include_event(EventConstants.END_FREE_SPINS.value) is True

        # Required events included
        assert filter.should_include_event(EventConstants.WIN.value) is True
