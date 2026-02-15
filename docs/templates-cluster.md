# Cluster Template

**Location**: `games/template_cluster/`
**Win Type**: Cluster-pay
**Inheritance**: `GameState` → `Tumble` → `Board` → `GameState` (base, `src/state/game_state.py`)

## Overview

The cluster template implements a modern cascade-style slot game where wins are formed by adjacent matching symbols. Winning symbols are removed and new symbols tumble down, potentially creating chain reactions. The game features grid position multipliers that increase with consecutive wins during free spins.

## Game Mechanics

### Core Features

- **Cluster-pay wins**: Matching symbols must be adjacent (horizontally/vertically)
- **Tumble mechanics**: Winning symbols removed, new symbols fall down
- **Grid multipliers**: Position-based multipliers that increase with wins
- **Free spin mode**: Scatter triggers, persistent grid multipliers

### Board Configuration

```python
self.num_reels = 7
self.num_rows = [7] * self.num_reels  # 7×7 grid
self.win_type = "cluster"
```

### Paytable Structure

Cluster pays use tier-based paytables:

```python
t1, t2, t3, t4 = (5, 5), (6, 8), (9, 12), (13, 36)
pay_group = {
    (t1, "H1"): 5.0,   # 5 matching symbols = 5x
    (t2, "H1"): 12.5,  # 6-8 symbols = 12.5x
    (t3, "H1"): 25.0,  # 9-12 symbols = 25x
    (t4, "H1"): 60.0,  # 13-36 symbols = 60x
    ...
}
```

The first element in each tuple defines the range (min, max) of matching symbols.

## Game-Specific Implementation

### State Management

```python
def reset_book(self) -> None:
    """Reset state for new simulation."""
    super().reset_book()
    self.tumble_win = 0  # Track cumulative tumble wins

def reset_free_spin(self) -> None:
    """Initialize free spin mode."""
    super().reset_free_spin()
    self.reset_grid_multipliers()  # Start with fresh multipliers
```

### Main Game Loop

The `run_spin()` method implements the tumble cycle:

1. Draw initial board
2. Find cluster wins
3. Apply grid multipliers
4. Remove winning symbols
5. Tumble new symbols
6. Repeat steps 2-5 until no more wins
7. Check for free spin triggers

```python
def run_spin(self) -> Board:
    """Execute a single base game spin with tumbles."""
    board = self.draw_board()
    self.book.add_event(reveal_board_multipliers_event(self))

    # Initial cluster calculation
    cluster_calc = Cluster(board, self)
    wins = cluster_calc.calculate_cluster_wins()

    # Tumble loop
    while wins:
        self.apply_multiplier(wins)
        board = self.tumble_board(wins)
        cluster_calc = Cluster(board, self)
        wins = cluster_calc.calculate_cluster_wins()

    # Check scatter triggers
    if self.check_free_spin_condition():
        self.run_free_spin_from_base()

    return board
```

### Grid Multipliers

Grid multipliers track which positions contributed to wins:

```python
def apply_multiplier(self, wins: list) -> None:
    """Apply grid multipliers to wins and increment counters.

    Each winning position's multiplier increases for subsequent tumbles.
    """
    for win in wins:
        for position in win["positions"]:
            multiplier = self.grid_multipliers[position[0]][position[1]]
            win["amount"] *= multiplier
            self.grid_multipliers[position[0]][position[1]] += 1
```

## Custom Functions

### Grid Multiplier Management

```python
def reset_grid_multipliers(self) -> None:
    """Initialize all grid positions to 1x multiplier."""
    self.grid_multipliers = [
        [1 for _ in range(self.config.num_rows[i])]
        for i in range(self.config.num_reels)
    ]
```

### Free Spin Triggers

```python
def check_free_spin_condition(self) -> bool:
    """Check if scatter count meets trigger requirement."""
    scatter_count = sum(
        1 for symbol in self.board.flatten()
        if symbol.name == "scatter"
    )
    return scatter_count >= self.config.scatter_trigger_count
```

## Custom Events

The template includes custom events defined in `game_events.py`:

```python
def reveal_board_multipliers_event(game_state) -> dict:
    """Emit grid multiplier state at spin start."""
    return {
        "type": "REVEAL_BOARD_MULTIPLIERS",
        "multipliers": game_state.grid_multipliers
    }
```

## Configuration Files

### Run Configuration (`dev.toml`)

```toml
[execution]
num_threads = 10
compression = false

[simulation]
base = 100           # Fast iteration for development
bonus = 100

[pipeline]
run_sims = true
run_optimization = false  # Skip optimization for speed
run_analysis = false
```

### Bet Modes

The game supports multiple bet modes with different distributions:

```python
self.bet_modes = {
    "base": BetMode(
        reels_file="base.csv",
        distributions={"scatter_trigger": {3: 1.0}}
    ),
    "free": BetMode(
        reels_file="free.csv",
        distributions={"scatter_trigger": {3: 1.0}}
    )
}
```

## Usage Example

```bash
# Run with default config (dev.toml via symlink)
make run GAME=template_cluster

# Run with production config
make run GAME=template_cluster CONFIG=prod.toml

# Run unit tests
make unit-test GAME=template_cluster
```

## Key Implementation Details

### Tumble Inheritance

This template inherits from `Tumble` class, which provides:
- `tumble_board()`: Remove symbols and drop new ones
- `tumble_win` tracking
- Tumble-specific event emission

### Win Calculation

Uses `Cluster` class from `src/calculations/cluster.py`:
- Breadth-first search for adjacent symbols
- Diagonal adjacency detection
- Cluster size calculation

### State Variables

- `tumble_win`: Cumulative win amount across tumbles
- `grid_multipliers`: 2D array of position multipliers
- `triggered_free_game`: Boolean for free spin activation

## Files Overview

| File | Purpose | Lines |
|------|---------|-------|
| `game_state.py` | All game logic | ~150 |
| `game_config.py` | Configuration | ~100 |
| `game_events.py` | Custom events | ~30 |
| `game_optimization.py` | Optimization params | ~80 |
| `run.py` | Execution script | ~50 |

## Related Documentation

- [Tumble Mechanics](game-structure.md#tumble-mechanics)
- [Cluster Calculation](game-structure.md#win-calculations)
- [Event System](events.md)
