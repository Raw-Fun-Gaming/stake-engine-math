# Optimization Guide

The Math SDK includes a Rust-based genetic algorithm for optimizing win distributions to meet target RTP (Return to Player), hit rates, and other constraints.

## Overview

The optimization algorithm:
- Adjusts win probabilities and multiplier distributions
- Uses genetic algorithms to search for optimal configurations
- Can target specific RTP, hit rate, and average win constraints
- Scales specific win ranges to fine-tune distributions

## Setup

### 1. Install Rust/Cargo

```bash
# Install Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Verify installation
cargo --version
```

### 2. Build Optimization Program

```bash
cd optimization_program
cargo build --release
cd ..
```

## Configuration

Optimization is configured in each game's `game_optimization.py` file:

### Basic Structure

```python
from src.write_data.optimization_setup import OptimizationSetup, ConstructConditions, ConstructScaling, ConstructParameters

optimization_setup = OptimizationSetup(
    setup_dict={
        "base": {  # Bet mode name
            "conditions": {...},
            "scaling": {...},
            "parameters": {...}
        }
    }
)
```

### Conditions

Define target metrics for different game phases:

```python
"conditions": {
    # Base game conditions
    "base_game": ConstructConditions(
        hr=3.5,      # Target hit rate (% of spins with wins)
        rtp=0.59     # Target RTP contribution from base game
    ).return_dict(),

    # Free game conditions
    "free_game": ConstructConditions(
        rtp=0.37,    # Target RTP contribution from free games
        hr=200,      # Target hit rate (per 10k spins)
        search_conditions={"symbol": "scatter"}  # Trigger condition
    ).return_dict(),
}
```

#### ConstructConditions Parameters

- **`hr`** (float): Target hit rate
  - For base game: percentage (e.g., 3.5 = 3.5%)
  - For features: occurrences per 10k spins (e.g., 200 = 200 times)
- **`rtp`** (float): Target RTP contribution (e.g., 0.59 = 59%)
- **`average_win`** (float, optional): Target average win when feature hits
- **`search_conditions`** (dict, optional): Conditions to identify the feature
  - `{"symbol": "scatter"}` - Look for scatter symbol
  - `{"event_type": "triggerFreeSpins"}` - Look for specific event

### Scaling

Adjust specific win ranges:

```python
"scaling": ConstructScaling([
    # Scale wins between 10x-20x by factor of 1.5
    {"min": 10, "max": 20, "scale": 1.5},

    # Scale wins above 100x by factor of 0.8
    {"min": 100, "max": float('inf'), "scale": 0.8},
]).return_dict()
```

This is useful for:
- Increasing frequency of mid-range wins
- Reducing extreme wins
- Balancing volatility

### Parameters

Optimization algorithm settings:

```python
"parameters": ConstructParameters(
    num_show=5000,              # Number of top outcomes to display
    num_per_fence=10000,        # Population size per optimization group
    test_spins=[50, 100, 200],  # Test with these spin counts
    score_type="rtp"            # Optimization scoring method
).return_dict()
```

#### ConstructParameters Options

- **`num_show`**: How many outcomes to show in results
- **`num_per_fence`**: Population size (larger = more thorough but slower)
- **`test_spins`**: Spin counts to test optimized distributions
- **`score_type`**: What to optimize for
  - `"rtp"` - Target RTP accuracy
  - `"hr"` - Target hit rate accuracy
  - `"balanced"` - Balance both

## Complete Example

```python
# games/my_game/game_optimization.py

from src.write_data.optimization_setup import (
    OptimizationSetup,
    ConstructConditions,
    ConstructScaling,
    ConstructParameters
)

optimization_setup = OptimizationSetup(
    setup_dict={
        "base": {
            "conditions": {
                # Base game: 3.5% hit rate, contributes 59% RTP
                "base_game": ConstructConditions(
                    hr=3.5,
                    rtp=0.59
                ).return_dict(),

                # Free spins: triggers 200 times per 10k spins, contributes 37% RTP
                "free_game": ConstructConditions(
                    rtp=0.37,
                    hr=200,
                    search_conditions={"symbol": "scatter"}
                ).return_dict(),

                # Big wins: average 50x when hitting 100x+
                "bigwin": ConstructConditions(
                    average_win=50,
                    search_conditions={"min_win": 100}
                ).return_dict(),
            },

            "scaling": ConstructScaling([
                # Increase mid-range wins (10x-50x)
                {"min": 10, "max": 50, "scale": 1.3},

                # Reduce very high wins (500x+)
                {"min": 500, "max": float('inf'), "scale": 0.7},
            ]).return_dict(),

            "parameters": ConstructParameters(
                num_show=5000,
                num_per_fence=20000,  # Larger for better accuracy
                test_spins=[100, 500, 1000],
                score_type="balanced"
            ).return_dict()
        }
    }
)
```

## Running Optimization

### Method 1: Via run.py

