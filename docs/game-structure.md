# Game Structure

This document explains the architecture and file organization of games in the Math SDK.

## Game Directory Layout

**New Architecture (Refactored - January 2026)**

Each game lives in `games/<game_name>/` with this simplified structure:

```
games/<game_name>/
  ├── run.py                    # Pure execution script (reads from TOML)
  ├── run_config.toml          # Runtime settings (threads, compression, pipeline)
  ├── game_config.py           # Game configuration and BetMode setup
  ├── gamestate.py             # ALL game logic in one file (~100-400 lines)
  ├── game_optimization.py     # Optimization parameters (optional)
  ├── game_events.py           # Custom event generation (optional, rare)
  ├── reels/                   # Reel strip CSV files (source files, committed)
  │   ├── base.csv
  │   ├── free.csv
  │   ├── wincap.csv
  │   └── ...
  ├── build/                   # Build output (generated, gitignored)
  │   ├── books/               # Simulation results (JSON/JSONL)
  │   ├── configs/             # Generated config files
  │   ├── forces/              # Force files for testing
  │   ├── lookup_tables/       # Lookup tables
  │   └── optimization_files/  # Optimization results
  └── tests/                   # Game-specific unit tests (optional)
      ├── run_tests.py
      └── test_*.py
```

### Key Changes from Old Architecture

**Removed (Old Structure):**
- ❌ `game_override.py` - Logic merged into `gamestate.py`
- ❌ `game_executables.py` - Logic merged into `gamestate.py`
- ❌ `game_calculations.py` - Logic merged into `gamestate.py`
- ❌ `library/` folder - Renamed to `build/` to match modern conventions

**Added (New Structure):**
- ✅ `run_config.toml` - TOML-based runtime configuration
- ✅ `gamestate.py` - Single consolidated file for all game logic
- ✅ `build/` folder - Clear separation of source vs generated artifacts

**Benefits:**
- **67% reduction** in inheritance complexity (6 → 2 layers)
- **75% reduction** in files per game (4 → 1 file per game)
- Easier to understand and maintain
- Single file contains all game-specific logic

## Class Inheritance Hierarchy

**New Simplified Architecture:**

Games follow a 2-layer inheritance chain:

```
GameState (src/state/game_state.py) ← base ABC
    ↓ inherited by
Board (src/calculations/board.py)
    ↓ inherited by (optional)
Tumble (src/calculations/tumble.py)
    ↓ inherited by
Game-specific GameState (games/<game_name>/game_state.py)
```

### Base Classes

**`GameState`** (src/state/game_state.py)
- Core simulation infrastructure (~850+ lines)
- Books management
- Event system with EventFilter integration
- State management
- Common actions (reset, special symbols, etc.)

**`Board`** (src/calculations/board.py)
- Random board generation
- Forced symbols
- Special symbol tracking
- Inherits from `GameState`

**`Tumble`** (src/calculations/tumble.py)
- Cascade/tumble mechanics
- For games with falling symbols
- Inherits from `Board`

**`GameState`** (games/<game_name>/gamestate.py)
- ALL game-specific logic in one file
- Organized into logical sections (see below)

## GameState File Structure

The `gamestate.py` file is organized into clear sections:

```python
from src.calculations.board import Board  # or Tumble

class GameState(Board):  # or Tumble
    """Game-specific logic for <game_name>"""

    # ============================================================
    # SECTION 1: SPECIAL SYMBOL HANDLERS
    # ============================================================
    def assign_special_sym_function(self):
        """Map symbols to handler functions"""
        self.special_symbol_functions = {
            "M": [self.assign_multiplier_property],
            "W": [self.handle_wild],
        }

    def assign_multiplier_property(self, symbol):
        """Assign multiplier to symbol"""
        multiplier = get_random_outcome(...)
        symbol.assign_attribute({"multiplier": multiplier})

    # ============================================================
    # SECTION 2: STATE MANAGEMENT OVERRIDES
    # ============================================================
    def reset_book(self):
        """Reset per-spin state"""
        super().reset_book()
        self.custom_state = 0

    # ============================================================
    # SECTION 3: GAME-SPECIFIC MECHANICS
    # ============================================================
    def check_bonus_trigger(self):
        """Check if bonus game should trigger"""
        scatter_count = self.board.count_symbol("scatter")
        return scatter_count >= 3

    # ============================================================
    # SECTION 4: WIN EVALUATION
    # ============================================================
    def evaluate_wins(self):
        """Calculate wins based on win_type"""
        if self.config.win_type == "cluster":
            self.cluster_wins()
        elif self.config.win_type == "lines":
            self.line_wins()

    # ============================================================
    # SECTION 5: MAIN GAME LOOPS
    # ============================================================
    def run_spin(self):
        """Main spin logic for base game"""
        self.draw_board()
        self.evaluate_wins()

        if self.check_bonus_trigger():
            self.run_freespin_from_base()

        return self.book

    def run_freespin(self):
        """Free spin logic"""
        self.draw_board()
        self.evaluate_wins()

        return self.book
```

