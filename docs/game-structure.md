# Game Structure

This document explains the architecture and file organization of games in the Math SDK.

## Game Directory Layout

Each game lives in `games/<game_name>/` with this structure:

```
games/<game_name>/
  ├── run.py                    # Main entry point
  ├── game_config.py           # Configuration and BetMode setup
  ├── gamestate.py             # Game loop (run_spin, run_freespin)
  ├── game_override.py         # Override base State methods
  ├── game_executables.py      # Win calculation logic
  ├── game_optimization.py     # Optimization parameters
  ├── game_events.py           # Custom event generation (optional)
  ├── game_calculations.py     # Helper calculations (optional)
  ├── reels/                   # Reel strip CSV files
  │   ├── base_reels.csv
  │   └── bonus_reels.csv
  ├── library/                 # Game-specific modules (optional)
  └── tests/                   # Game-specific unit tests
      ├── run_tests.py
      └── test_*.py
```

## Class Inheritance Hierarchy

Games follow this inheritance chain:

```
GameState (gamestate.py)
    ↓ inherits from
GameStateOverride (game_override.py)
    ↓ inherits from
GameExecutables (game_executables.py)
    ↓ inherits from
State (src/state/state.py)
```

### Purpose of Each Layer

**`gamestate.py`** - Main game loop
```python
class GameState(GameStateOverride):
    def run_spin(self):
        """Main spin logic for base game"""
        self.draw_board()
        self.calculate_wins()
        if self.check_fs_condition():
            self.run_freespin_from_base()

    def run_freespin(self):
        """Free spin logic"""
        # Free spin specific logic
```

**`game_override.py`** - Override specific behaviors
```python
class GameStateOverride(GameExecutables):
    def reset_game_state(self):
        """Custom reset logic"""
        super().reset_game_state()
        # Additional game-specific resets

    def assign_special_sym_function(self):
        """Define special symbol behaviors"""
        self.special_symbol_functions = {
            "M": [self.assign_mult_property]
        }
```

**`game_executables.py`** - Win calculation
```python
class GameExecutables(State):
    def calculate_wins(self):
        """Game-specific win calculation"""
        if self.config.win_type == "cluster":
            self.cluster_wins()
        elif self.config.win_type == "lines":
            self.line_wins()
```

**`State`** (base class) - Universal simulation infrastructure
- Books management
- Event system
- Win tracking
- Board operations

## Configuration System

### GameConfig Class

Located in `game_config.py`:

```python
from src.config.config import Config

class GameConfig(Config):
    def __init__(self):
        super().__init__()

        # Basic settings
        self.game_id = "tower_treasures"
        self.game_name = "Tower Treasures"
        self.win_type = "cluster"  # or "lines", "ways", "scatter"
        self.rtp = 0.9700

        # Board dimensions
        self.num_reels = 5
        self.num_rows = 3

        # Paytable
        self.paytable = {
            "A": {5: 50, 4: 20, 3: 5},
            "K": {5: 40, 4: 15, 3: 4},
            # ...
        }

        # BetModes
        self.betmodes = {
            "base": BetMode(...),
            "bonus": BetMode(...)
        }
```

### BetMode System

Each game mode has its own configuration:

```python
from src.config.betmode import BetMode

self.betmodes = {
    "base": BetMode(
        reel_file="reels/base_reels.csv",
        distributions={
            "mult_values": [2, 3, 5, 10],  # Multiplier values
            "weights": [50, 30, 15, 5]      # Corresponding weights
        },
        conditions={
            "min_scatters": 3,  # Trigger condition
        }
    ),
    "bonus": BetMode(
        reel_file="reels/bonus_reels.csv",
        # ... bonus-specific config
    )
}
```

## Event System

All events use constants from `src/events/event_constants.py`:

```python
from src.events.event_constants import EventConstants
from src.events.events import construct_event

# Create an event
event = construct_event(
    event_type=EventConstants.WIN.value,
    amount=10.0,
    details={"symbols": ["A"], "positions": [[0,0], [0,1]]}
)

# Add to book
self.book.add_event(event)
```

### Standard Event Types

- **Wins**: `WIN`, `SET_FINAL_WIN`, `SET_WIN`, `SET_TOTAL_WIN`, `WIN_CAP`
- **Free Spins**: `TRIGGER_FREE_SPINS`, `RETRIGGER_FREE_SPINS`, `END_FREE_SPINS`
- **Tumbles**: `TUMBLE_BOARD`, `SET_TUMBLE_WIN`, `UPDATE_TUMBLE_WIN`
- **Special**: `UPDATE_GLOBAL_MULT`, `UPGRADE`, `REVEAL`

