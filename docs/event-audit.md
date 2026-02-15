# Event Generation Audit - Phase 3.2

**Date**: 2026-01-15
**Purpose**: Audit all event types to identify redundant, optional, and required events for optimization

---

## Event Types Inventory

Based on `src/events/constants.py` and event modules (`core.py`, `free_spins.py`, `tumble.py`, `special_symbols.py`):

### 1. Board/Reveal Events
- **REVEAL** (`reveal_event()`)
  - **When**: Every spin (base and free)
  - **Purpose**: Show board symbols to player
  - **Data**: board (symbols), special_symbols
  - **Frequency**: Every simulation
  - **Required**: Yes (RGS displays board)
  - **Optimization**: Skip for losing spins if `include_losing_boards=False`

### 2. Win Events
- **WIN** (`win_event()`, `prize_win_event()`)
  - **When**: After each win calculation
  - **Purpose**: Show individual win (cluster/line/way/scatter)
  - **Data**: symbol, positions, multiplier, amount
  - **Frequency**: Multiple per winning spin
  - **Required**: Yes (player needs to see what won)
  - **Redundant**: Possibly if already in SET_WIN

- **SET_WIN** (`set_win_event()`)
  - **When**: After all wins calculated
  - **Purpose**: Set total win for current stage
  - **Data**: amount
  - **Frequency**: Once per stage
  - **Required**: Maybe (might be implicit from WIN events sum)
  - **Optimization**: Could be calculated client-side

- **SET_TOTAL_WIN** (`set_total_win_event()`)
  - **When**: After base + free games combined
  - **Purpose**: Set combined win amount
  - **Data**: amount
  - **Frequency**: Once per book
  - **Required**: Maybe (sum of all wins)
  - **Optimization**: Could be calculated client-side

- **SET_FINAL_WIN** (`set_final_win_event()`)
  - **When**: After win cap applied
  - **Purpose**: Final payout amount
  - **Data**: amount, win_cap (if applied)
  - **Frequency**: Once per book
  - **Required**: Yes (actual payout)
  - **Optimization**: Only if different from SET_TOTAL_WIN

- **WIN_CAP** (`win_cap_event()`)
  - **When**: Win exceeds cap
  - **Purpose**: Notify win was capped
  - **Data**: original_amount, capped_amount
  - **Frequency**: Rare (only on max wins)
  - **Required**: Maybe (important for player transparency)

### 3. Free Spin Events
- **TRIGGER_FREE_SPINS** (`trigger_free_spins_event()`)
  - **When**: Scatter symbols trigger free spins
  - **Purpose**: Start free spin mode
  - **Data**: symbol, positions, count, multiplier
  - **Frequency**: ~3-5% of spins
  - **Required**: Yes (mode change)

- **RETRIGGER_FREE_SPINS** (`trigger_free_spins_event()` with retrigger flag)
  - **When**: Scatters during free spins
  - **Purpose**: Add more free spins
  - **Data**: symbol, positions, count
  - **Frequency**: Rare
  - **Required**: Yes (important event)

- **UPDATE_FREE_SPINS** (`update_free_spins_event()`)
  - **When**: After each free spin
  - **Purpose**: Update remaining free spin count
  - **Data**: remaining_spins
  - **Frequency**: Every free spin
  - **Required**: Maybe (client can track)
  - **Optimization**: Could be implicit (count down from trigger)

- **END_FREE_SPINS** (`end_free_spins_event()`)
  - **When**: Free spins exhausted
  - **Purpose**: Exit free spin mode
  - **Data**: total_win
  - **Frequency**: Same as triggers
  - **Required**: Maybe (implicit when count reaches 0)

### 4. Tumble/Cascade Events
- **TUMBLE** (`tumble_event()`)
  - **When**: After wins in tumble games
  - **Purpose**: Show removed symbols and new ones falling
  - **Data**: removedIndexes, newSymbols
  - **Frequency**: Every tumble
  - **Required**: Yes (core mechanic display)

- **SET_TUMBLE_WIN** (`set_tumble_win_event()`)
  - **When**: Start of tumble sequence
  - **Purpose**: Initialize tumble win tracking
  - **Data**: amount (usually 0)
  - **Frequency**: Every tumble sequence
  - **Required**: Maybe
  - **Optimization**: Implicit (first win in sequence)

- **UPDATE_TUMBLE_WIN** (`update_tumble_win_event()`)
  - **When**: After each tumble win
  - **Purpose**: Add to cumulative tumble win
  - **Data**: amount (cumulative)
  - **Frequency**: Every tumble in sequence
  - **Required**: Maybe
  - **Optimization**: Could sum WIN events

### 5. Multiplier Events
- **UPDATE_GLOBAL_MULTIPLIER** (`update_global_mult_event()`)
  - **When**: Global multiplier changes
  - **Purpose**: Show multiplier progression
  - **Data**: new_multiplier
  - **Frequency**: Game-specific
  - **Required**: Yes (visible to player)

### 6. Special Feature Events
- **UPGRADE** (`upgrade_event()`)
  - **When**: Symbols upgraded to higher value
  - **Purpose**: Show transformation
  - **Data**: from_positions, to_position, from_symbol, to_symbol
  - **Frequency**: Game-specific
  - **Required**: Yes (visual effect)

---

