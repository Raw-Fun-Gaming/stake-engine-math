# Expanding Wilds Template

**Location**: `games/template_expanding_wilds/`
**Win Type**: Line-pay
**Inheritance**: `GameState` → `Board` → `GameState` (base, `src/state/game_state.py`)

## Overview

The expanding wilds template demonstrates advanced slot mechanics including expanding wild symbols, sticky wilds that persist across free spins, and a special "super spin" prize collection mode. This template showcases how to implement complex multi-stage bonus features.

## Game Mechanics

### Core Features

- **Line-pay base game**: Traditional payline wins
- **Expanding wilds**: Wild symbols expand to fill entire reels
- **Sticky wilds**: Expanded wilds persist during free spins
- **Wild multipliers**: Wilds carry random multiplier values
- **Super Spin mode**: Respin-style prize collection with sticky prize symbols
- **Prize symbols**: Random value symbols collected during super spins

### Board Configuration

```python
self.num_reels = 5
self.num_rows = [5] * self.num_reels  # 5×5 grid for more expansion potential
self.win_type = "lines"
```

## Game-Specific Implementation

### Special Symbol Handlers

```python
def assign_special_sym_function(self) -> None:
    """Define special symbol behaviors.

    W symbols get multiplier attributes (in free game only)
    P symbols get prize values
    """
    self.special_symbol_functions = {
        "W": [self.assign_multiplier_property],
        "P": [self.assign_prize_value],
    }

def assign_multiplier_property(self, symbol: Any) -> None:
    """Assign multiplier attribute to wild symbol.

    Only assigned in free game mode.
    """
    if self.game_type != self.config.base_game_type:
        multiplier_value = get_random_outcome(
            self.get_current_distribution_conditions()["multiplier_values"][self.game_type]
        )
        symbol.assign_attribute({"multiplier": multiplier_value})

def assign_prize_value(self, symbol: Any) -> None:
    """Assign prize value to prize symbol."""
    multiplier_value = get_random_outcome(
        self.get_current_distribution_conditions()["prize_values"]
    )
    symbol.assign_attribute({"prize": multiplier_value})
```

### State Management

```python
def reset_book(self) -> None:
    """Reset all state variables for a new simulation.

    Extends base reset_book to include expanding wild state.
    """
    super().reset_book()
    self.expanding_wilds = []  # Track which reels have expanding wilds
    self.available_reels = [i for i in range(self.config.num_reels)]

def reset_super_spin(self) -> None:
    """Initialize super_spin mode state."""
    self.total_free_spins = 3  # Start with 3 super spins
    self.super_spin_multiplier = 1
    self.sticky_positions = []  # Track sticky prize positions
```

### Expanding Wild Logic

```python
def expand_wilds(self, board: Board) -> Board:
    """Expand wild symbols to fill entire reels.

    When a wild lands, the entire reel becomes wild.
    In free game, these expanded reels persist across spins.
    """
    for reel_idx, reel in enumerate(board):
        if any(symbol.name == "W" for symbol in reel):
            # Found a wild - expand entire reel
            for row_idx in range(len(reel)):
                board[reel_idx][row_idx] = Symbol(
                    name="W",
                    attributes={"multiplier": self.wild_multiplier}
                )

            # Track for persistence in free spins
            if self.game_type == "free":
                self.expanding_wilds.append(reel_idx)
                self.book.add_event(
                    new_expanding_wild_event(reel_idx, self.wild_multiplier)
                )

    return board
```

### Main Game Loop (Base Game)

```python
def run_spin(self) -> Board:
    """Execute a single base game spin."""
    board = self.draw_board()

    # Expand any wild symbols
    board = self.expand_wilds(board)

    # Calculate line wins
    lines_calc = Lines(board, self)
    wins = lines_calc.calculate_line_wins()

    for win in wins:
        self.book.add_event(construct_event(
            EventConstants.WIN.value,
            details=win
        ))

    # Check for free spin trigger (3+ scatters)
    if self.check_free_spin_condition():
        self.run_free_spin_from_base()

    return board
```

### Free Spin Loop (With Persistent Wilds)

```python
def run_free_spin(self) -> Board:
    """Execute a single free spin with persistent expanding wilds."""
    board = self.draw_board()

    # Restore previously expanded wilds (sticky)
    board = self.restore_expanding_wilds(board)

    # Expand any new wilds
    board = self.expand_wilds(board)

    # Calculate wins with all wilds
    lines_calc = Lines(board, self)
    wins = lines_calc.calculate_line_wins()

    # Apply wild multipliers
    for win in wins:
        if self.has_wild_in_win(win):
            win["amount"] *= self.get_wild_multiplier(win)

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

### Super Spin Mode

Super spin is a special bonus mode triggered separately from free spins:

```python
def run_super_spin_from_base(self) -> None:
    """Enter super spin mode from base game."""
    self.reset_super_spin()
    self.book.add_event(trigger_super_spin_event(self.total_free_spins))

    while self.total_free_spins > 0:
        self.run_single_super_spin()
        self.total_free_spins -= 1

    self.book.add_event(end_super_spin_event(self.super_spin_win))

def run_single_super_spin(self) -> Board:
    """Execute a single super spin (respin with sticky prizes).

    Prize symbols that land become sticky and remain for subsequent spins.
    New prizes reset the spin counter to 3.
    """
    board = self.draw_board()

    # Restore sticky prize positions
    board = self.restore_sticky_prizes(board)

    # Check for new prizes
    new_prizes = self.find_prize_symbols(board)

    if new_prizes:
        # New prizes reset spin counter
        self.total_free_spins = 3

        # Add new prizes to sticky positions
        for prize_position in new_prizes:
            self.sticky_positions.append(prize_position)
            self.super_spin_win += prize_position.symbol.attributes["prize"]

            self.book.add_event(
                new_sticky_event(prize_position)
            )

    return board