### Typical File Size
- Simple games: ~100-150 lines
- Medium complexity: ~200-300 lines
- Complex games: ~300-400 lines

All in ONE readable file instead of scattered across 4+ files.

## Configuration System

### GameConfig Class

Located in `game_config.py`:

```python
from src.config.config import Config
from src.config.bet_mode import BetMode
from src.formatter import OutputMode

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

        # Output optimization (Phase 3)
        self.output_mode = OutputMode.COMPACT  # or OutputMode.VERBOSE
        self.simple_symbols = True
        self.compress_positions = True

        # BetModes
        self.betmodes = {
            "base": BetMode(...),
            "bonus": BetMode(...)
        }
```

### Run Configuration (TOML)

**New in January 2026:** Runtime settings separated into `run_config.toml`:

```toml
[execution]
num_threads = 10        # Python simulation threads
rust_threads = 20       # Rust optimization threads
batching_size = 50000   # Simulations per batch
compression = false     # Enable zstd compression
profiling = false       # Enable performance profiling

[simulation]
base = 10000           # Base game simulations
bonus = 10000          # Bonus game simulations

[pipeline]
run_sims = true            # Generate simulation books
run_optimization = false   # Run Rust optimization
run_analysis = false       # Generate PAR sheets
run_format_checks = true   # Run RGS verification

target_modes = ["base", "bonus"]

[analysis]
custom_keys = [{ symbol = "scatter" }]
```

**Benefits:**
- Clear separation: `game_config.py` = rules, `run_config.toml` = execution
- Easy to edit without touching code
- Multiple configs per game (dev/prod/test)

### BetMode System

Each game mode has its own configuration:

```python
from src.config.bet_mode import BetMode

self.betmodes = {
    "base": BetMode(
        reels={"base": "base.csv"},  # Reel file mapping
        distributions={
            "multiplier_values": [2, 3, 5, 10],
            "weights": [50, 30, 15, 5]
        },
        conditions={
            "min_scatters": 3,  # Trigger condition
        }
    ),
    "bonus": BetMode(
        reels={"free": "free.csv", "wincap": "wincap.csv"},
        # ... bonus-specific config
    )
}
```

## Event System

All events use constants from `src/events/constants.py`:

```python
from src.events.constants import EventConstants

# Create an event
event = {
    "index": len(self.book.events),
    "type": EventConstants.WIN.value,
    "amount": 1000,
    "details": [{"symbol": "A", "positions": [[0, 0], [0, 1]]}],
}

# Add to book (automatically filtered based on config)
self.book.add_event(event)
```

### Standard Event Types

- **Wins**: `WIN`, `SET_FINAL_WIN`, `SET_WIN`, `SET_TOTAL_WIN`, `WIN_CAP`
- **Free Spins**: `TRIGGER_FREE_SPINS`, `RETRIGGER_FREE_SPINS`, `END_FREE_SPINS`, `UPDATE_FREE_SPINS`
- **Tumbles**: `TUMBLE`, `SET_TUMBLE_WIN`, `UPDATE_TUMBLE_WIN`
- **Special**: `UPDATE_GLOBAL_MULTIPLIER`, `UPGRADE`, `REVEAL`

### Event Filtering (Phase 3.2)

Events are automatically filtered based on configuration:

```python
# In game_config.py
config.skip_derived_wins = True  # Skip SET_WIN, SET_TOTAL_WIN
config.skip_progress_updates = True  # Skip UPDATE_FREE_SPINS
config.verbose_event_level = "standard"  # "full", "standard", or "minimal"
```

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
   - Load `GameConfig` from `game_config.py`
   - Load `RunConfig` from `run_config.toml`
   - Create `GameState` instance
   - Set up reel strips and distributions

