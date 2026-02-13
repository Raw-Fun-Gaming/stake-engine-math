# Stake Engine Math SDK

<p align="center">
  <a href="https://github.com/Raw-Fun-Gaming/stake-engine-math/releases/latest"><img src="https://img.shields.io/github/v/release/Raw-Fun-Gaming/stake-engine-math?style=flat-square&color=blue" alt="Release"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12+-blue?style=flat-square&logo=python&logoColor=white" alt="Python Version"></a>
  <a href="https://github.com/Raw-Fun-Gaming/stake-engine-math/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Raw-Fun-Gaming/stake-engine-math?style=flat-square" alt="License"></a>
  <a href="https://github.com/Raw-Fun-Gaming/stake-engine-math/tree/main/tests"><img src="https://img.shields.io/badge/tests-54%20passing-success?style=flat-square&logo=pytest" alt="Tests"></a>
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-black?style=flat-square" alt="Code Style"></a>
  <a href="https://mypy-lang.org/"><img src="https://img.shields.io/badge/type%20checked-mypy-blue?style=flat-square" alt="Type Checked"></a>
</p>

The Math SDK is a Python-based engine for defining game rules, simulating outcomes, and optimizing win distributions. It generates all necessary backend and configuration files, lookup tables, and simulation results.

---

## 🎉 Major Architecture Refactoring & Optimization

The codebase has undergone a comprehensive refactoring and optimization (Phases 1-3) that dramatically simplifies the architecture, improves maintainability, and significantly reduces output file sizes.

### Key Improvements

**Phase 1-2: Architecture Refactoring**

- 🏗️ **Flattened Inheritance**: Reduced from 6 layers to 2 layers (67% reduction in complexity)
- 📁 **Simplified Structure**: Games now use 1 file instead of 4 (75% reduction)
- 📝 **Comprehensive Type Hints**: 180+ functions with full type annotations
- 📚 **Rich Documentation**: 120+ docstrings with examples and usage guidance
- 🛡️ **Better Error Handling**: Custom exception hierarchy with clear error messages
- 🔤 **Modern Code Quality**: Enums, constants, and standardized patterns
- ✅ **Fully Tested**: All 7 games migrated and verified working

**Phase 3: Output Optimization**

- 🗜️ **Smart Compression**: 27.9% file size reduction via intelligent output formatting
- ⚡ **Faster Generation**: 13% speed improvement with compact mode
- 🎯 **Event Filtering**: Additional 10-15% reduction through selective event emission
- 📊 **Combined Savings**: 35-40% total file size reduction (e.g., 18.89 MB → 11-12 MB per 10K sims)
- 🔄 **Backward Compatible**: All optimizations are opt-in, defaults to verbose mode
- ✅ **Production Ready**: Fully tested (54 tests passing), RGS verified

**Phase 5: Performance Optimization**

- ⚡ **35-47% simulation speedup** via paytable caching
- 📈 **287 sims/sec average** (up from 204 sims/sec)
- 🔧 **Built-in profiling tools**
- ✅ **Zero accuracy regression**

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/Raw-Fun-Gaming/stake-engine-math.git
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

# Output will be generated in:
# games/template_cluster/build/books/
```

---

## 📚 Documentation

Explore the comprehensive documentation to learn about the SDK:

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Getting Started__

    ---

    Learn how to install, configure, and run your first simulation

    [:octicons-arrow-right-24: Running Games](running-games.md)

-   :material-architecture:{ .lg .middle } __Architecture__

    ---

    Understand the refactored architecture and game structure

    [:octicons-arrow-right-24: Game Structure](game-structure.md)

-   :material-lightning-bolt:{ .lg .middle } __Optimization__

    ---

    Use the Rust optimization algorithm to tune win distributions

    [:octicons-arrow-right-24: Optimization Guide](optimization.md)

-   :material-chart-line:{ .lg .middle } __Performance__

    ---

    Learn about performance improvements and profiling tools

    [:octicons-arrow-right-24: Performance Analysis](performance-analysis.md)

</div>

---

## ✨ Key Features

### TOML-Based Configuration

Clean separation between game rules and runtime settings:

```toml
[execution]
num_threads = 10        # Python simulation threads
compression = false     # Enable zstd compression
profiling = false       # Enable performance profiling

[simulation]
base = 10000           # Base game simulations
bonus = 10000          # Bonus game simulations

[pipeline]
run_sims = true            # Generate simulation books
run_optimization = true    # Run Rust optimization
run_analysis = true        # Generate PAR sheets

target_modes = ["base", "bonus"]
```

### Output Optimization

Enable file size optimization in your game's `game_config.py`:

```python
from src.output.output_formatter import OutputMode

config = GameConfig()

# Enable output compression (Phase 3.1)
config.output_mode = OutputMode.COMPACT  # 27.9% reduction
config.simple_symbols = True
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

### Simplified Game Structure

**Before:** Games required 4+ files with 6-layer inheritance

**After:** Single `gamestate.py` file with 2-layer inheritance

```python
from src.calculations.board import Board

class GameState(Board):
    """Game-specific logic for my_game"""

    def run_spin(self):
        """Main spin logic for base game"""
        self.draw_board()
        self.evaluate_wins()
        return self.book
```

---

## 🛠️ Development

### Testing

```bash
# Run game-specific unit tests
make unit-test GAME=<game_name>

# Run full SDK tests
make test

# Test coverage report
make coverage
```

### Configuration Validation

```bash
# List all games
make list-games

# Validate game configuration
make validate GAME=<game_name>
```

### Performance Profiling

```bash
# Profile simulation performance
make profile GAME=<game_name>

# Run compression benchmarks
make benchmark GAME=<game_name>
```

---

## 📦 Installation via PyPI

Coming soon! The package will be available for installation via pip:

```bash
pip install stake-engine-math
```

See the [Publishing Guide](PUBLISHING.md) for details on the PyPI publishing process.

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](https://github.com/Raw-Fun-Gaming/stake-engine-math/blob/main/CONTRIBUTING.md) for details on:

- Code style and standards
- Development workflow
- Testing requirements
- Pull request process

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Raw-Fun-Gaming/stake-engine-math/blob/main/LICENSE) file for details.

---

## 🔗 Links

- **GitHub Repository**: [Raw-Fun-Gaming/stake-engine-math](https://github.com/Raw-Fun-Gaming/stake-engine-math)
- **Latest Release**: [v2.0.0](https://github.com/Raw-Fun-Gaming/stake-engine-math/releases/tag/v2.0.0)
- **Wiki**: [Documentation Wiki](https://github.com/Raw-Fun-Gaming/stake-engine-math/wiki)
- **Issues**: [Report a Bug](https://github.com/Raw-Fun-Gaming/stake-engine-math/issues)

---

<div align="center">

**Ready to get started?** Jump to [Running Games](running-games.md) to run your first simulation! 🎰

</div>
