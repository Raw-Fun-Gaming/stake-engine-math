# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the Stake Engine Math SDK - a Python-based engine for defining slot game rules, simulating outcomes, and optimizing win distributions. It generates backend configuration files, lookup tables, and simulation results for online casino games.

**Key characteristics:**
- Python 3.12+ required
- Rust/Cargo required for optimization algorithm
- **Refactored architecture (Jan 2026)**: Simplified from 6-layer to 2-layer inheritance
- Game-specific state machines in single consolidated files
- Event-driven architecture with standardized event constants
- Cluster/Lines/Ways/Scatter pay calculation systems

**Recent Major Refactoring (Phase 1-2, Jan 2026):**
- ✅ **Flattened inheritance**: 6 layers → 2 layers (67% reduction)
- ✅ **Simplified games**: 4 files → 1 file per game (75% reduction)
- ✅ **Type hints**: 180+ functions with comprehensive type annotations
- ✅ **Documentation**: 120+ docstrings with examples
- ✅ **Code quality**: Constants, enums, custom exceptions
- ✅ **All games migrated**: 7 games verified working with new structure

**Output Optimization (Phase 3, Jan 2026):**
- ✅ **Output compression**: 27.9% file size reduction via OutputFormatter (Phase 3.1)
- ✅ **Event filtering**: 10-15% additional reduction via EventFilter (Phase 3.2)
- ✅ **Combined savings**: 35-40% total file size reduction from baseline
- ✅ **Performance**: 13% faster generation with compact mode
- ✅ **Backward compatible**: All optimizations opt-in, defaults to verbose
- ✅ **Production ready**: Fully tested (54 tests), RGS verified

## Build and Development Commands

### Setup and Installation
```bash
make setup                          # Setup virtual environment and install all dependencies
source env/bin/activate            # Activate virtual environment (macOS/Linux)
```

### Running Games
```bash
make run GAME=<game_name>          # Run game simulation (e.g., make run GAME=tower_treasures)
                                   # Automatically formats JSON output if compression=False
```

### Testing
```bash
make test                          # Run main project tests (pytest)
make unit-test GAME=<game_name>    # Run game-specific unit tests (e.g., make unit-test GAME=tower_treasures)
pytest tests/                      # Alternative: run pytest directly
```

### Rust Optimization Program
```bash
cd optimization_program
cargo build --release              # Build optimization algorithm
cargo run --release                # Run optimization
```

The optimization program reads configuration from `optimization_program/src/setup.txt`.

## High-Level Architecture

### Game Structure Hierarchy

**New Architecture (as of Phase 1.3 refactoring - Jan 2026):**

Each game lives in `games/<game_name>/` with a simplified inheritance chain:

```
GameState (games/<game_name>/gamestate.py)
    ↓ inherits from
Board (src/calculations/board.py) or Tumble (src/calculations/tumble.py)
    ↓ inherits from
BaseGameState (src/state/base_game_state.py)
```

**Key improvements:**
- **Single file per game**: All game logic consolidated in `gamestate.py` (~100-400 lines)
- **Reduced complexity**: Inheritance reduced from 6 layers to 2 layers (67% reduction)
- **Clear organization**: Game files divided into logical sections:
  - Special symbol handlers
  - State management overrides
  - Game-specific mechanics
  - Win evaluation
  - Main game loops (`run_spin()`, `run_freespin()`)

**Base Classes:**
- `BaseGameState`: Core simulation infrastructure (books, events, state management, common actions)
- `Board`: Random board generation, forced symbols, special symbol tracking
- `Tumble`: Cascade/tumble mechanics (optional, only for games with falling symbols)

### Configuration System

Each game has a `game_config.py` that inherits from `src.config.config.Config`:

```python
class GameConfig(Config):
    def __init__(self):
        super().__init__()
        self.game_id = "tower_treasures"
        self.win_type = "cluster"  # or "lines", "ways", "scatter"
        self.rtp = 0.9700
        self.paytable = {...}
        # ... game-specific configuration
```

**Key config attributes:**
- `win_type`: Determines win calculation method (cluster/lines/ways/scatter)
- `paytable`: Win multipliers for symbol combinations
- `num_reels`, `num_rows`: Board dimensions
- `betmodes`: Different game modes (base/bonus) with distinct distributions

