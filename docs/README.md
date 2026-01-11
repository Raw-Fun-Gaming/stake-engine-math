# Stake Engine Math SDK Documentation

This documentation covers the essential aspects of using and developing with the Math SDK.

## Quick Links

- [Running Games and Building Books](running-games.md) - How to run simulations and generate books
- [Game Structure](game-structure.md) - Understanding the architecture and file organization
- [Optimization Guide](optimization.md) - Using the Rust optimization algorithm
- [Event System](events.md) - Working with the standardized event system
- [Testing](testing.md) - Writing and running tests

## Overview

The Stake Engine Math SDK is a Python-based framework for:
- Defining slot game rules and mechanics
- Simulating game outcomes at scale
- Optimizing win distributions to target RTPs
- Generating books files for RGS deployment

## Getting Started

### Prerequisites

- Python 3.12+
- pip package installer
- Rust/Cargo (for optimization algorithm)
- Make (recommended)

### Installation

```bash
# Setup virtual environment and install dependencies
make setup

# Activate virtual environment
source env/bin/activate
```

### Your First Simulation

```bash
# Run a sample game
make run GAME=0_0_cluster

# The books files will be generated in games/0_0_cluster/
```

## Key Concepts

### Books
Books are the simulation results - JSON/JSONL files containing all possible game outcomes. Each entry includes:
- **board**: The reel strip result (symbol grid)
- **events**: Game events (wins, triggers, multipliers)
- **final_win**: Total win amount

### BetModes
Games have different modes (base game, bonus game) each with their own:
- Reel strips and symbol distributions
- Win calculation logic
- Probability weights

### Event-Driven Architecture
All game actions are tracked as events using `EventConstants` for consistency.

### Optimization
The Rust-based genetic algorithm adjusts win distributions to meet target RTP, hit rate, and other constraints.

## Project Structure

```
games/<game_name>/
  ├── run.py                 # Main entry point
  ├── game_config.py         # Game configuration
  ├── gamestate.py           # Game loop (run_spin, run_freespin)
  ├── game_override.py       # Override base behaviors
  ├── game_executables.py    # Win calculation logic
  ├── game_optimization.py   # Optimization parameters
  ├── reels/                 # Reel strip CSV files
  └── tests/                 # Game-specific unit tests

src/                         # Core SDK modules
  ├── calculations/          # Win calculation algorithms
  ├── config/                # Base configuration
  ├── events/                # Event system
  ├── state/                 # State machine
  └── ...

optimization_program/        # Rust optimization engine
```

## Common Tasks

### Running Simulations

```bash
make run GAME=<game_name>
```

### Running Tests

```bash
# Game-specific tests
make unit-test GAME=<game_name>

# Full SDK tests
make test
```

### Building Optimization

```bash
cd optimization_program
cargo build --release
```

## Additional Resources

- [CLAUDE.md](../CLAUDE.md) - Comprehensive technical reference
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
