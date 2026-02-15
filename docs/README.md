# Stake Engine Math SDK Documentation

Welcome to the Stake Engine Math SDK documentation. This comprehensive guide covers everything from getting started to advanced optimization techniques.

---

## Quick Navigation

### 🚀 Getting Started
- [Running Games](running-games.md) - How to run simulations and generate books
- [Game Structure](game-structure.md) - Understanding the architecture
- [Testing](testing.md) - Writing and running tests

### 📚 Core Concepts
- [Event System](events.md) - Working with the standardized event system
- [Optimization Guide](optimization.md) - Using the Rust optimization algorithm

### 🔧 Advanced Topics
- [Migration History](migration-history.md) - Evolution from fork to refactored architecture
- [Performance Analysis](performance-analysis.md) - Profiling and optimization results
- [Event Audit](event-audit.md) - Complete event type inventory
- [Compression Benchmarks](compression-benchmarks.md) - Output optimization metrics
- [Performance Optimization Results](performance-optimization-results.md) - Detailed speedup analysis

### 📖 Reference
- [CLAUDE.md](../CLAUDE.md) - Comprehensive technical reference (root)
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development guidelines (root)
- [CHANGELOG.md](../CHANGELOG.md) - Version history (root)
- [README.md](../README.md) - Quick start guide (root)

---

## Overview

The Stake Engine Math SDK is a Python-based framework for:
- **Defining** slot game rules and mechanics
- **Simulating** game outcomes at scale (10K-1M simulations)
- **Optimizing** win distributions to target RTPs
- **Generating** books files for RGS deployment

---

## Recent Major Improvements (January 2026)

The SDK underwent a comprehensive refactoring and optimization program:

### ✅ Architecture Refactoring (Phases 1-2)
- **67% reduction** in inheritance complexity (6 → 2 layers)
- **75% reduction** in files per game (4 → 1 file per game)
- **180+ type hints** added with comprehensive docstrings
- Custom exception hierarchy for better error handling
- Standardized constants and enums

### ✅ Output Optimization (Phase 3)
- **27.9% file size reduction** via OutputFormatter (compact mode)
- **10-15% additional reduction** via EventFilter
- **Total: 35-40% smaller files** (e.g., 18.89 MB → 11-12 MB per 10K sims)
- **13% faster generation** with compact mode
- Fully backward compatible, RGS verified

### ✅ Performance Optimization (Phase 5)
- **35-47% simulation speedup** via paytable caching
- **287 sims/sec average** (up from 204 sims/sec)
- Built-in profiling tools
- Zero accuracy regression

**Total Impact:**
- Simpler architecture → Easier maintenance
- Smaller output → Faster deployments
- Faster simulations → Quicker iterations
- Better DX → Faster onboarding

See [Migration History](migration-history.md) for complete details.

---

## Getting Started

### Prerequisites

- **Python 3.12+** (required for modern type hints)
- **pip** package installer
- **Rust/Cargo** (for optimization algorithm)
- **Make** (recommended for streamlined commands)

### Installation

```bash
# Clone repository
git clone <repo-url>
cd stake-engine-math

# Setup virtual environment and install dependencies
make setup

# Activate virtual environment
source env/bin/activate
```

### Your First Simulation

```bash
# Run a sample game
make run GAME=template_cluster

# Books files will be generated in:
# games/template_cluster/library/
```

---

## Key Concepts

### Books
Simulation results stored as JSON/JSONL files containing all possible game outcomes:
- **board**: The reel strip result (symbol grid)
- **events**: Game events (wins, triggers, multipliers, etc.)
- **payout_multiplier**: Total win amount

Books can be generated in two modes:
- **VERBOSE**: Human-readable with full details (debugging)
- **COMPACT**: Minimal size for production (27.9% smaller)

### BetModes
Games have different modes (base game, bonus game) each with their own:
- Reel strips and symbol distributions
- Win calculation logic
- Probability weights

Example:
```python
self.bet_modes = {
    "base": BetMode(...),
    "bonus": BetMode(...)
}
```

### Event-Driven Architecture
All game actions are tracked as events using `EventConstants` for consistency:
- WIN, REVEAL, TRIGGER_FREE_SPINS, etc.
- Standardized event types prevent typos
- Event filtering available for size optimization

### Optimization
The Rust-based genetic algorithm adjusts win distributions to meet targets:
- **RTP** (Return to Player)
- **Hit Rate** (win frequency)
- **Average Win** constraints
- **Custom conditions** (symbol appearances, event patterns)

---

## Project Structure