**Output Optimization Configuration (Phase 3):**
```python
# Phase 3.1: Output Compression
config.output_mode = OutputMode.COMPACT  # or OutputMode.VERBOSE (default)
config.compress_symbols = True  # "L5" instead of {"name": "L5"}
config.compress_positions = True  # [0, 2] instead of {"reel": 0, "row": 2}
config.include_losing_boards = False  # Skip board reveals with zero wins
config.skip_implicit_events = True  # Skip redundant zero-amount events

# Phase 3.2: Event Filtering
config.skip_derived_wins = True  # Skip SET_WIN, SET_TOTAL_WIN (calculable from WIN events)
config.skip_progress_updates = True  # Skip UPDATE_FREE_SPINS, UPDATE_TUMBLE_WIN
config.verbose_event_level = "standard"  # "full" (default), "standard", or "minimal"
```

**Impact:**
- COMPACT mode: 27.9% file size reduction, 13% faster generation
- With event filtering: Additional 10-15% reduction
- **Total: 35-40% file size savings** (e.g., 18.89 MB → 11-12 MB per 10K simulations)

### BetMode and Distribution System

Games have multiple bet modes (base game, bonus game, etc.) each with their own:
- **Reel strips** (`games/<game_name>/reels/`)
- **Distributions** (symbol probabilities, multiplier values)
- **Win conditions** (free spin triggers, scatter requirements)

The `BetMode` class (defined in `game_config.py`) structures this:
```python
self.betmodes = {
    "base": BetMode(...),
    "bonus": BetMode(...)
}
```

### Event System

All game events use standardized constants from `src/events/event_constants.py`:

```python
from src.events.event_constants import EventConstants

# Use constants instead of hardcoded strings
event = {
    "type": EventConstants.WIN.value,  # NOT "win"
    "amount": 10.0
}
```

**Standard event types:**
- Win events: `WIN`, `SET_FINAL_WIN`, `SET_WIN`, `SET_TOTAL_WIN`, `WIN_CAP`
- Free spins: `TRIGGER_FREE_SPINS`, `RETRIGGER_FREE_SPINS`, `END_FREE_SPINS`
- Tumbles: `TUMBLE_BOARD`, `SET_TUMBLE_WIN`, `UPDATE_TUMBLE_WIN`
- Special: `UPDATE_GLOBAL_MULT`, `UPGRADE`, `REVEAL`

**Event Filtering (Phase 3.2):**

Events are automatically filtered based on configuration via the `EventFilter` class:

- **REQUIRED events** (always emitted): `WIN`, `REVEAL`, triggers, tumbles, upgrades
- **STANDARD events** (emit by default): `SET_WIN`, `SET_TOTAL_WIN`, `WIN_CAP`, `END_FREE_SPINS`
- **VERBOSE events** (optional): `UPDATE_FREE_SPINS`, `UPDATE_TUMBLE_WIN`, `SET_TUMBLE_WIN`

Filtering is applied automatically when events are added to books via `book.add_event()`. All games inherit this functionality through `BaseGameState`.

### Win Calculation Modules

Located in `src/calculations/`:
- `cluster.py`: Cluster-pay games (adjacent matching symbols)
- `lines.py`: Line-pay games (traditional paylines)
- `ways.py`: Ways-pay games (left-to-right ways)
- `scatter.py`: Scatter symbol detection

Games specify their win type in config and call the appropriate calculation method.

### Simulation Flow

1. **Initialization**: Load `GameConfig`, create `GameState` instance
2. **Run simulations**: `create_books()` (from `src.state.run_sims`) runs N simulations
3. **Books generation**: Outcomes stored in "books" files (JSON/JSONL with simulation results)
4. **Optimization** (optional): Rust program optimizes win distributions
5. **Analysis** (optional): Generate PAR sheets and statistics
6. **Verification**: RGS verification tests validate output format

Each simulation:
- `run_spin()` → Draw board → Calculate wins → Check triggers → Store events
- Free spins use `run_freespin()` with separate loop

### Books and Output Files

