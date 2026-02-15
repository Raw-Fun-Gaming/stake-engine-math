# Scatter Template

**Location**: `games/template_scatter/`
**Win Type**: Scatter-pay
**Inheritance**: `GameState` → `Board` → `GameState` (base, `src/state/game_state.py`)

## Overview

The scatter template implements "pay anywhere" mechanics where matching symbols pay regardless of position on the board. Unlike lines or ways which require adjacent positions, scatter-pay counts all instances of a symbol anywhere on the grid. This is commonly used for bonus symbols and instant-win mechanics.

## Game Mechanics

### Core Features

- **Scatter-pay wins**: Symbols pay regardless of position
- **Count-based**: Win based on total count across all positions
- **Large grid**: Typically uses bigger boards (6×5, 7×7, etc.)
- **Free spin mode**: Scatter triggers bonus rounds
- **Threshold-based**: Minimum counts required for wins (e.g., 8+ symbols)

### Board Configuration

```python
self.num_reels = 6
self.num_rows = [5] * self.num_reels  # 6×5 = 30 positions
self.win_type = "scatter"
```

### Paytable Structure

Scatter-pay uses range-based paytables:

```python
t1, t2, t3, t4 = (8, 8), (9, 10), (11, 13), (14, 36)
pay_group = {
    (t1, "H1"): 3.0,   # 8 symbols = 3x
    (t2, "H1"): 7.5,   # 9-10 symbols = 7.5x
    (t3, "H1"): 15.0,  # 11-13 symbols = 15x
    (t4, "H1"): 60.0,  # 14-36 symbols = 60x
    ...
}
```

The first element defines the range (min, max) of matching symbols required.

## Game-Specific Implementation

### State Management

```python
def reset_book(self) -> None:
    """Reset state for new simulation."""
    super().reset_book()
```

No additional state needed - scatter calculation is stateless.

### Main Game Loop

```python
def run_spin(self) -> Board:
    """Execute a single base game spin."""
    board = self.draw_board()

    # Calculate scatter wins
    scatter_calc = Scatter(board, self)
    wins = scatter_calc.calculate_scatter_wins()

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

### Scatter Win Detection

The `Scatter` class counts all instances of each symbol:

```python
# Pseudo-code for scatter calculation
symbol_counts = {}
for position in board:
    symbol = position.symbol
    symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

for symbol, count in symbol_counts.items():
    if count >= minimum_threshold:
        payout = paytable.get_payout_for_count(symbol, count)
        wins.append({"symbol": symbol, "count": count, "amount": payout})
```

## Custom Functions

### Special Symbol Assignment

```python
def assign_special_sym_function(self) -> None:
    """Define special symbol behaviors.

    Scatter template can optionally include multiplier symbols.
    """
    self.special_symbol_functions = {
        "M": [self.assign_multiplier_property]  # Optional
    }
```

### Multiplier Symbols (Optional)

Some scatter games include multiplier symbols that boost wins:

```python
def assign_multiplier_property(self, symbol) -> None:
    """Assign random multiplier value to symbol."""
    multiplier = get_random_outcome({2: 0.7, 3: 0.2, 5: 0.1})
    symbol.assign_attribute({"multiplier": multiplier})
```

### Free Spin Triggers

```python
def check_free_spin_condition(self) -> bool:
    """Check if bonus scatter count meets trigger requirement."""
    bonus_count = self.count_symbol_on_board("bonus")
    return bonus_count >= self.config.bonus_trigger_count
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
            "bonus_trigger": {3: 1.0}  # 3+ bonus symbols trigger
        }
    ),
    "free": BetMode(
        reels_file="free.csv",
        distributions={
            "bonus_trigger": {3: 0.5, 4: 0.3, 5: 0.2}
        }
    )
}
```

## Usage Example

```bash
# Run with default config
make run GAME=template_scatter

# Run with production config
make run GAME=template_scatter CONFIG=prod.toml

# Run unit tests
make unit-test GAME=template_scatter
```

## Key Implementation Details

### Win Calculation

Uses `Scatter` class from `src/calculations/scatter.py`:
- Counts all instances of each symbol type
- Checks against minimum thresholds in paytable
- Returns wins for all qualifying symbols
- No position tracking needed

### Paytable Ranges

Unlike lines/ways which use exact counts, scatter-pay uses ranges:

```python
# Example: How paytable ranges work
paytable = {
    (8, 8, "H1"): 3.0,    # Exactly 8 symbols
    (9, 10, "H1"): 7.5,   # 9 or 10 symbols
    (11, 13, "H1"): 15.0, # 11, 12, or 13 symbols
    (14, 30, "H1"): 60.0, # 14-30 symbols (max possible)
}
```

### Multiple Symbol Wins

All symbols can win simultaneously on the same spin:

```
Board has:
- 12 × "H1" symbols → Pays 15x (in range 11-13)
- 9 × "H2" symbols → Pays 5x (in range 9-10)
- 15 × "L1" symbols → Pays 25x (in range 14-30)
Total win = 15x + 5x + 25x = 45x
```

## Files Overview

| File | Purpose | Lines |
|------|---------|-------|
| `game_state.py` | Game logic | ~100 |
| `game_config.py` | Configuration | ~130 |
| `game_optimization.py` | Optimization params | ~60 |
| `run.py` | Execution script | ~50 |

**Note**: `game_events.py` is optional and used for custom event formatting.

## Differences from Other Win Types

| Feature | Lines | Ways | Scatter |
|---------|-------|------|---------|
| Position matters | Yes (paylines) | Yes (adjacent) | No (anywhere) |
| Win formation | Sequential | Left-to-right | Total count |
| Minimum symbols | 3 (usually) | 3 (usually) | 8+ (varies) |
| Grid size | 5×3 typical | 5×3 typical | 6×5 or larger |
| Multiple symbols | Rare | Rare | Common |

## Why Use This Template?

The scatter template is ideal for:

1. **Instant win games**: Bingo-style, match-three collections
2. **Large grids**: Games with 6×5, 7×7, or bigger boards
3. **Multiple symbols**: When many symbols should pay simultaneously
4. **Bonus features**: Collection mechanics (e.g., "collect 10 gems")
5. **Simple rules**: Easy for players to understand "count to win"

## Common Modifications

### Add Collection Mechanics

```python
def collect_symbols(self, symbol_name: str) -> int:
    """Count and remove collected symbols from board."""
    count = 0
    for reel_idx, reel in enumerate(self.board):
        for row_idx, symbol in enumerate(reel):
            if symbol.name == symbol_name:
                count += 1
                self.board[reel_idx][row_idx] = Symbol("empty")
    return count
```

### Progressive Multipliers

```python
def apply_progressive_multiplier(self, wins: list) -> None:
    """Increase multiplier based on symbol count."""
    for win in wins:
        count = win["count"]
        if count >= 20:
            win["multiplier"] = 5
        elif count >= 15:
            win["multiplier"] = 3
        elif count >= 10:
            win["multiplier"] = 2
```

### Symbol Upgrades

```python
def upgrade_symbols(self, board: Board) -> Board:
    """Upgrade low symbols to high symbols based on count."""
    low_count = self.count_symbol_on_board("L1")
    if low_count >= 15:
        # Upgrade all L1 to H1
        for reel in board:
            for symbol in reel:
                if symbol.name == "L1":
                    symbol.name = "H1"
    return board
```

## Related Documentation

- [Scatter Calculation](game-structure.md#win-calculations)
- [Large Grid Configuration](running-games.md#grid-configuration)
- [Event System](events.md)