```
stake-engine-math/
├── docs/                              # 📚 Documentation (you are here)
│   ├── README.md                      # This file
│   ├── migration-history.md           # Complete refactoring history
│   ├── running-games.md               # How to run simulations
│   ├── game-structure.md              # Architecture guide
│   ├── optimization.md                # Optimization guide
│   ├── events.md                      # Event system guide
│   ├── testing.md                     # Testing guide
│   ├── performance-analysis.md        # Performance profiling
│   ├── event-audit.md                 # Event inventory
│   ├── compression-benchmarks.md      # Output benchmarks
│   └── performance-optimization-results.md
│
├── games/<game_name>/                 # 🎮 Individual games
│   ├── run.py                         # Main entry point
│   ├── game_config.py                 # Game configuration
│   ├── game_state.py                   # All game logic (Phase 1.3)
│   ├── game_optimization.py           # Optimization parameters
│   ├── reels/                         # Reel strip CSV files
│   ├── library/                       # Generated books files
│   └── tests/                         # Game-specific tests
│
├── src/                               # 🔧 Core SDK modules
│   ├── calculations/                  # Win calculation algorithms
│   │   ├── board.py                   # Board generation
│   │   ├── cluster.py                 # Cluster-pay
│   │   ├── lines.py                   # Line-pay
│   │   ├── ways.py                    # Ways-pay
│   │   ├── scatter.py                 # Scatter-pay
│   │   └── tumble.py                  # Cascade mechanics
│   ├── config/                        # Configuration
│   │   ├── config.py                  # Base Config class
│   │   └── bet_mode.py                 # BetMode class
│   ├── events/                        # Event system
│   │   ├── constants.py               # Standardized event type constants
│   │   ├── filter.py                  # Event filtering (Phase 3.2)
│   │   ├── core.py                    # Core events (reveal, win, set_win, win_cap)
│   │   ├── free_spins.py             # Free spins events (trigger, update, end)
│   │   ├── tumble.py                  # Tumble events (tumble, board multipliers)
│   │   ├── special_symbols.py        # Special symbol events (upgrade, prize)
│   │   └── helpers.py                 # Utilities (to_camel_case, convert_symbol_json)
│   ├── formatter.py                   # Output optimization - COMPACT/VERBOSE modes (Phase 3.1)
│   ├── state/                         # Core state machine
│   │   ├── game_state.py              # GameState base class (Phase 1.3)
│   │   ├── books.py                   # Book generation
│   │   └── run_sims.py                # Simulation runner
│   ├── wins/                          # Win management
│   │   └── win_manager.py
│   ├── constants.py                   # Enums (GameMode, WinType)
│   ├── exceptions.py                  # Custom exceptions
│   └── types.py                       # Type aliases
│
├── optimization_program/              # 🦀 Rust optimization engine
│   └── src/
│       └── main.rs
│
├── tests/                             # ✅ SDK-wide tests (54 tests)
│   ├── test_output_formatter.py       # Output compression tests
│   ├── test_event_filter.py           # Event filtering tests
│   ├── test_book_event_filtering.py   # Integration tests
│   └── win_calculations/              # Win algorithm tests
│
├── scripts/                           # 🛠️ Helper scripts
│   ├── format_books_json.py           # JSON formatting
│   ├── profile_performance.py         # Performance profiling
│   ├── validate_config.py             # Config validation
│   └── benchmark_compression.py       # Compression benchmarks
│
├── utils/                             # 🔍 Utility tools
│   ├── game_analytics/                # PAR sheet generation
│   └── rgs_verification.py            # RGS compatibility checks
│
├── README.md                          # 📖 Quick start guide
├── CLAUDE.md                          # 🤖 Complete technical reference
├── CONTRIBUTING.md                    # 👥 Development guidelines
└── CHANGELOG.md                       # 📝 Version history
```

---

## Common Tasks

### Running Simulations

```bash
# Run a game with default settings
make run GAME=tower_treasures

# Run with custom simulation count
# Edit run_config.toml: [simulation] base = 10000
```

### Enable Output Optimization

In your game's `game_config.py`:

```python
from src.formatter import OutputMode

class GameConfig(Config):
    def __init__(self):
        super().__init__()

        # Enable compact output (27.9% smaller)
        self.output_mode = OutputMode.COMPACT
        self.simple_symbols = True
        self.compress_positions = True

        # Enable event filtering (additional 10-15% reduction)
        self.skip_derived_wins = True
        self.skip_progress_updates = True
        self.verbose_event_level = "standard"
```

### Running Tests

```bash
# Game-specific tests
make unit-test GAME=tower_treasures

# Full SDK tests
make test

# Test coverage report
make coverage
```

### Configuration Validation

```bash
# List all games
make list-games

# Validate game configuration
make validate GAME=tower_treasures
```