Simulation results go to `games/<game_name>/` as "books" files:
- Format: JSON (if `output_regular_json=True`) or JSONL
- Compression: zstd (if `compression=True` in `run.py`)
- Auto-formatting: When `compression=False`, Makefile runs `scripts/format_books_json.py`

**The formatter:**
- Pretty-prints complex objects
- Keeps simple objects like `{"name": "L1"}` on single lines
- Can reconstruct corrupted JSONL files

### Optimization System

The Rust optimization program (`optimization_program/`) uses genetic algorithms to adjust win distributions:

**Configuration flow:**
1. Define `OptimizationSetup` in `games/<game_name>/game_optimization.py`
2. Specify conditions (RTP targets, hit rates) and scaling factors
3. Write setup to `optimization_program/src/setup.txt`
4. Run optimization: `OptimizationExecution(...)` in game's `run.py`

**Key optimization concepts:**
- **Conditions**: Target RTP, hit rate (HR), average win constraints
- **Scaling**: Adjust specific win ranges (e.g., scale 10-20x wins by 1.5)
- **Search conditions**: Find specific outcomes (symbols, event types)

## File Structure Reference

**New Structure (Refactored Architecture):**

```
games/<game_name>/
  ├── run.py                    # Main entry point: simulation, optimization, analysis
  ├── game_config.py           # Game configuration and BetMode setup
  ├── gamestate.py             # ALL game logic in one file (~100-400 lines)
  │                            # Sections: special symbols, state management,
  │                            # mechanics, win evaluation, game loops
  ├── game_optimization.py     # Optimization parameters (optional)
  ├── game_events.py           # Custom event generation (optional, rare)
  ├── reels/                   # Reel strip files (CSV) per betmode
  ├── library/                 # Game-specific modules (optional, rare)
  └── tests/                   # Game-specific unit tests (optional)
      ├── run_tests.py         # Test runner
      └── test_*.py            # Individual test modules

src/                           # Universal SDK modules
  ├── state/
  │   ├── base_game_state.py   # ⭐ NEW: Unified base class (850+ lines)
  │   ├── books.py             # Book class with EventFilter integration
  │   ├── state.py             # Legacy compatibility layer
  │   └── run_sims.py          # Simulation runner
  ├── calculations/
  │   ├── board.py             # Board generation (inherits from BaseGameState)
  │   ├── tumble.py            # Tumble/cascade mechanics (optional)
  │   ├── cluster.py           # Cluster-pay calculations
  │   ├── lines.py             # Line-pay calculations
  │   ├── ways.py              # Ways-pay calculations
  │   └── scatter.py           # Scatter-pay calculations
  ├── config/                  # Configuration classes
  ├── events/                  # Event system and constants
  │   ├── event_constants.py   # Standardized event type constants
  │   ├── event_filter.py      # ⭐ NEW: Event filtering (Phase 3.2)
  │   └── events.py            # Event generation functions
  ├── output/                  # ⭐ NEW: Output optimization (Phase 3.1)
  │   └── output_formatter.py  # OutputFormatter for compression
  ├── wins/                    # Win manager
  ├── constants.py             # ⭐ NEW: GameMode, WinType enums
  ├── exceptions.py            # ⭐ NEW: Custom exception hierarchy
  └── write_data/              # Output file generation

optimization_program/          # Rust optimization algorithm
  └── src/
      ├── main.rs              # Optimization engine
      └── setup.toml           # Optimization config (TOML format)

utils/                         # Analysis and verification tools
  ├── game_analytics/          # PAR sheet generation, statistics
  └── rgs_verification.py      # Output format validation
```

**Key Changes from Old Structure:**
- ❌ Removed: `game_override.py`, `game_executables.py`, `game_calculations.py` per game
- ✅ Simplified: All game logic now in single `gamestate.py` file
- ✅ Added: `BaseGameState` unified base class
- ✅ Added: Constants and exceptions modules
- ✅ Added: `output/` directory with OutputFormatter (Phase 3.1)
- ✅ Added: EventFilter in `events/` (Phase 3.2)

## Important Development Guidelines

### When Adding a New Game

