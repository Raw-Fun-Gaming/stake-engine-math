# Stake Engine Math SDK

The Math SDK is a Python-based engine for defining game rules, simulating outcomes, and optimizing win distributions. It generates all necessary backend and configuration files, lookup tables, and simulation results.

## 🎉 Major Architecture Refactoring & Optimization (January 2026)

The codebase has undergone a comprehensive refactoring and optimization (Phases 1-3) that dramatically simplifies the architecture, improves maintainability, and significantly reduces output file sizes:

### Key Improvements

**Phase 1-2: Architecture Refactoring**
- **🏗️ Flattened Inheritance**: Reduced from 6 layers to 2 layers (67% reduction in complexity)
- **📁 Simplified Structure**: Games now use 1 file instead of 4 (75% reduction)
- **📝 Comprehensive Type Hints**: 180+ functions with full type annotations
- **📚 Rich Documentation**: 120+ docstrings with examples and usage guidance
- **🛡️ Better Error Handling**: Custom exception hierarchy with clear error messages
- **🔤 Modern Code Quality**: Enums, constants, and standardized patterns
- **✅ Fully Tested**: All 7 games migrated and verified working

**Phase 3: Output Optimization (NEW!)**
- **🗜️ Smart Compression**: 27.9% file size reduction via intelligent output formatting
- **⚡ Faster Generation**: 13% speed improvement with compact mode
- **🎯 Event Filtering**: Additional 10-15% reduction through selective event emission
- **📊 Combined Savings**: 35-40% total file size reduction (e.g., 18.89 MB → 11-12 MB per 10K sims)
- **🔄 Backward Compatible**: All optimizations are opt-in, defaults to verbose mode
- **✅ Production Ready**: Fully tested (54 tests passing), RGS verified

### What Changed

**Before:**
```
games/<game>/
  ├── gamestate.py
  ├── game_override.py
  ├── game_executables.py
  └── game_calculations.py
```

**After:**
```
games/<game>/
  └── gamestate.py  # All game logic in one file (~100-400 lines)
```

**Benefits:**
- Easier to understand - all game logic in one place
- Easier to debug - no jumping between 4+ files
- Easier to maintain - changes don't require coordinating across layers
- Easier to create new games - clear, self-contained template

See [REFACTOR_PROGRESS_2026-01-15.md](REFACTOR_PROGRESS_2026-01-15.md) and [PHASE3_COMPLETE_2026-01-15.md](PHASE3_COMPLETE_2026-01-15.md) for complete details and [CLAUDE.md](CLAUDE.md) for the updated architecture guide.

### Using Output Optimization (Phase 3)

Enable file size optimization in your game's `run.py`:

```python
from src.output.output_formatter import OutputMode

config = GameConfig()

# Enable output compression (Phase 3.1)
config.output_mode = OutputMode.COMPACT  # 27.9% reduction
config.compress_symbols = True
config.compress_positions = True

# Enable event filtering (Phase 3.2) - additional 10-15% reduction
config.skip_derived_wins = True  # Skip SET_WIN, SET_TOTAL_WIN
config.skip_progress_updates = True  # Skip UPDATE_* events
config.verbose_event_level = "standard"  # "minimal", "standard", or "full"
```

**Impact:**
- Compact mode alone: **27.9% smaller files**, 13% faster generation
- With filtering: **35-40% total reduction** from baseline
- Example: 10K simulations reduced from 18.89 MB to 11-12 MB

All optimizations are backward compatible and production-ready!

## Documentation

- **[docs/](docs/)** - User guides and tutorials
  - [Running Games](docs/running-games.md) - How to run simulations and build books
  - [Game Structure](docs/game-structure.md) - Architecture and file organization
  - [Optimization](docs/optimization.md) - Using the optimization algorithm
  - [Events](docs/events.md) - Event system guide
  - [Testing](docs/testing.md) - Writing and running tests
- **[CLAUDE.md](CLAUDE.md)** - Comprehensive technical reference

## Improvements & Added Features

