# Contributing to Stake Engine Math SDK

Welcome! This guide will help you understand the coding standards and conventions used in this project.

## Table of Contents

- [Code Standards](#code-standards)
- [Naming Conventions](#naming-conventions)
- [Type Hints](#type-hints)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Development Workflow](#development-workflow)

---

## Code Standards

### Python Version
- **Required**: Python 3.12 or higher
- **Reason**: Modern type hints and performance improvements

### Code Formatting
- **Formatter**: [Black](https://black.readthedocs.io/) with default settings (88 char line length)
- **Import Sorting**: [isort](https://pycqa.github.io/isort/) with black-compatible profile
- **Linter**: [flake8](https://flake8.pycqa.org/) with relaxed line length (88 chars)
- **Type Checker**: [mypy](http://mypy-lang.org/) in strict mode

### Pre-commit Hooks
All code must pass pre-commit hooks before committing:
- Black formatting
- isort import sorting
- flake8 linting
- mypy type checking
- Trailing whitespace removal

---

## Naming Conventions

### General Principles
- **Be explicit over implicit**: `free_spin_count` not `fs`
- **Use full words**: Avoid abbreviations unless universally understood (e.g., `rtp`, `id`, `rng`)
- **Be consistent**: Use the same term throughout the codebase

### Variables

#### ✓ Good
```python
free_spin_count = 10
total_free_spins = 20
simulation_id = 1
game_mode = GameMode.BASE
current_board = draw_board()
win_multiplier = 5.0
```

#### ✗ Bad
```python
fs = 10          # Too abbreviated
tot_fs = 20      # Inconsistent abbreviation
sim = 1          # Unclear
gametype = "base"  # Should be enum
bd = draw()      # Too cryptic
mult = 5.0       # Ambiguous
```

### Constants
```python
# Use UPPER_SNAKE_CASE for module-level constants
MAX_FREE_SPINS = 100
DEFAULT_RTP = 0.96
MIN_CLUSTER_SIZE = 5

# Use enums for related constants
class GameMode(Enum):
    BASE = "base"
    FREE_SPIN = "freespin"
    BONUS = "bonus"
```

### Functions and Methods

#### Naming Rules
- Use `snake_case`
- Start with a **verb** that describes the action
- Be descriptive and specific

#### ✓ Good
```python
def calculate_cluster_wins(board: Board) -> list[Win]:
    """Calculate all cluster wins on the board."""
    ...

def has_free_spin_trigger(symbols: list[Symbol]) -> bool:
    """Check if free spin trigger condition is met."""
    ...

def reset_simulation_state() -> None:
    """Reset all state variables for a new simulation."""
    ...

def draw_board() -> Board:
    """Draw a random board from reel strips."""
    ...
```

#### ✗ Bad
```python
def calc(board):  # Too abbreviated, unclear what it calculates
    ...

def check_fs():  # Abbreviated, unclear return value
    ...

def reset():  # Too generic, reset what?
    ...

def board():  # Not a verb, unclear action
    ...
```

### Classes

#### Naming Rules
- Use `PascalCase`
- Use descriptive nouns or noun phrases
- Avoid generic names like `Manager`, `Handler`, `Processor` unless necessary

#### ✓ Good
```python
class BaseGameState:
    """Base class for all game state implementations."""
    ...

class ClusterWinCalculator:
    """Calculates cluster-based wins."""
    ...

class WinManager:
    """Manages win tracking and aggregation."""
    ...

class GameConfig:
    """Game configuration and parameters."""
    ...
```

#### ✗ Bad
```python
class State:  # Too generic
    ...

class GameExecutables:  # Not a noun, unclear purpose
    ...

class GeneralGameState:  # "General" is vague
    ...
```

### Files and Modules

#### Rules
- Use `snake_case` for all Python files
- Name files after their primary class or purpose
- Group related functionality

#### ✓ Good
```
base_game_state.py      # Contains BaseGameState class
cluster_calculator.py   # Contains cluster win logic
win_manager.py          # Contains WinManager class
game_config.py          # Contains GameConfig class
event_constants.py      # Contains EventConstants enum
```

#### ✗ Bad
```
state.py           # Too generic
gamestate.py       # Should be snake_case
executables.py     # Unclear purpose
override.py        # What does it override?
```

### Game-Specific Naming

#### Game Directory Structure
```
games/
  <game_name>/
    game_state.py          # Main game implementation (was gamestate.py)
    game_config.py         # Game configuration
    game_optimization.py   # Optimization parameters
    game_events.py         # Custom event generators (optional)
    game_calculations.py   # Helper calculations (optional)
    reels/                 # Reel strip CSV files
    library/               # Generated output files
    tests/                 # Game-specific tests
```

#### Common Variable Names in Games
```python
# Use these consistently across all games
self.simulation_id          # Current simulation number (was: sim)
self.free_spin_count        # Current free spin number (was: fs)
self.total_free_spins       # Total free spins awarded (was: tot_fs)
self.game_mode              # Current game mode (was: gametype)
self.current_board          # Current board state (was: board)
self.win_multiplier         # Total win multiplier (was: final_win)
self.is_win_cap_reached     # Win cap status (was: wincap_triggered)
self.global_multiplier      # Global multiplier (keep as-is)
```

---

## Type Hints

### Required Type Hints
All functions and methods **must** have type hints for:
- All parameters
- Return values
- Class attributes (if not obvious from `__init__`)

### Type Hint Examples

#### Functions
```python
from typing import Optional, Union

def calculate_win(
    symbol: str,
    count: int,
    multiplier: float = 1.0
) -> float:
    """Calculate win amount for a symbol combination."""
    return count * multiplier

def get_random_symbol(
    distribution: dict[str, float]
) -> Optional[str]:
    """Select a random symbol from weighted distribution."""
    ...
```

#### Classes
```python
from typing import ClassVar

class GameConfig:
    """Game configuration and parameters."""

    # Class variable
    _instance: ClassVar[Optional['GameConfig']] = None

    # Instance variables (type hints in __init__)
    def __init__(self) -> None:
        self.game_id: str = "tower_treasures"
        self.rtp: float = 0.97
        self.num_reels: int = 5
        self.num_rows: list[int] = [5] * self.num_reels
```

#### Type Aliases
Create type aliases for complex types:

```python
from typing import TypeAlias

# Board representation
Board: TypeAlias = list[list[Symbol]]

# Position on the board
Position: TypeAlias = tuple[int, int]  # (reel, row)

# Win details
WinDetails: TypeAlias = dict[str, Union[str, int, float, list[Position]]]
```

### Generic Types
```python
from typing import Generic, TypeVar

T = TypeVar('T')

class Distribution(Generic[T]):
    """Generic weighted distribution."""

    def __init__(self, items: dict[T, float]) -> None:
        self.items = items

    def sample(self) -> T:
        """Sample a random item from the distribution."""
        ...
```

---

## Documentation

### Docstring Format
Use Google-style docstrings for all public classes, methods, and functions.

#### Module Docstrings
```python
"""Cluster win calculation module.

This module provides functionality for detecting and calculating
cluster-based wins in slot games. Clusters are groups of adjacent
matching symbols.
"""
```

#### Class Docstrings
```python
class BaseGameState(ABC):
    """Base class for all slot game simulations.

    Provides core infrastructure for:
    - Random board generation from reel strips
    - Event recording and book management
    - Win calculation and management
    - Free spin triggering and tracking
    - RNG seeding for reproducibility

    Games should inherit from this class and implement:
        - run_spin(): Main game logic for a single spin
        - run_freespin(): Free spin game logic
        - assign_special_sym_function(): Special symbol handlers

    Attributes:
        config: Game configuration instance
        simulation_id: Current simulation number
        game_mode: Current game mode (base, freespin, etc.)
        current_board: Current board state

    Example:
        >>> class MyGame(BaseGameState):
        ...     def run_spin(self, simulation_id: int) -> None:
        ...         self.reset_seed(simulation_id)
        ...         self.draw_board()
        ...         self.calculate_wins()
    """
```

#### Method Docstrings
```python
def calculate_cluster_wins(
    self,
    board: Board,
    min_cluster_size: int = 5
) -> list[WinDetails]:
    """Calculate all cluster wins on the board.

    Detects all clusters of adjacent matching symbols and calculates
    their win amounts based on the paytable.

    Args:
        board: 2D board of symbols to analyze
        min_cluster_size: Minimum cluster size to count as a win

    Returns:
        List of win detail dictionaries containing:
            - symbol: The winning symbol
            - positions: List of (reel, row) positions
            - count: Number of symbols in cluster
            - amount: Win amount (multiplier × bet)

    Raises:
        ValueError: If min_cluster_size is less than 1

    Example:
        >>> wins = self.calculate_cluster_wins(board, min_cluster_size=5)
        >>> print(wins[0]['symbol'])
        'L1'
    """
```

### Inline Comments
- Use sparingly - code should be self-documenting
- Explain **why**, not **what**
- Keep comments up to date

```python
# ✓ Good - explains why
# Use BFS instead of DFS to ensure clusters are detected in order
clusters = self._find_clusters_bfs(board)

# ✗ Bad - explains what (obvious from code)
# Loop through each reel
for reel in board:
    ...
```

---

## Project Structure

### Directory Organization

```
stake-engine-math/
├── src/                          # Core SDK modules
│   ├── calculations/             # Win calculation algorithms
│   │   ├── cluster.py
│   │   ├── lines.py
│   │   ├── ways.py
│   │   └── scatter.py
│   ├── config/                   # Configuration classes
│   │   ├── config.py
│   │   ├── betmode.py
│   │   └── distributions.py
│   ├── events/                   # Event system
│   │   ├── event_constants.py
│   │   └── events.py
│   ├── state/                    # Core state machine
│   │   ├── base_game_state.py   # (was state.py)
│   │   ├── books.py
│   │   └── run_sims.py
│   ├── wins/                     # Win management
│   │   └── win_manager.py
│   └── write_data/               # Output generation
│       ├── write_data.py
│       └── write_configs.py
├── games/                        # Individual game implementations
│   ├── template/                 # Template for new games
│   ├── tower_treasures/
│   │   ├── game_state.py        # (was gamestate.py)
│   │   ├── game_config.py
│   │   ├── game_optimization.py
│   │   ├── reels/
│   │   ├── library/
│   │   └── tests/
│   └── 0_0_cluster/
├── optimization_program/         # Rust optimization
│   └── src/
├── tests/                        # SDK-wide tests
├── utils/                        # Utility scripts
├── docs/                         # Documentation
└── scripts/                      # Helper scripts
```

### Import Organization

Use isort with the following order:
1. Standard library imports
2. Third-party imports
3. Local application imports

```python
# Standard library
import os
import random
from abc import ABC, abstractmethod
from typing import Optional

# Third-party
import numpy as np

# Local application
from src.config.config import Config
from src.events.event_constants import EventConstants
from src.wins.win_manager import WinManager
```

---

## Testing

### Test Structure
```
tests/
├── test_cluster_calculator.py
├── test_win_manager.py
├── test_base_game_state.py
└── win_calculations/
    ├── test_clusterpay.py
    ├── test_linespay.py
    └── test_wayspay.py

games/tower_treasures/tests/
├── test_game_state.py
├── test_special_symbols.py
└── integration_test_example.py
```

### Test Naming
```python
class TestClusterCalculator:
    """Tests for ClusterCalculator class."""

    def test_finds_single_cluster(self) -> None:
        """Test detection of a single cluster."""
        ...

    def test_ignores_small_clusters(self) -> None:
        """Test that clusters below min size are ignored."""
        ...

    def test_handles_empty_board(self) -> None:
        """Test behavior with empty board."""
        ...
```

### Running Tests
```bash
# Run all tests
make test

# Run game-specific tests
make unit-test GAME=tower_treasures

# Run with coverage
pytest --cov=src tests/
```

---

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone <repo-url>
cd stake-engine-math

# Setup virtual environment and install dependencies
make setup
source env/bin/activate

# Install development dependencies
pip install black isort flake8 mypy pytest pytest-cov

# Install pre-commit hooks
pre-commit install
```

### Before Committing

```bash
# Format code
black .
isort .

# Check types
mypy src/ games/

# Run linter
flake8 src/ games/

# Run tests
pytest tests/
```

### Creating a New Game

1. Copy template:
   ```bash
   cp -r games/template games/my_new_game
   ```

2. Update `game_config.py`:
   ```python
   class GameConfig(Config):
       def __init__(self):
           super().__init__()
           self.game_id = "my_new_game"
           self.game_name = "My New Game"
           # ... configure game
   ```

3. Implement `game_state.py`:
   ```python
   class GameState(BaseGameState):
       def run_spin(self, simulation_id: int) -> None:
           # Implement game logic
           ...
   ```

4. Add reel strips to `reels/` directory

5. Run simulation:
   ```bash
   make run GAME=my_new_game
   ```

### Code Review Checklist

- [ ] Code follows naming conventions
- [ ] All functions have type hints
- [ ] All public methods have docstrings
- [ ] Tests added for new functionality
- [ ] Pre-commit hooks pass
- [ ] No mypy errors
- [ ] No flake8 warnings
- [ ] Documentation updated

---

## Common Patterns

### Singleton Pattern
```python
class GameConfig:
    """Game configuration (singleton)."""

    _instance: ClassVar[Optional['GameConfig']] = None

    def __new__(cls) -> 'GameConfig':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### Abstract Base Classes
```python
from abc import ABC, abstractmethod

class BaseGameState(ABC):
    """Base class for game implementations."""

    @abstractmethod
    def run_spin(self, simulation_id: int) -> None:
        """Run a single spin simulation.

        Must be implemented by subclasses.
        """
        ...
```

### Event Generation
```python
from src.events.event_constants import EventConstants
from src.events.events import construct_event

# Always use EventConstants, never hardcoded strings
event = construct_event(
    event_type=EventConstants.WIN.value,
    details={
        "symbol": "L1",
        "amount": 10.0,
        "positions": [(0, 0), (0, 1)]
    }
)
self.book.add_event(event)
```

### Configuration Access
```python
# Get current betmode
betmode = self.get_betmode(self.game_mode)

# Get distributions
distributions = betmode.distributions

# Get current distribution conditions
conditions = self.get_current_distribution_conditions()
```

---

## Questions?

If you have questions about these conventions or encounter edge cases,
please open an issue for discussion.

---

**Last Updated**: 2026-01-10