## Redundancy Analysis

### Definitely Redundant
None identified - all events serve specific purposes

### Potentially Redundant (Can Be Derived)

1. **SET_WIN** - Sum of WIN events
   - **Savings**: 1 event per stage × ~30% hit rate = ~0.3 events/spin
   - **Risk**: Low (simple sum)

2. **SET_TOTAL_WIN** - Sum of base + free wins
   - **Savings**: 1 event per book
   - **Risk**: Low (simple sum)

3. **UPDATE_FREE_SPINS** - Count down from trigger
   - **Savings**: N events per free spin sequence
   - **Risk**: Low (trivial calculation)

4. **UPDATE_TUMBLE_WIN** - Sum of tumble WIN events
   - **Savings**: N events per tumble sequence
   - **Risk**: Low (simple sum)

5. **SET_TUMBLE_WIN** (amount=0) - Implicit start
   - **Savings**: 1 event per tumble sequence
   - **Risk**: Low (start is obvious)

### Conditional Events (Can Be Skipped)

1. **REVEAL** for losing spins
   - **Condition**: `include_losing_boards=False` AND win amount = 0
   - **Savings**: ~70% of reveals (most spins lose)
   - **Risk**: None (already implemented in config)

2. **SET_FINAL_WIN** when same as SET_TOTAL_WIN
   - **Condition**: No win cap applied
   - **Savings**: Most spins (win cap rare)
   - **Risk**: Low (redundant information)

3. **END_FREE_SPINS** (implicit)
   - **Condition**: Can be inferred from spin count
   - **Savings**: 1 event per free spin sequence
   - **Risk**: Medium (mode change is important)

---

## Proposed Optimization Strategy

### Phase 3.2.1: Add Event Filtering Config

Add new config options:
```python
class Config:
    # Existing
    output_mode: OutputMode = OutputMode.VERBOSE
    skip_implicit_events: bool = False
    include_losing_boards: bool = True

    # New Phase 3.2
    skip_derived_wins: bool = False  # Skip SET_WIN, SET_TOTAL_WIN if True
    skip_progress_updates: bool = False  # Skip UPDATE_FREE_SPINS, UPDATE_TUMBLE_WIN
    verbose_event_level: str = "full"  # "full", "standard", "minimal"
```

### Phase 3.2.2: Event Categories

**Required (Always Emit)**:
- REVEAL (unless losing and include_losing_boards=False)
- WIN (individual wins)
- TRIGGER_FREE_SPINS, RETRIGGER_FREE_SPINS
- TUMBLE
- UPDATE_GLOBAL_MULTIPLIER, UPGRADE
- SET_FINAL_WIN

**Standard (Emit by Default)**:
- SET_WIN, SET_TOTAL_WIN
- WIN_CAP
- END_FREE_SPINS

**Verbose (Only if verbose_event_level="full")**:
- UPDATE_FREE_SPINS
- UPDATE_TUMBLE_WIN
- SET_TUMBLE_WIN

### Phase 3.2.3: Estimated Savings

**Conservative Estimate** (skip_derived_wins=True, skip_progress_updates=True):
- SET_WIN: 0.3 events/spin
- UPDATE_FREE_SPINS: 0.15 events/spin (avg 5 free spins × 3% trigger rate)
- UPDATE_TUMBLE_WIN: 0.05 events/spin (tumble games only)
- SET_TUMBLE_WIN: 0.05 events/spin (tumble games only)
- **Total**: ~0.55 events/spin

**Current Average**: ~2.5 events/spin (estimated)
**After Optimization**: ~2.0 events/spin
**Savings**: ~20% event count reduction

**File Size Impact**:
- Current (Phase 3.1): 27.9% reduction from baseline
- With Phase 3.2: Additional ~10-15% reduction
- **Total Projected**: 35-40% reduction from baseline

---

## Implementation Plan

### Task 3.2.1: Add Configuration Options
- Add new config fields
- Update Config class docstrings
- Add tests for new options

### Task 3.2.2: Update Event Emission Logic
- Modify event functions to check config
- Add conditional emission
- Maintain backward compatibility

### Task 3.2.3: Create EventFilter Class
- Centralize filtering logic
- Support custom predicates
- Easy to extend

### Task 3.2.4: Update Documentation
- Document event categories
- Explain filtering options
- Provide examples

### Task 3.2.5: Test and Benchmark
- Run tests with different filter levels
- Measure file size improvements
- Verify RGS compatibility

---

## Risks and Mitigation

### Risk 1: RGS Compatibility
**Impact**: High
**Mitigation**: Make all optimizations opt-in, default to verbose

### Risk 2: Client-Side Calculation Bugs
**Impact**: Medium
**Mitigation**: Document clearly which events are skippable, provide examples

### Risk 3: Game-Specific Requirements
**Impact**: Medium
**Mitigation**: Allow per-game override of event filtering

---

## Conclusion

Phase 3.2 can provide an additional 10-15% file size reduction through intelligent event filtering, bringing total optimization to 35-40% from baseline. All optimizations are:
- **Backward compatible**: Default to verbose
- **Opt-in**: Require explicit config changes
- **Safe**: Only skip truly redundant events
- **Documented**: Clear guidance on what to skip

**Recommendation**: Proceed with implementation, prioritizing safe optimizations first.
