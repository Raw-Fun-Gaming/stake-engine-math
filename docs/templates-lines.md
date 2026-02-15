# Lines Template

**Location**: `games/template_lines/`
**Win Type**: Line-pay
**Inheritance**: `GameState` → `Board` → `GameState` (base, `src/state/game_state.py`)

## Overview

The lines template implements traditional payline-based slot mechanics. This is the simplest and most common slot game type, where wins are formed by matching symbols along predefined paylines from left to right.

## Game Mechanics

### Core Features

- **Payline wins**: Traditional left-to-right line matching
- **Simple structure**: No complex cascades or special features
- **Free spin mode**: Scatter symbol triggers bonus rounds
- **Wild substitution**: Wild symbols substitute for all except scatter

### Board Configuration

```python
self.num_reels = 5
self.num_rows = [3] * self.num_reels  # Classic 5×3 grid
self.win_type = "lines"
```

### Paytable Structure

Lines use simple count-based paytables:

```python
self.paytable = {
    (5, "W"): 50,   # 5 wilds on a line = 50x
    (4, "W"): 20,   # 4 wilds = 20x
    (3, "W"): 10,   # 3 wilds = 10x
    (5, "H1"): 50,
    (4, "H1"): 20,
    (3, "H1"): 10,
    (5, "H2"): 15,
    (4, "H2"): 5,
    (3, "H2"): 3,
    ...
}
```

## Game-Specific Implementation

### State Management

```python
def reset_book(self) -> None:
    """Reset state for new simulation.

    Lines template uses base reset without additional state.
    """
    super().reset_book()
```

This template doesn't need custom state management - it uses the base implementation directly.

### Main Game Loop

The `run_spin()` method is straightforward:

1. Draw board from reel strips
2. Calculate line wins
3. Check for scatter triggers
4. Run free spins if triggered

```python
def run_spin(self) -> Board:
    """Execute a single base game spin."""
    board = self.draw_board()

    # Calculate line wins
    lines_calc = Lines(board, self)
    wins = lines_calc.calculate_line_wins()

    # Emit win events
    for win in wins:
        self.book.add_event(construct_event(
            EventConstants.WIN.value,
            details=win
        ))

    # Check for free spin trigger
    if self.check_free_spin_condition():
        self.run_free_spin_from_base()

    return board
```

### Free Spin Logic

```python
def run_free_spin(self) -> Board:
    """Execute a single free spin.

    Uses different reel strips but same win calculation.
    """
    board = self.draw_board()

    lines_calc = Lines(board, self)
    wins = lines_calc.calculate_line_wins()

    for win in wins:
        self.book.add_event(construct_event(
            EventConstants.WIN.value,
            details=win
        ))

    # Check for retriggers
    if self.check_free_spin_condition():
        self.retrigger_free_spins()

    return board
```

## Payline Configuration

Paylines are defined in the config as a list of row positions per reel:

```python
self.paylines = [
    [1, 1, 1, 1, 1],  # Middle line
    [0, 0, 0, 0, 0],  # Top line
    [2, 2, 2, 2, 2],  # Bottom line
    [0, 1, 2, 1, 0],  # V-shape
    [2, 1, 0, 1, 2],  # Inverted V
    [0, 0, 1, 0, 0],  # W-shape
    [2, 2, 1, 2, 2],  # M-shape
    [1, 0, 0, 0, 1],  # Top diagonal
    [1, 2, 2, 2, 1],  # Bottom diagonal
    [0, 1, 1, 1, 0],  # Small V
]
```

Each payline is checked for matching symbols from left to right.

## Custom Functions

### Special Symbol Assignment

```python
def assign_special_sym_function(self) -> None:
    """Define special symbol behaviors.

    Lines template has no special symbol attributes.
    Standard wild substitution is handled by Lines class.
    """
    pass
```

The template doesn't need custom symbol handlers - wilds and scatters are handled by the base `Lines` calculation class.

### Free Spin Triggers

```python
def check_free_spin_condition(self) -> bool:
    """Check if scatter count meets trigger requirement."""
    scatter_count = self.count_symbol_on_board("scatter")
    required = self.config.bet_modes[self.game_type].distributions.get(
        "scatter_trigger", {3: 1.0}
    )
    return scatter_count >= min(required.keys())
```

## Configuration Files

### Run Configuration (`dev.toml`)

```toml
[execution]
num_threads = 10
compression = false

[simulation]
base = 100           # Fast for development
bonus = 100

[pipeline]
run_sims = true
run_optimization = false
run_analysis = false
```

### Bet Modes

```python
self.bet_modes = {
    "base": BetMode(
        reels_file="base.csv",
        distributions={
            "scatter_trigger": {3: 1.0}  # 3+ scatters trigger
        }
    ),
    "free": BetMode(
        reels_file="free.csv",
        distributions={
            "scatter_trigger": {3: 0.5, 4: 0.3, 5: 0.2}  # Retrigger distribution
        }
    )
}
```

## Usage Example

```bash
# Run with default config
make run GAME=template_lines

# Run with production config (1M simulations)
make run GAME=template_lines CONFIG=prod.toml

# Run unit tests
make unit-test GAME=template_lines
```

## Key Implementation Details

### Win Calculation

Uses `Lines` class from `src/calculations/lines.py`:
- Iterates through each payline
- Checks for matching symbols from left to right
- Handles wild substitution automatically
- Returns list of winning lines with details

### Wild Symbols

Wild behavior is built into the `Lines` class:
- Substitutes for all symbols except scatter
- Multiple wilds on same line count as highest paying symbol
- Wild-only wins use wild paytable values

### Scatter Symbols

Scatters are counted separately and don't need to be on paylines:
- Pay regardless of position (scatter-pay logic)
- Trigger free spins when count threshold met
- Don't substitute with wilds

## Files Overview

| File | Purpose | Lines |
|------|---------|-------|
| `game_state.py` | Game logic | ~100 |
| `game_config.py` | Configuration | ~120 |
| `game_optimization.py` | Optimization params | ~60 |
| `run.py` | Execution script | ~50 |

**Note**: This template does NOT include `game_events.py` because it uses only standard events from `src/events/constants.py`.

## Why Use This Template?

The lines template is ideal for:

1. **Learning the SDK**: Simplest structure to understand
2. **Classic slots**: Traditional casino-style games
3. **Starting point**: Add features incrementally to this base
4. **Testing**: Quick simulation and verification

## Common Modifications

### Add Multiplier Wilds

```python
def assign_special_sym_function(self) -> None:
    self.special_symbol_functions = {
        "W": [self.assign_multiplier]
    }

def assign_multiplier(self, symbol) -> None:
    multiplier = get_random_outcome({2: 0.7, 3: 0.2, 5: 0.1})
    symbol.assign_attribute({"multiplier": multiplier})
```

### Add Progressive Free Spins

```python
def retrigger_free_spins(self) -> None:
    """Award additional spins and increase multiplier."""
    self.total_free_spins += 5
    self.free_spin_multiplier += 1
```

## Related Documentation

- [Lines Calculation](game-structure.md#win-calculations)
- [Payline Configuration](running-games.md#paylines)
- [Event System](events.md)