Edit `games/<game_name>/run.py`:

```python
from src.write_data.optimization_execution import OptimizationExecution

# Load game and config
game_state = GameState()
from games.my_game.game_optimization import optimization_setup

# Run optimization
OptimizationExecution(
    game_id="my_game",
    game_state=game_state,
    bet_modes=["base"],           # Bet modes to optimize
    run_sims=False,              # Use existing books (set True to regenerate)
    run_optimization=True,       # Enable optimization
    optimization_setup=optimization_setup
)
```

Then run:
```bash
make run GAME=my_game
```

### Method 2: Separate Optimization Run

1. Generate books first:
```toml
# run_config.toml - first pass
[pipeline]
run_sims = true
run_optimization = false
```

```bash
make run GAME=my_game
```

2. Then optimize:
```toml
# run_config.toml - second pass
[pipeline]
run_sims = false
run_optimization = true
```

```bash
make run GAME=my_game
```

## Optimization Flow

1. **Load Books**: Reads existing simulation results
2. **Parse Setup**: Loads `game_optimization.py` config
3. **Write Setup File**: Generates `optimization_program/src/setup.txt`
4. **Run Rust Optimizer**: Executes genetic algorithm
5. **Generate Results**:
   - Optimized probability distributions
   - Updated CSV files
   - Statistics and analysis
6. **Validate**: Tests optimized distributions against targets

## Output Files

After optimization:

```
games/<game_name>/
  ├── optimized_base_probs.csv        # Optimized probabilities
  ├── optimization_report.json        # Detailed statistics
  └── optimization_results/           # Intermediate results
      ├── generation_*.csv
      └── best_candidates.json
```

## Interpreting Results

### Optimization Report

```json
{
  "target_rtp": 0.97,
  "achieved_rtp": 0.9698,
  "target_base_hr": 3.5,
  "achieved_base_hr": 3.48,
  "target_free_game_hr": 200,
  "achieved_free_game_hr": 198,
  "generations": 150,
  "best_score": 0.0023
}
```

**Score**: Lower is better (deviation from targets)
- < 0.01: Excellent match
- 0.01-0.05: Good match
- \> 0.05: May need adjustment

### Common Issues

**RTP too high/low**
- Adjust scaling factors
- Modify paytable multipliers
- Check base game win frequencies

**Hit rate off target**
- Adjust trigger symbol distribution
- Modify win condition thresholds
- Check scatter placement in reels

**Optimization not converging**
- Increase `num_per_fence` for larger population
- Adjust `test_spins` for more accurate testing
- Simplify conditions (fewer constraints)

## Advanced Techniques

### Multi-Stage Optimization

Optimize different aspects separately:

```python
# Stage 1: Base game RTP
"base_game": ConstructConditions(rtp=0.60).return_dict()

# Stage 2: Free game frequency
"free_game": ConstructConditions(hr=200).return_dict()

# Stage 3: Fine-tune both
"base_game": ConstructConditions(hr=3.5, rtp=0.59).return_dict()
```

### Conditional Scaling

Different scaling for different game states:

```python
# In base game: scale medium wins up
"base_scaling": ConstructScaling([
    {"min": 5, "max": 20, "scale": 1.5}
]).return_dict()

# In free spins: scale high wins down
"free_spin_scaling": ConstructScaling([
    {"min": 50, "max": float('inf'), "scale": 0.8}
]).return_dict()
```

### Search Conditions

Find specific outcomes:

```python
# Find free spin triggers
search_conditions={"symbol": "scatter", "min_count": 3}

# Find high wins
search_conditions={"min_win": 100}

# Find specific events
search_conditions={"event_type": "triggerFreeSpins"}

# Combine conditions
search_conditions={
    "symbol": "M",
    "min_win": 50,
    "event_type": "updateGlobalMult"
}
```

## Performance Tips

### Quick Iteration
```python
num_per_fence=5000          # Smaller population
test_spins=[50]             # Fewer test spins
```

### Production Run
```python
num_per_fence=50000         # Large population
test_spins=[100, 500, 1000] # Thorough testing
```

### Memory Usage
- Large `num_per_fence` increases memory usage
- Use smaller books for initial optimization
- Generate full books after optimization converges

## Troubleshooting

### "Optimization failed to converge"
- Conflicting conditions (impossible to satisfy all targets)
- Try relaxing some constraints
- Check if paytable supports target RTP

### "Setup file not found"
- Ensure `game_optimization.py` exists
- Check file is imported correctly in `run.py`
- Verify `OptimizationSetup` is constructed properly

### "Rust build failed"
- Install Rust: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- Update Rust: `rustup update`
- Check `optimization_program/Cargo.toml` is valid

## See Also

- [Game Structure](game-structure.md) - Understanding game architecture
- [Running Games](running-games.md) - Generating books for optimization
- [CLAUDE.md](../CLAUDE.md) - Detailed optimization setup reference