2. **Run Simulations**
   - `create_books()` from `src/state/run_sims`
   - Runs N simulations per bet mode

3. **Single Simulation**
   ```
   run_spin()
     ↓
   draw_board()
     ↓
   evaluate_wins()
     ↓
   check_triggers()
     ↓
   run_freespin() (if triggered)
     ↓
   store_events()
   ```

4. **Books Generation**
   - Write simulation results to `build/books/`
   - Generate probability CSV files
   - Optional: Format, compress, verify

## Build Output Structure

The `build/` folder contains all generated artifacts:

```
games/<game_name>/build/
  ├── books/                      # Simulation results
  │   ├── <game>_base_books.json
  │   ├── <game>_base_probs.csv
  │   └── ...
  ├── configs/                    # Generated config files
  ├── forces/                     # Force files for optimization
  ├── lookup_tables/              # Lookup tables
  ├── optimization_files/         # Optimization results
  └── temp_multi_threaded_files/  # Temporary files
```

All `build/` contents are gitignored - these are generated artifacts, not source files.

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

### 3. Update Run Config

Edit `games/my_new_game/run_config.toml`:
```toml
[simulation]
base = 1000  # Start small for testing

[execution]
compression = false  # Readable output for debugging

[pipeline]
run_sims = true
run_optimization = false  # Disable initially
run_analysis = false
```

### 4. Create Reel Strips

Create CSV files in `games/my_new_game/reels/`:
```csv
# base.csv
A,K,Q,J,10,9,A,K,Q,J
K,Q,J,10,9,A,K,Q,J,10
# ... (num_rows × num_reels)
```

### 5. Implement Game Logic

Edit `games/my_new_game/gamestate.py`:
```python
from src.calculations.board import Board

class GameState(Board):
    """My new game logic"""

    def assign_special_sym_function(self):
        """Define special symbols"""
        self.special_symbol_functions = {
            "M": [self.assign_mult],
        }

    def evaluate_wins(self):
        """Calculate wins"""
        if self.config.win_type == "cluster":
            self.cluster_wins()

    def run_spin(self):
        """Main game loop"""
        self.draw_board()
        self.evaluate_wins()
        return self.book

    def run_freespin(self):
        """Free spin loop"""
        self.draw_board()
        self.evaluate_wins()
        return self.book
```

### 6. Test

```bash
# Small test run
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

### Single File Organization
```python
# ✅ Good - all logic in gamestate.py, organized by sections
class GameState(Board):
    # Special symbols section
    def assign_special_sym_function(self): ...

    # Mechanics section
    def check_bonus(self): ...

    # Game loops section
    def run_spin(self): ...

# ❌ Bad - don't split into multiple files
# game_override.py, game_executables.py, etc.
```

### Use Distributions
```python
# ✅ Good - use distributions from config
multiplier = get_random_outcome(
    self.get_current_distribution_conditions()["multiplier_values"]
)

# ❌ Bad - hardcoded random
multiplier = random.choice([2, 3, 5, 10])
```

### Configuration vs Execution Settings
```python
# ✅ Good - game rules in game_config.py
class GameConfig(Config):
    self.paytable = {...}
    self.rtp = 0.97

# ✅ Good - execution settings in run_config.toml
[simulation]
base = 10000

# ❌ Bad - don't mix concerns
```

## Migration from Old Architecture

If you have an old game with multiple files:

1. **Merge files into gamestate.py**:
   - Copy special symbol functions from `game_override.py`
   - Copy win calculation from `game_executables.py`
   - Copy helper functions from `game_calculations.py`
   - Copy game loops from `game_state.py`

2. **Organize into sections** (see GameState File Structure above)

3. **Update inheritance**: `GameState(Board)` instead of `GameState(GameStateOverride)`

4. **Test thoroughly**: `make run GAME=<game>` and `make unit-test GAME=<game>`

See [Migration History](migration-history.md) for complete refactoring details.

## See Also

- [Running Games](running-games.md) - How to run simulations
- [Event System](events.md) - Working with events
- [Optimization](optimization.md) - Optimizing distributions
- [Migration History](migration-history.md) - Complete refactoring story
- [CLAUDE.md](../CLAUDE.md) - Comprehensive technical reference
