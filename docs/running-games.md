# Running Games and Building Books

This guide explains how to run game simulations and generate books files.

## Quick Start

```bash
# Activate virtual environment
source env/bin/activate

# Run game simulation
make run GAME=<game_name>

# Example
make run GAME=0_0_cluster
```

## Configuration

Edit the game's `run.py` file to configure simulation behavior:

### Basic Settings

```python
# games/<game_name>/run.py

# Enable/disable simulation
run_sims = True

# Number of simulations per betmode
num_sim_args = {
    "base": 10000,   # 10k base game simulations
    "bonus": 5000    # 5k bonus game simulations (if applicable)
}
```

### Output Format

```python
# Compression
compression = False  # True for .zst compressed files, False for readable JSON

# JSON format
output_regular_json = True  # True for JSON array, False for JSONL (newline-delimited)
```

**When `compression=False`**, the Makefile automatically formats JSON output:
- Simple objects like `{"name": "L1"}` stay compact
- Complex structures are pretty-printed
- Uses `scripts/format_books_json.py`

### Additional Options

```python
# RGS format verification
run_format_checks = True  # Validate output against RGS requirements

# Generate analytics (PAR sheets, statistics)
run_game_analytics = False

# Upload to AWS S3
upload_to_aws = False
```

## Output Files (Books)

Books are saved in the game directory:

```
games/<game_name>/
  ├── <game_name>_base_books.json      # Base game results
  ├── <game_name>_base_probs.csv       # Probability weights
  └── ...
```

### Books Format

**JSON Format** (`output_regular_json=True`):
```json
[
  {
    "board": [["A", "K", "Q"], ["A", "K", "J"], ["K", "Q", "J"]],
    "events": [
      {"type": "win", "amount": 5.0, "symbols": ["A"]},
      {"type": "trigger_free_spins", "count": 10}
    ],
    "final_win": 5.0
  }
]
```

**JSONL Format** (`output_regular_json=False`):
```jsonl
{"board": [["A", "K", "Q"], ...], "events": [...], "final_win": 5.0}
{"board": [["J", "Q", "K"], ...], "events": [...], "final_win": 2.5}
```

**Compressed** (`compression=True`):
- Files have `.zst` extension (zstandard compression)
- Much smaller file sizes
- Must decompress to read

## Complete Workflow

### 1. Initial Setup

```bash
# First time only
make setup
source env/bin/activate
```

### 2. Configure Game

Edit `games/<game_name>/run.py`:

```python
run_sims = True
num_sim_args = {"base": 10000}  # Start small for testing
compression = False              # Readable output for debugging
output_regular_json = True
```

### 3. Run Simulation

```bash
make run GAME=0_0_cluster
```

Output:
```
Running simulation for 0_0_cluster...
Base game: 10000 simulations
Generating books...
Formatting JSON output...
✓ Books generated successfully
```

### 4. Verify Results

```bash
# Check generated files
ls -lh games/0_0_cluster/*_books.*

# View first entries
head -n 50 games/0_0_cluster/0_0_cluster_base_books.json
```

### 5. Run Tests

```bash
# Game-specific tests
make unit-test GAME=0_0_cluster

# Full SDK tests
make test
```

## How Books Are Used

### In Production (RGS)

1. **Upload**: Books + CSV probabilities uploaded to Carrot RGS
2. **Selection**: Player bets → RGS selects simulation by weighted probability
3. **Response**: Game outcome returned via `/play` API
4. **Render**: Frontend displays board, plays events, shows wins

### File Structure for RGS

```
game_files/
  ├── <game_name>_base_books.json.zst
  ├── <game_name>_base_probs.csv
  ├── <game_name>_bonus_books.json.zst  (if applicable)
  └── <game_name>_bonus_probs.csv
```

## Running with Optimization

For games using the Rust optimization algorithm:

### 1. Configure Optimization

Edit `games/<game_name>/game_optimization.py`:

```python
"base": {
    "conditions": {
        "basegame": ConstructConditions(hr=3.5, rtp=0.59).return_dict(),
        "freegame": ConstructConditions(rtp=0.37, hr=200).return_dict(),
    },
    "scaling": ConstructScaling([...]).return_dict(),
}
```

### 2. Build Optimizer (First Time)

```bash
cd optimization_program
cargo build --release
cd ..
```

### 3. Run with Optimization

Enable in `games/<game_name>/run.py`:

```python
from src.write_data.optimization_execution import OptimizationExecution

OptimizationExecution(
    game_id="0_0_cluster",
    gamestate=gamestate,
    betmodes=["base"],
    run_sims=False,           # Use existing books
    run_optimization=True,
    optimization_setup=optimization_setup
)
```

Then:
```bash
make run GAME=0_0_cluster
```

## Troubleshooting

### "No module named 'src'"
```bash
pip install -e .
```

### "Virtual environment not found"
```bash
make setup
source env/bin/activate
```

### Books Not Generated
- Check `run_sims = True` in run.py
- Verify `num_sim_args` has positive values
- Review console output for errors

### JSON Formatting Issues
```bash
# Manually format
python scripts/format_books_json.py games/<game_name>/<books_file>.json
```

## Performance Tips

### Development
- Use small `num_sim_args` (1,000-10,000) for rapid iteration
- Disable compression for debugging
- Skip format checks to save time

### Production
- Use large `num_sim_args` (100,000+) for accurate distributions
- Enable compression to save disk space
- Use JSONL format for streaming processing

### Quick Test Config

```python
# Fast iteration during development
num_sim_args = {"base": 1000}
compression = False
output_regular_json = True
run_format_checks = False
```

## See Also

- [Game Structure](game-structure.md) - Architecture overview
- [Optimization Guide](optimization.md) - Detailed optimization usage
- [Event System](events.md) - Working with events
