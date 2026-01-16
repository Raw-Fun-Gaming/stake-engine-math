# Testing Guide

The Math SDK includes comprehensive testing capabilities at both the SDK level and game-specific level.

## Test Types

### 1. SDK-Level Tests
Located in `tests/` - test core SDK functionality

### 2. Game-Specific Unit Tests
Located in `games/<game_name>/tests/` - test individual game mechanics

## Running Tests

### All SDK Tests

```bash
# Activate virtual environment
source env/bin/activate

# Run all tests
make test

# Or use pytest directly
pytest tests/
```

### Game-Specific Tests

```bash
# Run tests for a specific game
make unit-test GAME=<game_name>

# Example
make unit-test GAME=tower_treasures

# Or use pytest directly
pytest games/tower_treasures/tests/
```

### Running Specific Test Files

```bash
# Single test file
pytest tests/test_state.py

# Single test function
pytest tests/test_state.py::test_draw_board

# With verbose output
pytest tests/test_state.py -v

# With print statements
pytest tests/test_state.py -s
```

## Writing Game-Specific Tests

### Test Structure

```
games/<game_name>/tests/
  ├── run_tests.py           # Test runner
  ├── test_basic.py          # Basic functionality tests
  ├── test_wins.py           # Win calculation tests
  ├── test_features.py       # Feature trigger tests
  └── test_mechanics.py      # Special mechanics tests
```

### Basic Test Template

```python
# games/my_game/tests/test_basic.py

import pytest
from games.my_game.game_state import GameState

@pytest.fixture
def game_state():
    """Create a fresh game_state for each test"""
    gs = GameState()
    return gs

def test_game_initialization(game_state):
    """Test that game initializes correctly"""
    assert game_state.config.game_id == "my_game"
    assert game_state.config.num_reels == 5
    assert game_state.config.num_rows == 3

def test_board_draw(game_state):
    """Test that board is drawn correctly"""
    game_state.draw_board()

    # Check board dimensions
    assert len(game_state.board) == game_state.config.num_reels
    assert len(game_state.board[0]) == game_state.config.num_rows

    # Check all positions have symbols
    for reel in game_state.board:
        for symbol in reel:
            assert symbol in game_state.config.all_symbols

def test_win_calculation(game_state):
    """Test basic win calculation"""
    # Set a known board state
    game_state.board = [
        ["A", "K", "Q"],
        ["A", "K", "J"],
        ["A", "Q", "J"],
        ["K", "Q", "J"],
        ["K", "Q", "J"]
    ]

    game_state.calculate_wins()

    # Check that wins were calculated
    assert game_state.book.get_total_win() > 0
```

### Testing Specific Mechanics

#### Test Feature Triggers

```python
def test_free_spin_trigger(game_state):
    """Test that free spins trigger correctly"""
    # Create board with 3+ scatters
    game_state.board = [
        ["S", "K", "Q"],  # Scatter
        ["A", "S", "J"],  # Scatter
        ["A", "Q", "S"],  # Scatter
        ["K", "Q", "J"],
        ["K", "Q", "J"]
    ]

    # Check trigger condition
    assert game_state.check_fs_condition() == True

    # Run spin and check events
    book = game_state.run_spin()
    event_types = [e["type"] for e in book.events]
    assert "triggerFreeSpins" in event_types
```

#### Test Special Symbols

```python
def test_multiplier_symbol(game_state):
    """Test that multiplier symbols are assigned correctly"""
    # Create board with multiplier symbol
    game_state.board = [
        ["M", "A", "A"],  # M = multiplier symbol
        ["A", "A", "A"],
        ["A", "A", "A"],
        ["K", "K", "K"],
        ["K", "K", "K"]
    ]

    # Process special symbols
    game_state.process_special_symbols()

    # Check that multiplier was assigned
    mult_symbol = game_state.board[0][0]
    assert hasattr(mult_symbol, "attributes")
    assert "multiplier" in mult_symbol.attributes
    assert mult_symbol.attributes["multiplier"] > 1
```

#### Test Win Calculations

```python
def test_cluster_win(game_state):
    """Test cluster win calculation"""
    # Create board with cluster
    game_state.board = [
        ["A", "A", "K"],
        ["A", "A", "K"],
        ["K", "K", "K"],
        ["Q", "Q", "Q"],
        ["Q", "Q", "Q"]
    ]

    game_state.calculate_wins()

    # Check that cluster was detected
    assert len(game_state.book.winning_clusters) > 0

    # Check win amount
    total_win = game_state.book.get_total_win()
    assert total_win > 0

    # Verify win is from 'A' cluster
    winning_symbols = [c["symbol"] for c in game_state.book.winning_clusters]
    assert "A" in winning_symbols
```

#### Test Tumble Mechanics

```python
def test_tumble_cascade(game_state):
    """Test that tumbles work correctly"""
    # Create board with winning cluster
    game_state.board = [
        ["A", "A", "A"],
        ["A", "A", "K"],
        ["K", "K", "Q"],
        ["Q", "Q", "J"],
        ["J", "J", "10"]
    ]

    initial_win = game_state.calculate_wins()
    assert initial_win > 0

    # Perform tumble
    game_state.tumble_board()

    # Check that winning symbols were removed
    # (specific logic depends on your tumble implementation)
    assert game_state.board != [
        ["A", "A", "A"],
        ["A", "A", "K"],
        ["K", "K", "Q"],
        ["Q", "Q", "J"],
        ["J", "J", "10"]
    ]
```

### Testing with Force Files

Force files allow testing specific scenarios:

