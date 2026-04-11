# Farm Pop

7×7 cluster-pay slot with tumble mechanics and grid incrementers. Clusters of 5+ adjacent (orthogonal) matching symbols form a win. Winning symbols are removed and remaining symbols fall down, with new symbols drawn from the reel strip. Tumbles repeat until no new wins form.

## Symbols

| Symbol | Type | Description |
|--------|------|-------------|
| H1 | Premium | Highest-paying (e.g. Golden Chicken) |
| H2 | Premium | |
| H3 | Premium | |
| H4 | Premium | |
| L1 | Low | |
| L2 | Low | |
| L3 | Low | |
| L4 | Low | Lowest-paying |
| W | Wild | Substitutes for any paying symbol in cluster formation |
| S | Scatter | Triggers free spins (not part of cluster wins) |

## Paytable

Cluster sizes are grouped into 14 tiers. With grid incrementers, the effective count can exceed the physical cluster size.

| Tier | Count | H1 | H2 | H3 | H4 | L1 | L2 | L3 | L4 |
|------|----------|------|------|------|------|------|------|------|------|
| t1 | 5 | 1.0 | 0.7 | 0.5 | 0.4 | 0.25 | 0.2 | 0.15 | 0.1 |
| t2 | 6 | 1.5 | 1.0 | 0.7 | 0.5 | 0.35 | 0.3 | 0.2 | 0.15 |
| t3 | 7–8 | 2.5 | 1.8 | 1.2 | 0.9 | 0.6 | 0.5 | 0.35 | 0.25 |
| t4 | 9–10 | 4.0 | 2.8 | 2.0 | 1.5 | 1.0 | 0.8 | 0.6 | 0.4 |
| t5 | 11–13 | 6.5 | 4.5 | 3.2 | 2.5 | 1.6 | 1.3 | 1.0 | 0.6 |
| t6 | 14–16 | 10.0 | 7.0 | 5.0 | 3.8 | 2.5 | 2.0 | 1.5 | 1.0 |
| t7 | 17–20 | 15.0 | 10.0 | 7.5 | 5.5 | 3.8 | 3.0 | 2.2 | 1.5 |
| t8 | 21–24 | 22.0 | 15.0 | 11.0 | 8.0 | 5.5 | 4.5 | 3.5 | 2.5 |
| t9 | 25–29 | 35.0 | 24.0 | 17.0 | 13.0 | 8.5 | 7.0 | 5.0 | 4.0 |
| t10 | 30–34 | 55.0 | 38.0 | 27.0 | 20.0 | 13.0 | 10.0 | 7.5 | 6.0 |
| t11 | 35–40 | 85.0 | 58.0 | 42.0 | 30.0 | 20.0 | 15.0 | 11.0 | 9.0 |
| t12 | 41–46 | 135.0 | 90.0 | 65.0 | 46.0 | 30.0 | 24.0 | 17.0 | 13.0 |
| t13 | 47–53 | 225.0 | 150.0 | 100.0 | 72.0 | 48.0 | 36.0 | 26.0 | 20.0 |
| t14 | 54–60 | 400.0 | 275.0 | 185.0 | 130.0 | 80.0 | 55.0 | 40.0 | 28.0 |

Values are multipliers of the bet amount. See `game_config.py` for the source definition.

## Grid Incrementers

Both base and free games use a grid incrementer overlay (`revealGridIncrementers` event). Grid incrementers reset at the start of each spin (base) or at the start of the bonus round (free).

Each board position has an incrementer value that starts at 0 (deactivated). When a position contributes to a winning cluster, it activates at 1. On subsequent tumble wins at the same position, the incrementer increases by +1 (capped at `maximum_board_multiplier = 512`).

Unlike grid multipliers which multiply the base win, grid incrementers **add to the symbol count** and look up a higher paytable tier:

```
effective_count = cluster_size + sum(grid_incrementers_in_cluster)
win = paytable[effective_count, symbol] × global_multiplier
```