```

## Custom Events

The template includes several custom events in `game_events.py`:

```python
def new_expanding_wild_event(reel_idx: int, multiplier: int) -> dict:
    """Emit when a wild expands on a reel."""
    return {
        "type": "NEW_EXPANDING_WILD",
        "reel": reel_idx,
        "multiplier": multiplier
    }

def update_expanding_wild_event(reels: list) -> dict:
    """Emit current state of expanding wilds."""
    return {
        "type": "UPDATE_EXPANDING_WILDS",
        "reels": reels
    }

def new_sticky_event(position: dict) -> dict:
    """Emit when a prize becomes sticky in super spin."""
    return {
        "type": "NEW_STICKY_SYMBOL",
        "position": position,
        "value": position["symbol"]["attributes"]["prize"]
    }

def reveal_prize_event(prizes: list) -> dict:
    """Emit all collected prizes at end of super spin."""
    return {
        "type": "REVEAL_PRIZES",
        "prizes": prizes,
        "total": sum(p["value"] for p in prizes)
    }
```

## Configuration Files

### Game Configuration

```python
# Multiplier distributions for wild symbols
self.bet_modes["free"].distributions["multiplier_values"] = {
    "free": {2: 0.6, 3: 0.3, 5: 0.1}
}

# Prize value distributions for super spin
self.bet_modes["super_spin"].distributions["prize_values"] = {
    10: 0.4,
    20: 0.3,
    50: 0.2,
    100: 0.08,
    500: 0.02
}

# Free spin trigger requirements
self.bet_modes["base"].distributions["scatter_trigger"] = {3: 1.0}

# Super spin trigger (separate from free spins)
self.bet_modes["base"].distributions["super_spin_trigger"] = {3: 1.0}
```

### Run Configuration (`dev.toml`)

```toml
[execution]
num_threads = 10
compression = false

[simulation]
base = 100
bonus = 100
super_spin = 100  # Additional mode

[pipeline]
run_sims = true
run_optimization = false
run_analysis = false

target_modes = ["base", "bonus", "super_spin"]
```

## Usage Example

```bash
# Run with default config
make run GAME=template_expanding_wilds

# Run with production config
make run GAME=template_expanding_wilds CONFIG=prod.toml

# Run unit tests
make unit-test GAME=template_expanding_wilds
```

## Key Implementation Details

### Expanding Wild Mechanics

1. **Detection**: Check each reel for wild symbol
2. **Expansion**: Replace entire reel with wilds
3. **Persistence**: In free game, store reel index in `self.expanding_wilds`
4. **Restoration**: On next spin, apply wilds to stored reel indices before drawing

### Super Spin Mechanics

Super spin is a "Hold & Win" style feature:

1. **Trigger**: Special bonus symbol (separate from free spin scatter)
2. **Initial state**: 3 spins, empty board
3. **Prize landing**: Prize symbols land with random values
4. **Sticky behavior**: Prizes remain on board, spin counter resets to 3
5. **Continuation**: Continue until 0 spins remaining
6. **Payout**: Sum of all collected prize values

### State Variables

```python
# Expanding wilds tracking
self.expanding_wilds: list[int]          # Reel indices with expanding wilds
self.available_reels: list[int]          # Reels available for new wilds

# Super spin tracking
self.sticky_positions: list[dict]        # Prize symbol positions
self.super_spin_win: float               # Cumulative prize total
self.total_free_spins: int               # Remaining spins (resets on prize)
```

## Files Overview

| File | Purpose | Lines |
|------|---------|-------|
| `game_state.py` | Game logic | ~400 |
| `game_config.py` | Configuration | ~150 |
| `game_events.py` | Custom events | ~80 |
| `game_optimization.py` | Optimization params | ~100 |
| `run.py` | Execution script | ~50 |

## Why Use This Template?

The expanding wilds template is ideal for:

1. **Complex bonus features**: Learn multi-stage game flow
2. **Sticky symbols**: Understand persistent board state
3. **Prize collection**: Implement "Hold & Win" mechanics
4. **Multiple bonus modes**: See how to structure separate game types
5. **Advanced features**: Study symbol attributes and custom events

## Common Modifications

### Add Multiplier Accumulation

```python
def accumulate_wild_multipliers(self, board: Board) -> int:
    """Sum all wild multipliers on board."""
    total_mult = 1
    for reel in board:
        for symbol in reel:
            if symbol.name == "W" and "multiplier" in symbol.attributes:
                total_mult *= symbol.attributes["multiplier"]
    return total_mult
```

### Progressive Prize Values

```python
def get_progressive_prize_value(self, spin_count: int) -> int:
    """Increase prize values as super spin progresses."""
    base_distribution = {10: 0.4, 20: 0.3, 50: 0.2, 100: 0.1}

    if len(self.sticky_positions) >= 10:
        # Boost values when many prizes collected
        return get_random_outcome({50: 0.5, 100: 0.3, 500: 0.2})

    return get_random_outcome(base_distribution)
```

### Expanding Wild Limits

```python
def can_add_expanding_wild(self, reel_idx: int) -> bool:
    """Limit maximum number of expanding wild reels."""
    max_expanding_reels = 3
    return (
        len(self.expanding_wilds) < max_expanding_reels
        and reel_idx not in self.expanding_wilds
    )
```

## Related Documentation

- [Lines Calculation](game-structure.md#win-calculations)
- [Symbol Attributes](game-structure.md#special-symbols)
- [Custom Events](events.md#custom-events)
- [Multi-Mode Games](running-games.md#bet-modes)
