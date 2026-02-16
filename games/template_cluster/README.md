# Cluster-based win game

7x7 board. Clusters of 5 or more adjacent (horizontally/vertically touching) like-symbols form a win. Winning symbols are removed and symbols above tumble down to fill the gaps, with new symbols drawn from the reel strip to fill remaining empty positions. Tumbles repeat until no new wins form.

## Base Game

Standard tumbling game with Scatter (S) and Wild (W) symbols. Wilds substitute for any paying symbol in cluster formation. Minimum of 4 Scatter symbols required for free spin trigger.

## Free Game

Same tumble mechanics as base game, with an additional grid multiplier overlay (`revealGridMultipliers` event).

Each board position has a multiplier value that starts at 0 (deactivated). When a position contributes to a winning cluster, it activates at 1x. On subsequent tumble wins at the same position, the multiplier increments by +1 (capped at `maximum_board_multiplier`).

During win calculation, the multiplier values at all positions in a cluster are summed to produce a single board multiplier applied to the base paytable amount:

```
win = paytable[cluster_size, symbol] x sum(grid_multipliers_in_cluster) x global_multiplier
```

Grid multipliers persist across all tumbles and free spins within a single bonus round, resetting only at the start of the feature.

A minimum of 3 Scatter symbols required for re-triggers.

## Notes

Because of the separation between base game and free game distribution criteria, there is an additional free_spin entry check (`force_free_game`) to ensure the criteria requiring a forced free spin condition is met. Otherwise, Scatter symbols tumbling onto the board during base game criteria may incorrectly trigger free spins.
