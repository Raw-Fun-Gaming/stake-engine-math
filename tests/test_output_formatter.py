"""Unit tests for OutputFormatter class."""

import pytest
from unittest.mock import Mock

from src.output.output_formatter import OutputFormatter, OutputMode


@pytest.fixture
def mock_symbol():
    """Create a mock symbol for testing."""
    symbol = Mock()
    symbol.name = "L5"
    symbol.get_attribute = Mock(return_value=False)
    return symbol


@pytest.fixture
def mock_symbol_with_multiplier():
    """Create a mock symbol with multiplier attribute."""
    symbol = Mock()
    symbol.name = "M"
    symbol.multiplier = 2
    symbol.get_attribute = Mock(side_effect=lambda attr: 2 if attr == "multiplier" else False)
    return symbol


class TestOutputFormatter:
    """Test suite for OutputFormatter class."""

    def test_init_default_values(self):
        """Test OutputFormatter initialization with default values."""
        formatter = OutputFormatter()

        assert formatter.output_mode == OutputMode.VERBOSE
        assert formatter.include_losing_boards is True
        assert formatter.compress_positions is False
        assert formatter.compress_symbols is False
        assert formatter.skip_implicit_events is False

    def test_init_compact_mode_enables_compression(self):
        """Test that compact mode automatically enables compression."""
        formatter = OutputFormatter(output_mode=OutputMode.COMPACT)

        assert formatter.output_mode == OutputMode.COMPACT
        assert formatter.compress_positions is True
        assert formatter.compress_symbols is True

    def test_format_symbol_compact_simple(self, mock_symbol):
        """Test compact symbol formatting without special attributes."""
        formatter = OutputFormatter(output_mode=OutputMode.COMPACT)

        result = formatter.format_symbol(mock_symbol, [])

        assert result == "L5"
        assert isinstance(result, str)

    def test_format_symbol_compact_with_attributes(self, mock_symbol_with_multiplier):
        """Test compact symbol formatting with special attributes."""
        formatter = OutputFormatter(output_mode=OutputMode.COMPACT)

        result = formatter.format_symbol(mock_symbol_with_multiplier, ["multiplier"])

        # Symbol with special attributes uses verbose format even in compact mode
        assert isinstance(result, dict)
        assert result["name"] == "M"
        assert result["multiplier"] == 2

    def test_format_symbol_verbose(self, mock_symbol):
        """Test verbose symbol formatting."""
        formatter = OutputFormatter(output_mode=OutputMode.VERBOSE)

        result = formatter.format_symbol(mock_symbol, [])

        assert isinstance(result, dict)
        assert result["name"] == "L5"

    def test_format_position_compact(self):
        """Test compact position formatting."""
        formatter = OutputFormatter(output_mode=OutputMode.COMPACT)

        result = formatter.format_position(0, 2)

        assert result == [0, 2]
        assert isinstance(result, list)

    def test_format_position_verbose(self):
        """Test verbose position formatting."""
        formatter = OutputFormatter(output_mode=OutputMode.VERBOSE)

        result = formatter.format_position(0, 2)

        assert isinstance(result, dict)
        assert result["reel"] == 0
        assert result["row"] == 2

    def test_format_position_list_compact(self):
        """Test compact position list formatting."""
        formatter = OutputFormatter(output_mode=OutputMode.COMPACT)
        positions = [
            {"reel": 0, "row": 1},
            {"reel": 2, "row": 3},
            {"reel": 4, "row": 0},
        ]

        result = formatter.format_position_list(positions)

        assert result == [[0, 1], [2, 3], [4, 0]]

    def test_format_position_list_verbose(self):
        """Test verbose position list formatting."""
        formatter = OutputFormatter(output_mode=OutputMode.VERBOSE)
        positions = [
            {"reel": 0, "row": 1},
            {"reel": 2, "row": 3},
        ]

        result = formatter.format_position_list(positions)

        assert len(result) == 2
        assert result[0] == {"reel": 0, "row": 1}
        assert result[1] == {"reel": 2, "row": 3}

    def test_should_include_board_reveal_with_win(self):
        """Test board reveal inclusion for winning spins."""
        formatter = OutputFormatter(include_losing_boards=False)

        assert formatter.should_include_board_reveal(10.5) is True
        assert formatter.should_include_board_reveal(0.01) is True

    def test_should_include_board_reveal_without_win(self):
        """Test board reveal exclusion for losing spins."""
        formatter = OutputFormatter(include_losing_boards=False)

        assert formatter.should_include_board_reveal(0.0) is False

    def test_should_include_board_reveal_always_when_enabled(self):
        """Test board reveal always included when configured."""
        formatter = OutputFormatter(include_losing_boards=True)

        assert formatter.should_include_board_reveal(0.0) is True
        assert formatter.should_include_board_reveal(10.5) is True

    def test_should_include_event_all_when_not_skipping(self):
        """Test all events included when skip_implicit_events is False."""
        formatter = OutputFormatter(skip_implicit_events=False)

        assert formatter.should_include_event("setFinalWin", {"amount": 0}) is True
        assert formatter.should_include_event("reveal", {}) is True

    def test_should_include_event_skip_implicit(self):
        """Test implicit events are skipped when configured."""
        formatter = OutputFormatter(skip_implicit_events=True)

        # Zero final win is implicit, should be skipped
        assert formatter.should_include_event("setFinalWin", {"amount": 0}) is False

        # Non-zero final win should be included
        assert formatter.should_include_event("setFinalWin", {"amount": 10}) is True

        # Other events should be included
        assert formatter.should_include_event("win", {"amount": 5}) is True

    def test_format_board_compact(self, mock_symbol):
        """Test compact board formatting."""
        formatter = OutputFormatter(output_mode=OutputMode.COMPACT)

        # Create a simple 2x2 board
        board = [
            [mock_symbol, mock_symbol],
            [mock_symbol, mock_symbol],
        ]

        result = formatter.format_board(board, [])

        assert len(result) == 2
        assert len(result[0]) == 2
        assert result[0][0] == "L5"
        assert result[1][1] == "L5"

    def test_format_board_verbose(self, mock_symbol):
        """Test verbose board formatting."""
        formatter = OutputFormatter(output_mode=OutputMode.VERBOSE)

        board = [
            [mock_symbol, mock_symbol],
        ]

        result = formatter.format_board(board, [])

        assert len(result) == 1
        assert len(result[0]) == 2
        assert isinstance(result[0][0], dict)
        assert result[0][0]["name"] == "L5"

    def test_get_format_version_compact(self):
        """Test format version string for compact mode."""
        formatter = OutputFormatter(output_mode=OutputMode.COMPACT)

        version = formatter.get_format_version()

        assert version == "2.0-compact"

    def test_get_format_version_verbose(self):
        """Test format version string for verbose mode."""
        formatter = OutputFormatter(output_mode=OutputMode.VERBOSE)

        version = formatter.get_format_version()

        assert version == "2.0-verbose"

    def test_manual_compression_flags_ignored_in_compact_mode(self):
        """Test that manual compression flags are overridden in compact mode."""
        formatter = OutputFormatter(
            output_mode=OutputMode.COMPACT,
            compress_positions=False,  # Should be ignored
            compress_symbols=False,    # Should be ignored
        )

        # Compact mode should force compression on
        assert formatter.compress_positions is True
        assert formatter.compress_symbols is True

    def test_file_size_savings_estimate(self, mock_symbol):
        """Test that compact format is actually smaller than verbose."""
        compact_formatter = OutputFormatter(output_mode=OutputMode.COMPACT)
        verbose_formatter = OutputFormatter(output_mode=OutputMode.VERBOSE)

        # Format a symbol
        compact_result = compact_formatter.format_symbol(mock_symbol, [])
        verbose_result = verbose_formatter.format_symbol(mock_symbol, [])

        # Compact should be smaller (just a string vs dict)
        import json
        compact_size = len(json.dumps(compact_result))
        verbose_size = len(json.dumps(verbose_result))

        assert compact_size < verbose_size

    def test_position_savings_estimate(self):
        """Test that compact positions are smaller than verbose."""
        compact_formatter = OutputFormatter(output_mode=OutputMode.COMPACT)
        verbose_formatter = OutputFormatter(output_mode=OutputMode.VERBOSE)

        compact_pos = compact_formatter.format_position(0, 2)
        verbose_pos = verbose_formatter.format_position(0, 2)

        import json
        compact_size = len(json.dumps(compact_pos))
        verbose_size = len(json.dumps(verbose_pos))

        assert compact_size < verbose_size
