# Ways Template

**Location**: `games/template_ways/`
**Win Type**: Ways-pay
**Inheritance**: `GameState` → `Board` → `GameState` (base, `src/state/game_state.py`)

## Overview

The ways template implements "ways to win" mechanics, where matching symbols on adjacent reels (left to right) form wins regardless of row position. This creates significantly more winning combinations than traditional paylines - for example, a 5×3 grid offers 243 ways to win (3^5).

## Game Mechanics

### Core Features

- **Ways-pay wins**: Matching symbols on adjacent reels
- **No paylines**: Any position on adjacent reels counts
- **Left-to-right**: Must start from leftmost reel
- **Free spin mode**: Scatter triggers bonus rounds
- **Wild substitution**: Wilds substitute for all except scatter

### Board Configuration

```python
self.num_reels = 5
self.num_rows = [3] * self.num_reels  # 5×3 = 243 ways
self.win_type = "ways"
```

### Ways Calculation

Total ways = product of rows per reel:
- 5×3 grid: 3 × 3 × 3 × 3 × 3 = **243 ways**
- 5×4 grid: 4 × 4 × 4 × 4 × 4 = **1,024 ways**
- Variable rows (3-4-5-4-3): 3 × 4 × 5 × 4 × 3 = **720 ways**

### Paytable Structure

Ways-pay uses count-based paytables similar to lines:

```python
self.paytable = {
    (5, "H1"): 10,  # 5 matching reels = 10x
    (4, "H1"): 5,   # 4 matching reels = 5x
    (3, "H1"): 3,   # 3 matching reels = 3x
    (5, "H2"): 8,
    (4, "H2"): 4,
    (3, "H2"): 2,
    ...
}
```

## Game-Specific Implementation

### State Management

```python
def reset_book(self) -> None:
    """Reset state for new simulation.

    Ways template uses base reset without additional state.
    """
    super().reset_book()
```

### Main Game Loop

```python
def run_spin(self) -> Board:
    """Execute a single base game spin."""
    board = self.draw_board()

    # Calculate ways wins
    ways_calc = Ways(board, self)
    wins = ways_calc.calculate_ways_wins()

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

### Ways Win Detection

The `Ways` class checks each symbol on reel 0, then scans adjacent reels:

```python
# Pseudo-code for ways calculation
for symbol in reel_0:
    count = 1
    for next_reel in [1, 2, 3, 4]:
        if symbol appears on next_reel:
            count += 1
        else:
            break  # Ways must be consecutive

    if count >= 3:  # Minimum 3 reels for win
        win_amount = paytable[(count, symbol)] * total_ways
```

## Custom Functions

### Special Symbol Assignment

```python
def assign_special_sym_function(self) -> None:
    """Define special symbol behaviors.

    Ways template has no special symbol attributes.
    Standard wild substitution is handled by Ways class.
    """
    pass
```

### Free Spin Triggers

```python
def check_free_spin_condition(self) -> bool:
    """Check if scatter count meets trigger requirement."""
    scatter_count = self.count_symbol_on_board("scatter")
    required = self.config.scatter_trigger_count
    return scatter_count >= required
```

## Configuration Files

### Run Configuration (`dev.toml`)

```toml
[execution]
num_threads = 10
compression = false

[simulation]
base = 100
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
            "scatter_trigger": {3: 1.0}  # 3+ scatters
        }
    ),
    "free": BetMode(
        reels_file="free.csv",
        distributions={
            "scatter_trigger": {3: 0.6, 4: 0.3, 5: 0.1}
        }
    )
}
```

## Usage Example

```bash
# Run with default config
make run GAME=template_ways

# Run with production config
make run GAME=template_ways CONFIG=prod.toml

# Run unit tests
make unit-test GAME=template_ways
```

## Key Implementation Details

### Win Calculation

Uses `Ways` class from `src/calculations/ways.py`:
- Starts from leftmost reel
- Checks each symbol on reel 0
- Counts consecutive reels with matching symbols
- Handles wild substitution
- Calculates total ways for each win

### Ways Multiplier

The win amount includes a multiplier based on how many positions the symbol appeared on each reel:

```
Win = Base Payout × (Positions on Reel 1 × Positions on Reel 2 × ...)
```

Example with 3 symbols on 3 reels (5×3 grid):
- Symbol "H1" on reels 0, 1, 2
- Appears 2 times on reel 0, 3 times on reel 1, 1 time on reel 2
- Ways multiplier = 2 × 3 × 1 = 6 ways
- Total win = Base payout × 6

### Wild Behavior

- Wilds substitute for all symbols except scatter
- Multiple wilds on adjacent reels still count as matching
- Wild-only combinations use wild paytable

## Files Overview

| File | Purpose | Lines |
|------|---------|-------|
| `game_state.py` | Game logic | ~100 |
| `game_config.py` | Configuration | ~110 |
| `game_optimization.py` | Optimization params | ~60 |
| `run.py` | Execution script | ~50 |

**Note**: This template does NOT include `game_events.py` - uses standard events only.

## Differences from Lines

| Feature | Lines | Ways |
|---------|-------|------|
| Win formation | Specific paylines | Any adjacent reels |
| Number of wins | Limited by payline count | Product of rows |
| Position matters | Yes (must match payline) | No (any position on reel) |
| Typical grid | 5×3 (10-50 lines) | 5×3 (243 ways) |
| Win frequency | Lower | Higher |
| Payout size | Larger | Smaller (balanced by frequency) |

## Why Use This Template?

The ways template is ideal for:

1. **Modern slots**: Popular in contemporary casino games
2. **High volatility**: More frequent but smaller wins
3. **Variable rows**: Easy to implement different row heights per reel
4. **Simple rules**: Players understand "adjacent reels" easily

## Common Modifications

### Variable Row Heights

```python
# Create megaways-style variable rows
self.num_rows = [2, 3, 4, 3, 2]  # Total: 2×3×4×3×2 = 144 ways
```

### Add Multiplier Symbols

```python
def assign_special_sym_function(self) -> None:
    self.special_symbol_functions = {
        "M": [self.assign_multiplier]
    }

def assign_multiplier(self, symbol) -> None:
    """Assign multiplier that applies to all ways wins."""
    multiplier = get_random_outcome({2: 0.6, 3: 0.3, 5: 0.1})
    symbol.assign_attribute({"multiplier": multiplier})
```

### Reel Modifiers

```python
def apply_reel_modifier(self, board: Board) -> Board:
    """Add extra symbols to random reels (megaways-style)."""
    reel_idx = random.randint(0, self.config.num_reels - 1)
    extra_symbol = self.get_random_symbol()
    board[reel_idx].append(extra_symbol)
    return board
```

## Related Documentation

- [Ways Calculation](game-structure.md#win-calculations)
- [Variable Rows Configuration](running-games.md#variable-rows)
- [Event System](events.md)
