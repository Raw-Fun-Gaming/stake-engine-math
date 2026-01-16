# Running Games and Building Books

This guide explains how to run game simulations and generate books files.

## Quick Start

```bash
# Activate virtual environment
source env/bin/activate

# Run game simulation
make run GAME=<game_name>

# Example
make run GAME=template_cluster
```

## Configuration

Edit the game's `run_config.toml` file to configure simulation behavior:

### Basic Settings

```toml
# games/<game_name>/run_config.toml

# Pipeline control
[pipeline]
run_sims = true            # Enable/disable simulation

# Simulation counts per bet mode
[simulation]
base = 10000              # 10k base game simulations
bonus = 5000              # 5k bonus game simulations (if applicable)
```

### Output Format

```toml
# Compression settings (in [execution] section)
[execution]
compression = false       # True for .zst compressed files, False for readable JSON
num_threads = 10
profiling = false
```

**Note**: The `output_regular_json` setting is configured in `game_config.py`, not in TOML (True for JSON array, False for JSONL).

**When `compression = false`**, the Makefile automatically formats JSON output:
- Simple objects like `{"name": "L1"}` stay compact
- Complex structures are pretty-printed
- Uses `scripts/format_books_json.py`

### Additional Options

```toml
# Pipeline control
[pipeline]
run_format_checks = true   # Validate output against RGS requirements
run_analysis = false       # Generate analytics (PAR sheets, statistics)
run_optimization = false   # Run Rust optimization algorithm
```

## Output Files (Books)

Books are saved in the game's build directory:

```
games/<game_name>/build/books/
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
      {"type": "triggerFreeSpins", "count": 10}
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

**Compressed** (`compression = true`):
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

Edit `games/<game_name>/run_config.toml`:

```toml
# Pipeline control
[pipeline]
run_sims = true               # Enable simulation

# Simulation counts
[simulation]
base = 10000                  # Start small for testing

# Execution settings
[execution]
compression = false           # Readable output for debugging
num_threads = 10

# Target modes
target_modes = ["base"]
```

**Note**: `output_regular_json` is set in `game_config.py`, not in TOML.

### 3. Run Simulation

```bash
make run GAME=template_cluster
```

Output:
```
Running simulation for template_cluster...
Base game: 10000 simulations
Generating books...
Formatting JSON output...
✓ Books generated successfully
```

### 4. Verify Results

```bash
# Check generated files
ls -lh games/template_cluster/build/books/*_books.*

# View first entries
head -n 50 games/template_cluster/build/books/template_cluster_base_books.json
```

### 5. Run Tests

```bash
# Game-specific tests
make unit-test GAME=template_cluster

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
        "base_game": ConstructConditions(hr=3.5, rtp=0.59).return_dict(),
        "free_game": ConstructConditions(rtp=0.37, hr=200).return_dict(),
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

Enable in `games/<game_name>/run_config.toml`:

```toml
[pipeline]
run_sims = false           # Use existing books
run_optimization = true    # Enable optimization

# Target modes for optimization
target_modes = ["base"]
```

The `run.py` file will automatically load these settings and execute optimization.

Then:
```bash
make run GAME=template_cluster
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
- Check `run_sims = true` in run_config.toml
- Verify `[simulation]` section has positive values
- Review console output for errors

### JSON Formatting Issues
```bash
# Manually format
python scripts/format_books_json.py games/<game_name>/build/books/<books_file>.json
```

## Performance Tips

### Development
- Use small simulation counts (1,000-10,000) in `[simulation]` section for rapid iteration
- Disable compression for debugging (`compression = false`)
- Skip format checks to save time (`run_format_checks = false`)

### Production
- Use large simulation counts (100,000+) in `[simulation]` section for accurate distributions
- Enable compression to save disk space (`compression = true`)
- Use JSONL format for streaming processing (set `output_regular_json = False` in game_config.py)

### Quick Test Config

**Fast iteration during development** (`run_config.toml`):
```toml
[simulation]
base = 1000

[execution]
compression = false

[pipeline]
run_sims = true
run_format_checks = false
run_optimization = false
run_analysis = false

target_modes = ["base"]
```

## See Also

- [Game Structure](game-structure.md) - Architecture overview
- [Optimization Guide](optimization.md) - Detailed optimization usage
- [Event System](events.md) - Working with events
