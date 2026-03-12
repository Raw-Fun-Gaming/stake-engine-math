# Configuration Reference

Complete reference for all configuration parameters in the Math SDK. Parameters are split between two systems:

- **Game Config** (`game_config.py`) — Game rules, symbols, payouts, and output formatting
- **Run Config** (`run_config.toml`) — Execution settings, simulation counts, and pipeline flags

---

## Game Config (`game_config.py`)

Defined in `src/config/config.py`. Each game overrides these in `games/<game_name>/game_config.py`.

### Game Identification

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `game_id` | `str` | `"template_sample"` | Unique game identifier. Used for directory paths and output filenames. |
| `game_name` | `str` | `"sample_lines"` | Display name for the game. |
| `provider_name` | `str` | `"sample_provider"` | Game provider identifier. |
| `provider_number` | `int` | `1` | Numeric provider ID. |
| `rtp` | `float` | `0.97` | Target return to player percentage (0.0–1.0). |

### Board Dimensions

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num_reels` | `int` | `5` | Number of reels on the board. |
| `num_rows` | `int \| list[int]` | `3` | Number of rows per reel. Use a list for variable row counts (e.g., `[7] * 7`). |

### Win Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `win_cap` | `float` | `5000` | Maximum win cap multiplier. Wins are capped at this value. |
| `win_type` | `str` | — | Win calculation method. Set per game: `"cluster"`, `"lines"`, `"ways"`, or `"scatter"`. |
| `min_denomination` | `float` | `0.1` | Minimum bet denomination. |
| `paytable` | `dict[tuple[int, str], float]` | `{}` | Symbol payout table mapping `(count, symbol_name)` to multiplier. Use `convert_range_table()` for range-based definitions. |
| `win_levels` | `dict[str, dict[int, tuple]]` | See below | Win level thresholds for different contexts (`"standard"`, `"endFeature"`). Maps level number to `(min, max)` win range. |

### Symbols

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `special_symbols` | `dict[str, list[str]]` | `{None: []}` | Special symbol configurations. Keys are symbol types (e.g., `"wild"`, `"scatter"`), values are lists of symbol names. Example: `{"wild": ["W"], "scatter": ["S"]}` |
| `special_symbol_names` | `set[str]` | `set()` | Auto-populated by `get_special_symbol_names()`. All unique special symbol names. |
| `paying_symbol_names` | `set[str]` | `set()` | Auto-populated by `get_paying_symbols()`. All symbols that appear in the paytable. |
| `all_valid_symbol_names` | `set[str]` | `set()` | Union of paying + special symbols. Used for reel strip validation. |

### Game Modes

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_game_type` | `str` | `"base_game"` | Base game mode name. Used as key in distributions and event types. |
| `free_game_type` | `str` | `"free_game"` | Free game mode name. |
| `free_spin_triggers` | `dict[str, dict[int, int]]` | `{}` | Scatter count to free spin award mapping, per game mode. Example: `{"base_game": {4: 10, 5: 12}}` means 4 scatters = 10 free spins. |
| `anticipation_triggers` | `dict[str, int]` | — | Scatter count threshold for anticipation animation, per game mode. Usually set to `min(free_spin_triggers) - 1`. |
| `bet_modes` | `list[BetMode]` | `[]` | List of `BetMode` configurations defining distributions, costs, and RTP per mode. |

### Board Display

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_padding` | `bool` | `True` | Include top/bottom padding symbols in board display. When `True`, reveal events include extra symbols above/below the visible board. |
| `output_padding_positions` | `bool` | `True` | Include `paddingPositions` array in reveal events showing reel strip positions. |

### Reel Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `reels` | `dict[str, list[list[str]]]` | `{}` | Reel strip configurations. Keys are reel names (e.g., `"base"`, `"free"`, `"wincap"`), values are 2D arrays loaded from CSV files via `read_reels_csv()`. |
| `padding_reels` | `dict[str, list[list[str]]]` | `{}` | Padding symbol configurations displayed before board reveal. |

### Output Formatting

Controls the structure and size of generated books files. All options are backward-compatible (defaults produce verbose output).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output_regular_json` | `bool` | `True` | If `True`, outputs `.json` when compression is off. If `False`, outputs `.jsonl`. |
| `output_mode` | `OutputMode` | `VERBOSE` | Output format mode. `COMPACT` reduces file size by ~28%. `VERBOSE` for readability. |
| `simple_symbols` | `bool` | `True` | Use string `"L5"` instead of object `{"name": "L5"}` in events. |
| `compress_positions` | `bool` | `True` | Use array format `[reel, row]` instead of object `{"reel": 0, "row": 2}`. |
| `include_losing_boards` | `bool` | `True` | Include board reveals for 0-win spins. Set `False` to skip losing boards. |
| `skip_implicit_events` | `bool` | `False` | Skip redundant events that can be inferred (e.g., `set_final_win` with amount 0). |

