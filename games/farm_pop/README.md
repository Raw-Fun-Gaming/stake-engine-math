# Farm Pop

7x7 board. Clusters of 5 or more adjacent (horizontally/vertically touching) like-symbols form a win. Winning symbols are removed and symbols above tumble down to fill the gaps, with new symbols drawn from the reel strip to fill remaining empty positions. Tumbles repeat until no new wins form.

## Base Game

Standard tumbling game with Scatter (S) and Wild (W) symbols. Wilds substitute for any paying symbol in cluster formation. Minimum of 4 Scatter symbols required for free spin trigger.

## Free Game

Same tumble mechanics as base game, with an additional grid incrementer overlay (`revealGridIncrementers` event).

Each board position has an incrementer value that starts at 0 (deactivated). When a position contributes to a winning cluster, it activates at 1. On subsequent tumble wins at the same position, the incrementer increases by +1 (capped at `maximum_board_multiplier`).

Unlike grid multipliers which multiply the base win, grid incrementers **add to the symbol count** and look up a higher paytable tier:

```
effective_count = cluster_size + sum(grid_incrementers_in_cluster)
win = paytable[effective_count, symbol] x global_multiplier
```

For example, a 7-symbol H2 cluster (base win 3.2) with 3 positions having incrementer value 1 each becomes a 10-symbol H2 lookup (win 10.0). This creates a more intuitive visual representation (e.g., 1 pig symbol becomes 2 pig symbols) with lower variance than multipliers.

If `effective_count` exceeds the max paytable entry, it caps at the highest available tier.

Grid incrementers persist across all tumbles and free spins within a single bonus round, resetting only at the start of the feature.

A minimum of 3 Scatter symbols required for re-triggers.

## Notes

Because of the separation between base game and free game distribution criteria, there is an additional free_spin entry check (`force_free_game`) to ensure the criteria requiring a forced free spin condition is met. Otherwise, Scatter symbols tumbling onto the board during base game criteria may incorrectly trigger free spins.