```python
def test_specific_outcome(game_state):
    """Test a specific forced outcome"""
    # Load force file
    game_state.load_force_file("tests/force_files/big_win.json")

    # Run spin with forced outcome
    book = game_state.run_spin()

    # Verify expected outcome
    assert book.get_total_win() > 100  # Big win threshold
```

### Parameterized Tests

Test multiple scenarios efficiently:

```python
import pytest

@pytest.mark.parametrize("board,expected_win", [
    # Test case 1: Small cluster
    ([["A", "A", "K"], ["A", "K", "K"], ["K", "K", "Q"], ["Q", "Q", "J"], ["J", "J", "10"]], 5.0),

    # Test case 2: Medium cluster
    ([["A", "A", "A"], ["A", "A", "K"], ["A", "K", "K"], ["K", "K", "Q"], ["Q", "Q", "J"]], 15.0),

    # Test case 3: Large cluster
    ([["A", "A", "A"], ["A", "A", "A"], ["A", "A", "K"], ["A", "K", "K"], ["K", "K", "Q"]], 50.0),
])
def test_cluster_sizes(game_state, board, expected_win):
    """Test different cluster sizes"""
    game_state.board = board
    game_state.calculate_wins()
    assert abs(game_state.book.get_total_win() - expected_win) < 0.01
```

## Test Fixtures

### Shared Fixtures

Create `conftest.py` in the tests directory:

```python
# games/my_game/tests/conftest.py

import pytest
from games.my_game.game_state import GameState

@pytest.fixture
def game_state():
    """Fresh game_state for each test"""
    return GameState()

@pytest.fixture
def base_game_state(game_state):
    """Gamestate in base game mode"""
    game_state.game_type = "base"
    return game_state

@pytest.fixture
def free_spin_game_state(game_state):
    """Gamestate in free_spin mode"""
    game_state.game_type = "bonus"
    game_state.in_free_spin = True
    return game_state

@pytest.fixture
def sample_winning_board():
    """A board with guaranteed wins"""
    return [
        ["A", "A", "A"],
        ["A", "A", "K"],
        ["K", "K", "Q"],
        ["Q", "Q", "J"],
        ["J", "J", "10"]
    ]
```

Usage:
```python
def test_with_fixtures(base_game_state, sample_winning_board):
    """Test using multiple fixtures"""
    base_game_state.board = sample_winning_board
    base_game_state.calculate_wins()
    assert base_game_state.book.get_total_win() > 0
```

## Best Practices

### 1. Test One Thing at a Time

```python
# ✅ Good - focused test
def test_scatter_detection(game_state):
    """Test that scatters are detected"""
    game_state.board = create_board_with_scatters(3)
    assert game_state.count_scatters() == 3

# ❌ Bad - testing too much
def test_everything(game_state):
    """Test scatter detection, wins, and free spins"""
    # Too much in one test
```

### 2. Use Descriptive Names

```python
# ✅ Good
def test_free_spins_trigger_with_three_scatters(game_state):
    ...

# ❌ Bad
def test_fs(game_state):
    ...
```

### 3. Arrange-Act-Assert Pattern

```python
def test_multiplier_application(game_state):
    # Arrange - setup test conditions
    game_state.board = [["A", "A", "A"], ...]
    game_state.global_multiplier = 2

    # Act - perform action
    game_state.calculate_wins()

    # Assert - verify results
    expected_win = base_win * 2
    assert game_state.book.get_total_win() == expected_win
```

### 4. Test Edge Cases

```python
def test_empty_board(game_state):
    """Test behavior with no symbols"""
    game_state.board = [[], [], [], [], []]
    # Should not crash
    game_state.calculate_wins()

def test_all_same_symbol(game_state):
    """Test board with all same symbols"""
    game_state.board = [["A"] * 3 for _ in range(5)]
    game_state.calculate_wins()
    assert game_state.book.get_total_win() > 0

def test_maximum_win(game_state):
    """Test maximum possible win"""
    game_state.board = create_maximum_win_board()
    game_state.calculate_wins()
    assert game_state.book.get_total_win() <= game_state.config.max_win
```

## Continuous Integration

### Running Tests in CI

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -e .

    - name: Run tests
      run: |
        pytest tests/

    - name: Run game tests
      run: |
        pytest games/*/tests/
```

## Test Coverage

### Generate Coverage Report

```bash
# Install pytest-cov
pip install pytest-cov

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# View report
open htmlcov/index.html
```

### Coverage Configuration

```ini
# .coveragerc
[run]
source = src

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## Debugging Tests

### Print Debugging

```python
def test_with_debug(game_state):
    game_state.board = [["A", "A", "A"], ...]

    # Print board state
    print("\nBoard:")
    for reel in game_state.board:
        print(reel)

    game_state.calculate_wins()

    # Print events
    print("\nEvents:")
    for event in game_state.book.events:
        print(event)

    assert game_state.book.get_total_win() > 0
```

Run with `-s` flag to see prints:
```bash
pytest tests/test_wins.py -s
```

### Interactive Debugging

```python
def test_with_breakpoint(game_state):
    game_state.board = [["A", "A", "A"], ...]

    # Python debugger
    import pdb; pdb.set_trace()

    game_state.calculate_wins()
```

Run test and interact:
```bash
pytest tests/test_wins.py
# (Pdb) print(game_state.board)
# (Pdb) continue
```

## See Also

- [Game Structure](game-structure.md) - Understanding what to test
- [Event System](events.md) - Testing events
- [Running Games](running-games.md) - Integration testing with full runs