1. Copy `games/template/` to `games/<new_game>/`
2. Update `game_config.py`: Set `game_id`, `game_name`, `win_type`, paytable
3. Create reel strips in `reels/` directory (CSV format)
4. Implement game logic in `gamestate.py`:
   - Add special symbol handlers in the designated section
   - Override state management methods if needed (e.g., `reset_book()`)
   - Implement game-specific mechanics
   - Add win evaluation logic
   - Complete `run_spin()` and `run_freespin()` methods
5. Test with small simulation: Set `num_sim_args = {"base": 1000}` in `run.py`

**Note**: The new architecture consolidates all game logic in a single `gamestate.py` file. No need for separate `game_override.py`, `game_executables.py`, or `game_calculations.py` files.

### When Modifying Game Logic

- Always use `EventConstants` for event types, never hardcoded strings
- All game logic is in `gamestate.py` - modify methods in their designated sections
- Test changes with unit tests: `make unit-test GAME=<game_name>`
- For win calculation changes, modify the win evaluation section in `gamestate.py`
- Follow the section structure from the template for consistency

### Common Patterns

**Adding a custom event:**
```python
from src.events.event_constants import EventConstants
from src.events.events import construct_event

event = construct_event(
    event_type=EventConstants.REVEAL.value,
    details={"symbol": "scatter", "positions": [1, 2, 3]}
)
self.book.add_event(event)
```

**Special symbol with attributes:**
```python
def assign_special_sym_function(self):
    self.special_symbol_functions = {
        "M": [self.assign_mult_property]
    }

def assign_mult_property(self, symbol):
    multiplier = get_random_outcome(
        self.get_current_distribution_conditions()["mult_values"][self.gametype]
    )
    symbol.assign_attribute({"multiplier": multiplier})
```

**Checking win conditions:**
```python
if self.check_fs_condition() and self.check_freespin_entry():
    self.run_freespin_from_base()
```

### Testing

- **Main tests**: `pytest tests/` - SDK-wide functionality tests
- **Game unit tests**: Each game can have `tests/` directory with isolated tests
- **Integration testing**: Run full simulation with `make run GAME=<game>`
- **RGS verification**: Automatically runs format checks if `run_format_checks=True` in `run.py`

### JSON Formatting

When `compression = False` in `run.py`, the Makefile automatically formats books files:
- Script: `scripts/format_books_json.py`
- Keeps simple objects compact: `{"name": "L1"}`
- Pretty-prints complex structures for readability
- Handles JSONL and JSON formats

### Optimization Setup

The `game_optimization.py` file configures optimization per betmode:

```python
"base": {
    "conditions": {
        "basegame": ConstructConditions(hr=3.5, rtp=0.59).return_dict(),
        "freegame": ConstructConditions(rtp=0.37, hr=200,
                                       search_conditions={"symbol": "scatter"}).return_dict(),
    },
    "scaling": ConstructScaling([...]).return_dict(),
    "parameters": ConstructParameters(
        num_show=5000,        # Number of top outcomes to show
        num_per_fence=10000,  # Population size per optimization group
        test_spins=[50, 100, 200],  # Test spin counts
        score_type="rtp"      # Optimization scoring method
    ).return_dict()
}
```

**Before running optimization:**
- Verify simulation books exist (run with `run_sims=True` first)
- Check optimization parameters in `game_optimization.py`
- Ensure Rust toolchain is installed: `cargo --version`

## Documentation

- Main docs: `docs/` directory (MkDocs format)
- Online docs: https://stakeengine.github.io/math-sdk/
- View locally: `mkdocs serve` (requires MkDocs installation)

## Key Dependencies

- **numpy**: Array operations, statistics
- **zstandard**: Compression for books files
- **boto3**: AWS S3 uploads (optional)
- **xlsxwriter**: Excel PAR sheet export
- **pytest**: Testing framework
- **rust_decimal, rayon, serde_json**: Rust optimization dependencies

## Notes

- The SDK uses a virtual environment (`env/`). Always activate before development.
- Reels are stored as CSV files with symbol weights per position.
- The `BetMode` system allows different symbol distributions for base/bonus games.
- Force files can override specific outcomes for testing (see `src/write_data/force.py`).
- Each game is a singleton (`_instance` pattern) to prevent duplicate initialization.
