# Stake Engine Math SDK

The Math SDK is a Python-based engine for defining game rules, simulating outcomes, and optimizing win distributions. It generates all necessary backend and configuration files, lookup tables, and simulation results.

## 🎉 Major Architecture Refactoring (January 2026)

The codebase has undergone a comprehensive refactoring (Phases 1-2) that dramatically simplifies the architecture and improves maintainability:

### Key Improvements

- **🏗️ Flattened Inheritance**: Reduced from 6 layers to 2 layers (67% reduction in complexity)
- **📁 Simplified Structure**: Games now use 1 file instead of 4 (75% reduction)
- **📝 Comprehensive Type Hints**: 180+ functions with full type annotations
- **📚 Rich Documentation**: 120+ docstrings with examples and usage guidance
- **🛡️ Better Error Handling**: Custom exception hierarchy with clear error messages
- **🔤 Modern Code Quality**: Enums, constants, and standardized patterns
- **✅ Fully Tested**: All 7 games migrated and verified working

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

See [REFACTOR_PROGRESS.md](REFACTOR_PROGRESS.md) for complete details and [CLAUDE.md](CLAUDE.md) for the updated architecture guide.

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
