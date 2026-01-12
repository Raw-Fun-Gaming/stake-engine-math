# Phase 2 Execution Plan

**Status**: Ready to Begin
**Estimated Duration**: 2-3 weeks
**Phase 1 Complete**: ✅ (All foundation work done)

---

## Overview

Phase 2 focuses on code quality improvements through systematic renaming, constant extraction, comprehensive documentation, and improved error handling. This phase will make the codebase more maintainable and professional.

## Sub-Phases

### 2.1 Comprehensive Renaming Pass (4 days)

**Goal**: Rename all variables, methods, and attributes to be clear and descriptive.

**Impact**: 🔴 BREAKING CHANGES - All games and dependent code will need updates

**Key Renames:**

#### Variables
- `self.fs` → `self.current_free_spin`
- `self.tot_fs` → `self.total_free_spins`
- `self.sim` → `self.simulation_id`
- `self.gametype` → `self.game_mode`
- `self.anticipation` → `self.anticipation_flags`
- `self.wincap_triggered` → `self.win_cap_reached`

#### Methods
- `check_fs_condition()` → `has_free_spin_trigger()`
- `run_freespin_from_base()` → `start_free_spin_mode()`
- `update_fs_retrigger_amt()` → `add_retriggered_spins()`
- `imprint_wins()` → `record_final_wins()`
- `reset_book()` → `reset_simulation_state()`

#### Config Attributes
- `basegame_type` → `base_game_mode`
- `freegame_type` → `free_spin_mode`
- `num_sim_args` → `simulation_counts`
- `bet_modes` → `game_modes`

**Execution Strategy:**
1. Create comprehensive mapping document
2. Use search & replace with regex for systematic updates
3. Update one module at a time, commit after each
4. Run tests after each major rename
5. Update all 7 games to use new names

---

### 2.2 Extract Constants and Enums (2 days)

**Goal**: Replace magic strings and numbers with named constants and enums.

**Impact**: 🟡 MODERATE CHANGES - Some API changes, mostly additions

**Tasks:**
1. Create `GameMode` enum (replace "basegame"/"freegame" strings)
2. Create `WinType` enum (replace "cluster"/"lines"/"ways"/"scatter" strings)
3. Extract magic numbers to named constants
4. Create `src/constants.py` file
5. Update `EventConstants` with any missing events

**Example:**
```python
# src/constants.py
from enum import Enum

class GameMode(str, Enum):
    """Game mode types."""
    BASE = "basegame"
    FREE_SPIN = "freegame"
    BONUS = "bonus"
    SUPER_SPIN = "superspin"

class WinType(str, Enum):
    """Win calculation types."""
    CLUSTER = "cluster"
    LINES = "lines"
    WAYS = "ways"
    SCATTER = "scatter"

# Magic number constants
DEFAULT_NUM_REELS = 5
DEFAULT_NUM_ROWS = 3
MAX_FREE_SPINS = 100
DEFAULT_RTP = 0.96
```

---

### 2.3 Add Comprehensive Docstrings (Partially Done)

**Goal**: Ensure all modules, classes, and methods have clear documentation.

**Impact**: 🟢 NO BREAKING CHANGES - Documentation only

**Status**: ~60% complete from Phase 1.2

**Remaining Tasks:**
1. Add module-level docstrings to all files
2. Add class docstrings explaining purpose and usage
3. Add examples to key method docstrings
4. Document complex algorithms inline
5. Generate API documentation with Sphinx (optional)

**Priority Areas:**
- `src/write_data/` modules (no docstrings yet)
- `src/executables/` modules (minimal docstrings)
- Game-specific modules (partial coverage)

---

### 2.4 Improve Error Handling (3 days)

**Goal**: Replace warnings with proper exceptions and add validation.

**Impact**: 🟡 MODERATE CHANGES - Better error messages, some behavior changes

**Tasks:**
1. Create custom exception classes
2. Replace `warn()` with exceptions where appropriate
3. Add configuration validation
4. Add helpful error messages
5. Add logging throughout (optional)

**Custom Exceptions:**
```python
# src/exceptions.py
class GameEngineError(Exception):
    """Base exception for all game engine errors."""
    pass

class GameConfigError(GameEngineError):
    """Raised when game configuration is invalid."""
    pass

class ReelStripError(GameEngineError):
    """Raised when reel strip files are missing or malformed."""
    pass

class WinCalculationError(GameEngineError):
    """Raised when win calculation fails."""
    pass

class SimulationError(GameEngineError):
    """Raised when simulation fails."""
    pass
```

---

## Execution Order

### Recommended Approach: Incremental with Testing

**Option A: Full Phase 2 (2-3 weeks)**
1. 2.2 Extract Constants/Enums (2 days) ← Start here
2. 2.4 Improve Error Handling (3 days)
3. 2.3 Complete Docstrings (2 days)
4. 2.1 Comprehensive Renaming (4 days) ← Do last (most breaking)

**Rationale**: Do non-breaking changes first, then tackle the big rename at the end when everything else is stable.

**Option B: Minimal Breaking Changes**
1. 2.2 Extract Constants/Enums (enums only)
2. 2.3 Complete Docstrings
3. 2.4 Improve Error Handling
4. Skip 2.1 Renaming for now

**Rationale**: Avoid breaking changes entirely, focus on additions and improvements.

**Option C: Just Documentation**
1. 2.3 Complete Docstrings only

**Rationale**: Quickest path to better code understanding, zero breaking changes.

---

## Risk Assessment

### High Risk (Breaking Changes)
- **Phase 2.1 Renaming**: Will break all games, tests, and dependent code
  - Mitigation: Comprehensive mapping document, systematic approach, extensive testing

### Medium Risk (Some API Changes)
- **Phase 2.2 Enums**: May require code updates where strings are compared
  - Mitigation: Use string enums that are backward compatible
- **Phase 2.4 Error Handling**: May change program behavior (exceptions vs warnings)
  - Mitigation: Add try/except blocks, maintain backward compatibility where possible

### Low Risk (Additions Only)
- **Phase 2.2 Constants**: Pure additions, doesn't break existing code
- **Phase 2.3 Docstrings**: Pure additions, zero code changes

---

## Testing Strategy

After each sub-phase:
1. Run all unit tests
2. Run simulation for each game
3. Verify output format hasn't changed
4. Check that books files are still generated correctly
5. Run optimization on at least one game

---

## Rollback Plan

Each sub-phase should be committed separately:
- Sub-phase complete → Commit
- Tests pass → Push to branch
- Tests fail → Git revert

Keep `main` branch stable, do all Phase 2 work on `dev` branch.

---

## Recommended Action

Given that Phase 1 is complete and provides a solid foundation, I recommend:

**Suggested Path: Option A (Incremental Full Phase 2)**

Start with Phase 2.2 (Extract Constants/Enums) because:
1. Low-to-moderate breaking changes
2. Immediate code quality improvement
3. Makes future work easier
4. Can be done incrementally

Then proceed with 2.4, 2.3, and finally 2.1 when everything is stable.

---

## Questions for Review

1. **Scope**: Do you want full Phase 2 or a subset?
2. **Breaking Changes**: Are you comfortable with the renaming pass (2.1)?
3. **Testing**: Do you have a test suite to validate changes?
4. **Timeline**: Is 2-3 weeks acceptable for full Phase 2?

---

**Created**: 2026-01-12
**Last Updated**: 2026-01-12