For example, a 7-symbol H2 cluster (base win 1.8×) with 3 positions having incrementer value 1 each becomes a 10-symbol H2 lookup (win 2.8×).

If `effective_count` exceeds the max paytable entry, it caps at the highest available tier.

## Base Game

Standard tumbling game with grid incrementers. Wilds substitute for any paying symbol in cluster formation. Grid incrementers reset at the start of each spin and accumulate across tumbles within that spin.

### Free Spin Trigger (Base)

| Scatter Count | Free Spins Awarded |
|---------------|-------------------|
| 4 | 10 |
| 5 | 12 |
| 6 | 15 |
| 7 | 18 |
| 8 | 20 |

Anticipation triggers at 3 scatters (one below minimum).

## Free Game

Same tumble and cluster mechanics as base game. Grid incrementers **persist across all tumbles and free spins** within a single bonus round, resetting only at the start of the feature. This allows incrementers to build up over many spins, creating escalating win potential.

### Re-trigger (Free Game)

| Scatter Count | Additional Free Spins |
|---------------|----------------------|
| 3 | 5 |
| 4 | 8 |
| 5 | 10 |
| 6 | 12 |
| 7 | 15 |
| 8 | 18 |

Anticipation triggers at 2 scatters.

## Bet Modes

### Base (cost: 1.0×)

**Distributions:**

| Distribution | Quota | Description |
|-------------|-------|-------------|
| `wincap` | 0.001 | Forces free game + win cap (10,000×). Uses wincap reel strip (5:1 weight vs free). |
| `free_game` | 0.1 | Forces free game trigger. Scatter distribution: 4S (5:1 weight) or 5S. |
| `0` | 0.4 | Forced zero-win outcome. Base reel strip only. |
| `base_game` | 0.5 | Standard base game outcome with non-zero win. Base reel strip only. |

### Ante Modes

Ante modes increase the bet cost for a better free spin trigger rate. Higher antes offer progressively better cost-per-trigger, rewarding players who take the risk.

| Mode | Cost | Free Spin HR | Cost per Trigger |
|------|------|-------------|-----------------|
| Base | 1× | 1:200 | 200× |
| Ante-2x | 2× | 1:90 | 180× (10% better) |
| Ante-5x | 5× | 1:33 | 165× (17% better) |
| Ante-10x | 10× | 1:15 | 150× (25% better) |

All ante modes share the same distributions as base.

### Bonus (cost: 100×)

| Distribution | Quota | Description |
|-------------|-------|-------------|
| `wincap` | 0.001 | Forces free game + win cap. Includes multiplier values (2×–50×). |
| `free_game` | 0.1 | Standard free game outcome. |

Bonus mode includes weighted multiplier values per game type:

| Multiplier | Weight |
|------------|--------|
| 2× | 10 |
| 3× | 20 |
| 4× | 30 |
| 5× | 20 |
| 10× | 20 |
| 20× | 20 |
| 50× | 10 |

## Optimization RTP Splits

All modes target 0.96 total RTP. Wincap contributes 0.01 RTP across all modes.

| Mode | Free Game | Base Game (remainder) |
|------|-----------|----------------------|
| Base | 0.37 | 0.58 |
| Ante-2x | 0.45 | 0.50 |
| Ante-5x | 0.55 | 0.40 |
| Ante-10x | 0.65 | 0.30 |
| Bonus | 0.95 | — |

## Reel Strips

| File | Used By |
|------|---------|
| `reels/base.csv` | Base game (all distributions) |
| `reels/free.csv` | Free game (standard) |
| `reels/wincap.csv` | Free game (wincap distribution, 5:1 weight vs free) |

## Events

Events emitted during gameplay, as defined in the event config files (`build/configs/event_config_base.json`, `event_config_bonus.json`):

### Core Events