### Event Filtering

Controls which events are emitted to books files. Reduces file size by omitting events the client can derive.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip_derived_wins` | `bool` | `False` | Skip `SET_WIN` and `SET_TOTAL_WIN` events (client can sum `WIN` events). |
| `skip_progress_updates` | `bool` | `False` | Skip `UPDATE_FREE_SPINS` and `UPDATE_TUMBLE_WIN` counter events. |
| `verbose_event_level` | `str` | `"full"` | Event verbosity: `"full"` = all events, `"standard"` = important only, `"minimal"` = required only. |
| `exclude_win_detail_keys` | `set[str]` | `set()` | Keys to omit from win event detail objects. Example: `{"baseAmount", "multiplier"}` strips those fields from every win detail. |

### Debug Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_board_in_tumble` | `bool` | `False` | Include the full board state (post-tumble) in tumble events. Useful for verifying that board updates are correct after symbol removal and replacement. Adds a `"board"` key to each tumble event showing the current board. |

### Other

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `write_event_list` | `bool` | `True` | Write event list output during simulation. |
| `maximum_board_multiplier` | `int` | — | Maximum value for grid position multipliers/incrementers. Game-specific (e.g., `512` for farm_pop). |

---

## Run Config (`run_config.toml`)

Defined in `src/config/run_config.py`. Each game has TOML files in `games/<game_name>/`:

- `dev.toml` — Fast development (small simulations, no optimization)
- `prod.toml` — Production (large simulations, full pipeline)
- `run_config.toml` — Symlink to the default config (typically `dev.toml`)

### `[execution]`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num_threads` | `int` | `10` | Number of Python threads for parallel simulation. |
| `rust_threads` | `int` | `20` | Number of Rust threads for optimization. |
| `batching_size` | `int` | `50000` | Number of simulations per batch. |
| `compression` | `bool` | `false` | Enable zstd compression for output files. Required for `run_format_checks`. |
| `profiling` | `bool` | `false` | Enable performance profiling. |

### `[simulation]`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base` | `int` | `10000` | Number of base game simulations. |
| `bonus` | `int \| null` | `null` | Number of bonus game simulations (optional). |
| `free_spin` | `int \| null` | `null` | Number of free spin simulations (optional). |
| `super_spin` | `int \| null` | `null` | Number of super spin simulations (optional). |

### `[pipeline]`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `run_sims` | `bool` | `true` | Generate simulation books. |
| `run_optimization` | `bool` | `false` | Run Rust optimization algorithm. |
| `run_analysis` | `bool` | `false` | Generate PAR sheets and statistics. |
| `run_format_checks` | `bool` | `false` | Run RGS verification tests. Requires `compression = true`. |

### `[analysis]`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `custom_keys` | `list[dict]` | `[]` | Custom search keys for analysis. Example: `[{ symbol = "scatter" }]` |

### Top-level

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_modes` | `list[str]` | `["base"]` | Game modes to include in optimization. Example: `["base", "bonus"]` |

---

## Example: Minimal Game Config

```python
class GameConfig(Config):
    def __init__(self):
        super().__init__()
        self.game_id = "my_game"
        self.win_type = "cluster"
        self.rtp = 0.9700
        self.win_cap = 1000.0
        self.num_reels = 7
        self.num_rows = [7] * self.num_reels

        self.paytable = self.convert_range_table({
            ((5, 5), "H1"): 5.0,
            ((6, 8), "H1"): 12.5,
        })

        self.include_padding = False
        self.special_symbols = {"wild": ["W"], "scatter": ["S"]}

        self.bet_modes = [
            BetMode(name="base", cost=1.0, rtp=self.rtp, max_win=self.win_cap, ...),
        ]
```

## Example: Dev vs Prod TOML

=== "dev.toml"

    ```toml
    target_modes = ["base", "bonus"]

    [execution]
    num_threads = 4
    compression = false

    [simulation]
    base = 500
    bonus = 500

    [pipeline]
    run_sims = true
    run_optimization = false
    run_analysis = false
    ```

=== "prod.toml"

    ```toml
    target_modes = ["base", "bonus"]

    [execution]
    num_threads = 10
    compression = true

    [simulation]
    base = 1000000
    bonus = 1000000

    [pipeline]
    run_sims = true
    run_optimization = true
    run_analysis = true
    run_format_checks = true
    ```