### Performance Profiling

```bash
# Profile simulation performance
make profile GAME=tower_treasures

# Run compression benchmarks
make benchmark GAME=template_lines
```

### Building Optimization

```bash
cd optimization_program
cargo build --release
cargo run --release
```

---

## Development Workflow

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Creating a New Game

```bash
# Copy template
cp -r games/template games/my_new_game

# Edit configuration
# games/my_new_game/game_config.py

# Implement game logic
# games/my_new_game/game_state.py

# Add reel strips
# games/my_new_game/reels/

# Run simulation
make run GAME=my_new_game
```

### Code Quality Checks

```bash
# Format code
black .
isort .

# Type checking
mypy src/ games/

# Linting
flake8 src/ games/

# All checks run automatically on commit via pre-commit hooks
```

---

## Documentation Guides

### For New Users
1. Start with [Quick Start Guide](../README.md)
2. Read [Running Games](running-games.md)
3. Understand [Game Structure](game-structure.md)
4. Try creating a game from [template](../games/template/)

### For Game Developers
1. Review [Game Structure](game-structure.md)
2. Study [Event System](events.md)
3. Check [Testing Guide](testing.md)
4. Reference [CLAUDE.md](../CLAUDE.md) for deep technical details

### For Contributors
1. Read [CONTRIBUTING.md](../CONTRIBUTING.md)
2. Review [Migration History](migration-history.md) to understand recent changes
3. Check [CHANGELOG.md](../CHANGELOG.md) for version history
4. Run tests before submitting changes

### For Optimization Engineers
1. Study [Optimization Guide](optimization.md)
2. Review [Performance Analysis](performance-analysis.md)
3. Check [Compression Benchmarks](compression-benchmarks.md)
4. See [Performance Optimization Results](performance-optimization-results.md)

---

## Key Files Reference

### Root Documentation (Important - Keep in Root)
- [README.md](../README.md) - First file users see, quick start guide
- [CLAUDE.md](../CLAUDE.md) - Comprehensive technical reference for Claude Code
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development standards and conventions
- [CHANGELOG.md](../CHANGELOG.md) - Detailed version history

### Technical Documentation (In docs/)
- [migration-history.md](migration-history.md) - Complete refactoring story
- [performance-analysis.md](performance-analysis.md) - CPU/memory profiling
- [event-audit.md](event-audit.md) - Complete event inventory
- [compression-benchmarks.md](compression-benchmarks.md) - File size metrics

### User Guides (In docs/)
- [running-games.md](running-games.md) - How to run simulations
- [game-structure.md](game-structure.md) - Architecture overview
- [optimization.md](optimization.md) - Optimization workflow
- [events.md](events.md) - Event system usage
- [testing.md](testing.md) - Test writing and execution

---

## Help and Support

### Getting Help

If you encounter issues:

1. Check the relevant guide in [docs/](.)
2. Review [CLAUDE.md](../CLAUDE.md) for technical details
3. Check [CONTRIBUTING.md](../CONTRIBUTING.md) for conventions
4. Open an issue with:
   - Game name
   - Error message
   - Steps to reproduce
   - Expected vs actual behavior

### Common Issues

**Import Errors:**
```bash
# Make sure virtual environment is activated
source env/bin/activate
```

**Type Errors:**
```bash
# Check mypy configuration in pyproject.toml
# Some dynamic attributes use type: ignore
```

**Test Failures:**
```bash
# Run tests in verbose mode
pytest -v tests/

# Check test-specific documentation
# See testing.md for details
```

---

## Version Information

**Current Version**: 2.0.0 (January 2026)

**Major Changes**:
- Phase 1: Architecture simplification (6 → 2 layers)
- Phase 2: Code quality improvements (types, docs, standards)
- Phase 3: Output optimization (35-40% size reduction)
- Phase 5: Performance optimization (35-47% speedup)

See [CHANGELOG.md](../CHANGELOG.md) for complete version history.

---

## Next Steps

Ready to dive deeper? Pick your path:

**🎮 Game Developer Path:**
1. [Running Games](running-games.md)
2. [Game Structure](game-structure.md)
3. Create a game from template
4. [Testing](testing.md)

**🔧 SDK Developer Path:**
1. [CONTRIBUTING.md](../CONTRIBUTING.md)
2. [Migration History](migration-history.md)
3. [CLAUDE.md](../CLAUDE.md)
4. Run tests and explore codebase

**⚡ Optimization Engineer Path:**
1. [Optimization Guide](optimization.md)
2. [Performance Analysis](performance-analysis.md)
3. [Compression Benchmarks](compression-benchmarks.md)
4. Run profiling tools

---

**Happy coding! 🎰**