## Win Calculation Types

The SDK supports multiple win calculation methods:

### Cluster Pay
```python
# game_config.py
self.win_type = "cluster"

# Uses src/calculations/cluster.py
# Adjacent matching symbols form winning clusters
```

### Line Pay
```python
# game_config.py
self.win_type = "lines"
self.paylines = [
    [1, 1, 1, 1, 1],  # Middle line
    [0, 0, 0, 0, 0],  # Top line
    # ...
]

# Uses src/calculations/lines.py
# Symbols along defined paylines
```

### Ways Pay
```python
# game_config.py
self.win_type = "ways"

# Uses src/calculations/ways.py
# Left-to-right matching symbols (any position)
```

### Scatter Pay
```python
# Uses src/calculations/scatter.py
# Scatter symbols anywhere on board
```

## Simulation Flow

1. **Initialization**
   - Load `GameConfig`
   - Create `GameState` instance
   - Set up reel strips and distributions

2. **Run Simulations**
   - `create_books()` from `src/state/run_sims`
   - Runs N simulations per betmode

3. **Single Simulation**
   ```
   run_spin()
     ↓
   draw_board()
     ↓
   calculate_wins()
     ↓
   check_triggers()
     ↓
   run_freespin() (if triggered)
     ↓
   store_events()
   ```

4. **Books Generation**
   - Write simulation results to JSON/JSONL
   - Generate probability CSV files
   - Optional: Format, compress, verify

## Special Symbol Functions

Define special symbol behaviors in `game_override.py`:

```python
def assign_special_sym_function(self):
    """Map symbols to functions that run when they appear"""
    self.special_symbol_functions = {
        "M": [self.assign_mult_property],  # Multiplier symbol
        "W": [self.handle_wild_symbol],     # Wild symbol
        "S": []                             # Scatter (handled separately)
    }

def assign_mult_property(self, symbol):
    """Assign random multiplier to symbol"""
    mult = get_random_outcome(
        self.get_current_distribution_conditions()["mult_values"][self.gametype]
    )
    symbol.assign_attribute({"multiplier": mult})
```

## Creating a New Game

### 1. Copy Template

```bash
cp -r games/template/ games/my_new_game/
```

### 2. Update Config

Edit `games/my_new_game/game_config.py`:
```python
self.game_id = "my_new_game"
self.game_name = "My New Game"
self.win_type = "cluster"  # Choose win type
# ... configure paytable, betmodes, etc.
```

### 3. Create Reel Strips

Create CSV files in `games/my_new_game/reels/`:
```csv
position,symbol,weight
0,A,10
0,K,20
0,Q,30
1,A,15
# ...
```

### 4. Implement Game Logic

Edit `games/my_new_game/gamestate.py`:
```python
def run_spin(self):
    self.draw_board()
    self.calculate_wins()

    # Custom game logic
    if self.check_bonus_trigger():
        self.run_bonus_game()

    return self.book
```

### 5. Test

```bash
# Small test run
# Edit run.py: num_sim_args = {"base": 1000}
make run GAME=my_new_game

# Run tests
make unit-test GAME=my_new_game
```

## Best Practices

### Use EventConstants
```python
# ✅ Good
event_type=EventConstants.WIN.value

# ❌ Bad
event_type="win"
```

### Override in game_override.py
```python
# ✅ Good - override in game_override.py
class GameStateOverride(GameExecutables):
    def reset_game_state(self):
        super().reset_game_state()
        # Custom logic

# ❌ Bad - don't modify base State class
```

### Keep win logic in game_executables.py
```python
# ✅ Good - win logic in executables
class GameExecutables(State):
    def calculate_wins(self):
        # Win calculation logic
```

### Use distributions for random values
```python
# ✅ Good - use distributions
mult = get_random_outcome(
    self.config.betmodes[self.gametype].distributions["mult_values"]
)

# ❌ Bad - hardcoded random
mult = random.choice([2, 3, 5, 10])
```

## See Also

- [Running Games](running-games.md) - How to run simulations
- [Event System](events.md) - Working with events
- [Optimization](optimization.md) - Optimizing distributions
