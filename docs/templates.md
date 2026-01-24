# Template Games

The SDK includes several template games that demonstrate different slot mechanics and serve as starting points for new game development. Each template implements a specific win calculation method and showcases common game features.

## Available Templates

### Core Win Types

| Template | Win Type | Key Features |
|----------|----------|--------------|
| [Cluster](templates-cluster.md) | Cluster-pay | Adjacent matching symbols, tumbles, grid multipliers |
| [Lines](templates-lines.md) | Line-pay | Traditional paylines, simple structure |
| [Ways](templates-ways.md) | Ways-pay | Left-to-right adjacent reels |
| [Scatter](templates-scatter.md) | Scatter-pay | Pay anywhere on board |

### Advanced Features

| Template | Win Type | Special Features |
|----------|----------|------------------|
| [Expanding Wilds](templates-expanding-wilds.md) | Line-pay | Expanding wilds, super spin mode, prize collection |

## Template Structure

Each template follows the refactored architecture with a simplified file structure:

```
games/template_<type>/
  ├── run.py                    # Execution script
  ├── run_config.toml          # Runtime settings (symlink to dev.toml)
  ├── dev.toml                 # Development config (100 sims)
  ├── prod.toml                # Production config (1M sims)
  ├── game_config.py           # Game rules and configuration
  ├── game_state.py            # All game logic (100-400 lines)
  ├── game_optimization.py     # Optimization parameters
  ├── game_events.py           # Custom events (optional)
  └── reels/                   # Reel strip CSV files
      ├── base.csv
      ├── free.csv
      └── wincap.csv
```

## Quick Start with Templates

1. **Copy a template** that matches your desired win type:
   ```bash
   cp -r games/template_lines games/my_new_game
   ```

2. **Update configuration** in `game_config.py`:
   ```python
   self.game_id = "my_new_game"
   self.working_name = "My New Game"
   self.paytable = {...}  # Define your paytable
   ```

3. **Modify reel strips** in `reels/` directory (CSV files)

4. **Implement game logic** in `game_state.py`:
   - Add special symbol handlers
   - Implement game-specific mechanics
   - Complete `run_spin()` and `run_free_spin()` methods

5. **Run the game**:
   ```bash
   make run GAME=my_new_game  # Uses dev.toml (100 sims, fast)
   ```

## Template Documentation

Click on any template below to view detailed documentation including:
- Game mechanics overview
- Special features and behaviors
- Custom functions and handlers
- Configuration examples
- Implementation details

- [Cluster Template](templates-cluster.md)
- [Lines Template](templates-lines.md)
- [Ways Template](templates-ways.md)
- [Scatter Template](templates-scatter.md)
- [Expanding Wilds Template](templates-expanding-wilds.md)