This repository includes several enhancements and new features compared to the original SDK:

### 🗜️ **Output Optimization (Phase 3 - NEW!)**
- **Intelligent compression** - 27.9% file size reduction through OutputFormatter with COMPACT mode
- **Event filtering** - Additional 10-15% reduction via selective event emission with EventFilter
- **Performance boost** - 13% faster generation with compact mode
- **Smart formatting** - Symbol compression (`"L5"` vs `{"name": "L5"}`), position arrays (`[0,2]` vs `{"reel": 0, "row": 2}`)
- **Configurable verbosity** - Three event levels (minimal/standard/full) for different use cases
- **Format versioning** - Built-in version tracking for forward compatibility
- **Production tested** - 54 comprehensive tests, RGS verified, fully backward compatible

### 📝 **JSON Output Formatting**
- **Automatic JSON formatting** when compression is disabled - books files are automatically formatted with proper indentation for better readability
- **Smart formatting logic** that keeps simple name objects (like `{"name": "L1"}`) compact while pretty-printing complex structures
- **Integrated formatting pipeline** - formatting runs automatically after simulation via the Makefile
- **Advanced error handling** with JSONL reconstruction capabilities for corrupted files

### 🏷️ **Standardized Event Names**
- **Event constants system** - All event types are now defined in `EventConstants` enum for consistency
- **Centralized event management** - No more hardcoded event strings scattered throughout the codebase
- **Type safety** - Using constants prevents typos and ensures consistent event naming across the SDK
- **Comprehensive event coverage** - Standardized events for wins, free spins, tumbles, reveals, and special symbols

### 🧪 **Unit Testing Framework**
- **Game-specific unit tests** - Each game can have its own dedicated test suite
- **Isolated testing** - Test individual components without requiring full game simulation
- **Fast execution** - Quick feedback during development with focused test cases
- **Test automation** - Integrated with Makefile for easy test running (`make unittest GAME=<game_name>`)
- **Example implementations** - Tower defense game includes comprehensive sticky symbols tests

### 🔧 **Enhanced Development Workflow**
- **Improved Makefile** - Added commands for unit testing and automated formatting
- **Better error reporting** - More detailed error messages and debugging information
- **Documentation enhancements** - Comprehensive docs for events, testing, and formatting systems
- **Development tools** - Scripts for JSON formatting and game analytics

### 📊 **Advanced Analytics & Debugging**
- **Enhanced game analytics** - Better tools for analyzing simulation results and win distributions
- **Force record improvements** - More detailed tracking of custom-defined events and search keys
- **Simulation validation** - Better verification tools for ensuring data integrity
- **Statistics export** - Improved JSON and Excel export capabilities for PAR sheets

### 🎮 **Game Development Features**
- **Sticky symbols support** - Built-in framework for implementing sticky symbol mechanics
- **Event-driven architecture** - Enhanced event system for better game state management
- **Flexible configuration** - More options for customizing game behavior and output formats
- **Template improvements** - Better game templates and examples for faster development


# Installation

This repository requires Python3 (version >= 3.12), along with the PIP package installer.
If the included optimization algorithm is being used, Rust/Cargo will also need to be installed.

It is recommended to use [Make](https://www.gnu.org/software/make/) and setup the engine by running:
```sh
make setup
```

# Running Games

To run a game simulation and build books:

```sh
# Activate virtual environment
source env/bin/activate

# Run game simulation
make run GAME=<game_name>

# Example: Run the 0_0_cluster game
make run GAME=0_0_cluster
```

## Configuration

The behavior is controlled by settings in each game's `run.py` file:

```python
# Enable/disable simulation runs
run_sims = True

# Number of simulations per betmode
num_sim_args = {"base": 10000}

# Compression settings
compression = False  # False for readable JSON, True for compressed zstd files

# JSON format
output_regular_json = True  # True for single JSON file, False for JSONL format
```

## Testing

```sh
# Run game-specific unit tests
make unit-test GAME=<game_name>

# Run full SDK tests
make test
```