| Event | When | Key Fields |
|-------|------|------------|
| `reveal` | Start of each spin/free spin | `board` (7×7 symbol grid), `gameType` ("baseGame"/"freeGame"), `anticipation` (per-reel scatter count toward trigger) |
| `win` | Winning cluster(s) found | `reason` ("cluster"), `amount`, `totalAmount`, `details[]` — each detail has `symbol`, `positions` (reel/row pairs), `amount`, `count` (physical cluster size), `positionIncrements`, `effectiveCount` |
| `showWin` | After win presentation | `amount`, `level` (win tier for presentation) |

### Tumble Events

| Event | When | Key Fields |
|-------|------|------------|
| `tumble` | After winning symbols removed | `newSymbols` (per-reel arrays of replacement symbols), `removedIndexes` (per-reel arrays of removed row indices) |
| `revealGridIncrementers` | After grid update | `gridIncrementers` (7×7 integer grid of current incrementer values) |

### Win Accounting Events

| Event | When | Key Fields |
|-------|------|------------|
| `setWin` | After each tumble round | `amount` (cumulative tumble win) |
| `setTotalWin` | End of all tumbles | `amount` (total spin win) |
| `setFinalWin` | End of complete spin cycle | `amount` (base + free combined) |

### Free Spin Events

| Event | When | Key Fields |
|-------|------|------------|
| `triggerFreeSpins` | Scatter threshold met in base | `total` (spins awarded), `positions` (scatter locations) |
| `updateFreeSpins` | Start of each free spin | `amount` (current spin number), `total` (total free spins) |
| `retriggerFreeSpins` | Scatter threshold met in free game | `total` (new total including added spins), `positions` (scatter locations) |
| `endFreeSpins` | All free spins completed | `amount` (total free game win), `level` (win tier) |

### Event Flow

**Base game spin:**
```
reveal → [win → setWin → revealGridIncrementers → tumble]* → showWin → setTotalWin
  └─ if scatters ≥ 4: triggerFreeSpins → [free spin loop] → endFreeSpins
→ setFinalWin
```

**Free spin (each spin within bonus):**
```
updateFreeSpins → reveal → [win → setWin → revealGridIncrementers → tumble]* → showWin → setTotalWin
  └─ if scatters ≥ 3: retriggerFreeSpins
```

`*` = tumble loop repeats until no new wins. `revealGridIncrementers` is only emitted when there are wins. Win accounting events (`setWin`, `setTotalWin`) may be filtered by event verbosity settings.

## Configuration Reference

| Parameter | Value | Source |
|-----------|-------|--------|
| `game_id` | `"farm_pop"` | `game_config.py` |
| `win_type` | `"cluster"` | `game_config.py` |
| `rtp` | 0.96 | `game_config.py` |
| `win_cap` | 10,000× | `game_config.py` |
| `num_reels` | 7 | `game_config.py` |
| `num_rows` | [7, 7, 7, 7, 7, 7, 7] | `game_config.py` |
| `maximum_board_multiplier` | 512 | `game_config.py` |
| `include_padding` | false | `game_config.py` |
| `include_board_in_tumble` | false | `game_config.py` |
| `exclude_win_detail_keys` | `{baseAmount, multiplier}` | `game_config.py` |

### Optimization RTP Splits

**Base mode** (must sum to 0.96):
| Condition | RTP Target |
|-----------|-----------|
| `wincap` | 0.01 |
| `zero` | 0.00 |
| `free_game` | 0.37 |
| `base_game` | 0.58 (remainder) |

**Bonus mode** (must sum to 0.96):
| Condition | RTP Target |
|-----------|-----------|
| `wincap` | 0.01 |
| `free_game` | 0.95 (remainder) |

Hit rates: base = 3.5, free = 200.

## Notes

Because of the separation between base game and free game distribution criteria, there is an additional free_spin entry check (`force_free_game`) to ensure the criteria requiring a forced free spin condition is met. Otherwise, Scatter symbols tumbling onto the board during base game criteria may incorrectly trigger free spins.
