# Stake Engine Math SDK - Refactor Plan

**Date**: 2026-01-10
**Status**: Planning Phase
**Goal**: Improve code quality, reduce learning curve, optimize output format

## Executive Summary

This document outlines a comprehensive refactoring plan for the Stake Engine Math SDK. The project will remain in Python (no TypeScript port) as it focuses solely on slot game simulation and result generation, while the web frontend is already TypeScript-based.

**Estimated Timeline**: 6-8 weeks
**Approach**: Incremental improvements with continuous testing
**Risk Level**: Low-Medium (extensive testing required)

---

## Current Issues

### 1. Code Quality Issues
- **Inconsistent naming**: Mix of abbreviated (`fs`, `tot_fs`, `sim`) and full names (`reset_book`, `final_win`)
- **Poor variable semantics**: `repeat` flag, `gametype` string, `criteria` unclear purpose
- **Magic numbers**: Hardcoded values throughout codebase
- **Minimal type hints**: Most functions lack return type annotations
- **Unclear method purposes**: Methods like `check_game_repeat()` need better documentation

### 2. Architectural Issues
- **4-layer inheritance**: `GameState → GameStateOverride → GameExecutables → State` is too deep
- **Unclear responsibility boundaries**: When to override in which layer?
- **Tight coupling**: Games import entire override classes
- **Abstract class misuse**: Mix of abstract and concrete in `GeneralGameState`
- **Singleton pattern inconsistency**: Some classes use it, others don't

### 3. Output Bloat
- **Redundant data in books**: Every simulation includes verbose board representation
- **Inefficient symbol format**: `{"name": "L5"}` instead of `"L5"`
- **Verbose position arrays**: `{"reel": 0, "row": 2}` repeated thousands of times
- **Unnecessary events**: Many events could be implicit or compressed
- **File sizes**: 248k lines for 10k simulations (~25 lines per sim)

### 4. Documentation Issues
- **Steep learning curve**: Despite good CLAUDE.md, architecture is hard to grasp
- **Hidden conventions**: Event system, betmode setup, optimization require deep knowledge
- **Missing inline docs**: Many methods lack docstrings
- **Unclear file purposes**: `game_calculations.py` vs `game_executables.py` confusion

---

## Refactor Plan

### Phase 1: Foundation (Weeks 1-2)

#### 1.1 Establish Code Standards
**Priority**: High
**Effort**: 2 days

**Tasks:**
- [ ] Create `CONTRIBUTING.md` with naming conventions
- [ ] Define Python style guide (follow PEP 8 + project-specific rules)
- [ ] Set up pre-commit hooks for code formatting (black, isort, flake8)
- [ ] Configure mypy for strict type checking
- [ ] Add .editorconfig for consistent IDE settings

**Naming Conventions:**
```python
# Variables
✗ fs, tot_fs, sim          → ✓ free_spin_count, total_free_spins, simulation_id
✗ gametype                 → ✓ game_mode (or game_type for consistency)
✗ num_sim_args            → ✓ simulation_counts
✗ criteria                → ✓ force_condition (clarify purpose)

# Methods
✗ reset_fs_spin()         → ✓ reset_free_spin_state()
✗ imprint_wins()          → ✓ finalize_win_record()
✗ check_fs_condition()    → ✓ has_free_spin_trigger()

# Classes
✗ GeneralGameState        → ✓ BaseGameState
✗ GameStateOverride       → ✓ (merge into GameLogic)
✗ GameExecutables         → ✓ (merge into GameLogic)

# Constants
✗ Hardcoded strings       → ✓ Use EventConstants, GameMode enum
```

#### 1.2 Add Comprehensive Type Hints
**Priority**: High
**Effort**: 3 days

**Tasks:**
- [ ] Add return type annotations to all functions
- [ ] Add parameter type hints to all methods
- [ ] Create type aliases for common patterns: `Board = list[list[Symbol]]`
- [ ] Use `TypedDict` for configuration dictionaries
- [ ] Enable strict mypy checking
- [ ] Fix all type errors

**Example:**
```python
# Before
def draw_board(self):
    ...

# After
def draw_board(self) -> Board:
    """Draw a random board based on current reel strips and game mode.

    Returns:
        5x5 board of Symbol objects representing the drawn positions.
    """
    ...
```

#### 1.3 Flatten Inheritance Hierarchy
**Priority**: Critical
**Effort**: 5 days

**Current Structure:**
```
State (src/state/state.py)
  ↑
GameExecutables (game_executables.py) - win calculations
  ↑
GameStateOverride (game_override.py) - custom overrides
  ↑
GameState (gamestate.py) - main game loop
```

**New Structure:**
```
BaseGameState (src/state/base_game_state.py)
  ├── Core simulation infrastructure
  ├── Book management
  ├── Event system
  ├── Win management
  └── Abstract methods for games to implement

GameImplementation (games/<game>/game_state.py)
  ├── Game-specific logic
  ├── Win calculation methods
  ├── Special symbol handlers
  └── Game loop (run_spin, run_freespin)
```

**Tasks:**
- [ ] Rename `State` → `BaseGameState`
- [ ] Merge `GameExecutables` and `GameStateOverride` into single override pattern
- [ ] Move win calculation helpers to `src/calculations/` utilities
- [ ] Create clear abstract method contracts
- [ ] Update all games to use new structure
- [ ] Update documentation

**Benefits:**
- 2 layers instead of 4
- Clear separation: base infrastructure vs game logic
- Easier to understand which methods to override
- Less mental overhead for new developers

---

### Phase 2: Code Quality Improvements (Weeks 3-4)

#### 2.1 Comprehensive Renaming Pass
**Priority**: High
**Effort**: 4 days

**Tasks:**
- [ ] Create mapping document of old → new names
- [ ] Use IDE refactoring tools for safe renaming
- [ ] Update all variable names to be descriptive
- [ ] Rename all method names to be verb-based and clear
- [ ] Update configuration keys to be consistent
- [ ] Rename files to match their purpose

**Key Renames:**
```python
# Core variables
self.fs → self.current_free_spin
self.tot_fs → self.total_free_spins
self.sim → self.simulation_id
self.gametype → self.game_mode
self.anticipation → self.anticipation_flags
self.wincap_triggered → self.win_cap_reached

# Methods
check_fs_condition() → has_free_spin_trigger()
run_freespin_from_base() → start_free_spin_mode()
update_fs_retrigger_amt() → add_retriggered_spins()
imprint_wins() → record_final_wins()
reset_book() → reset_simulation_state()

# Config attributes
basegame_type → base_game_mode
freegame_type → free_spin_mode
num_sim_args → simulation_counts
bet_modes → game_modes
```

#### 2.2 Extract Constants and Enums
**Priority**: Medium
**Effort**: 2 days

**Tasks:**
- [ ] Create `GameMode` enum (replace string "basegame"/"freegame")
- [ ] Create `WinType` enum (replace string "cluster"/"lines"/"ways")
- [ ] Extract magic numbers to named constants
- [ ] Create configuration constants file
- [ ] Update EventConstants with any missing events

**Example:**
```python
# Before
self.gametype = "basegame"
if self.config.win_type == "cluster":
    ...

# After
from src.constants import GameMode, WinType

self.game_mode = GameMode.BASE
if self.config.win_type == WinType.CLUSTER:
    ...
```

#### 2.3 Add Comprehensive Docstrings
**Priority**: High
**Effort**: 4 days

**Tasks:**
- [ ] Add module-level docstrings to all files
- [ ] Add class docstrings explaining purpose and usage
- [ ] Add method docstrings with Args/Returns/Raises
- [ ] Document complex algorithms inline
- [ ] Add examples to docstrings for key methods
- [ ] Generate API documentation with Sphinx

**Example:**
```python
class BaseGameState(ABC):
    """Base class for all slot game simulations.

    Provides core infrastructure for:
    - Random board generation from reel strips
    - Event recording and book management
    - Win calculation and management
    - Free spin triggering and tracking
    - RNG seeding for reproducibility

    Games should inherit from this class and implement:
    - run_spin(): Main game logic for a single spin
    - run_freespin(): Free spin game logic
    - Special symbol handlers via assign_special_sym_function()

    Example:
        >>> class MyGame(BaseGameState):
        ...     def run_spin(self, simulation_id: int) -> None:
        ...         self.reset_seed(simulation_id)
        ...         self.draw_board()
        ...         self.calculate_wins()
    """
```

#### 2.4 Improve Error Handling
**Priority**: Medium
**Effort**: 3 days

**Tasks:**
- [ ] Create custom exception classes
- [ ] Replace `warn()` with proper exceptions where appropriate
- [ ] Add validation for configuration files
- [ ] Add helpful error messages
- [ ] Create error recovery mechanisms
- [ ] Add logging throughout

**Example:**
```python
class GameConfigError(Exception):
    """Raised when game configuration is invalid."""
    pass

class ReelStripError(Exception):
    """Raised when reel strip files are missing or malformed."""
    pass

# Usage
def validate_config(self) -> None:
    """Validate game configuration before simulation.

    Raises:
        GameConfigError: If configuration is invalid or incomplete.
    """
    if not self.config.paytable:
        raise GameConfigError(
            f"Game '{self.config.game_id}' missing paytable definition. "
            "Please define paytable in game_config.py"
        )
```

---

### Phase 3: Output Optimization (Week 5)

#### 3.1 Compress Books Format
**Priority**: High
**Effort**: 4 days

**Current Issues:**
- `{"name": "L5"}` repeated thousands of times
- Position objects are verbose
- Reveal events include full board even for losing spins
- Many implicit events could be removed

**Optimization Strategies:**

**Strategy A: Compact Symbol Format**
```python
# Before (verbose)
{"name": "L5"}

# After (compact)
"L5"

# Savings: ~15 bytes per symbol × 25 symbols per board × 10k sims = 3.75MB
```

**Strategy B: Compact Position Format**
```python
# Before (verbose)
{"reel": 0, "row": 2}

# After (compact) - use tuple or string
[0, 2]  # or "0,2"

# Savings: ~20 bytes per position
```

**Strategy C: Optional Verbose Mode**
```python
# Configuration
class GameConfig(Config):
    def __init__(self):
        super().__init__()
        self.output_mode = "compact"  # or "verbose"
        self.include_losing_boards = False  # Skip board reveal for 0-win spins
        self.compress_positions = True
```

**Strategy D: Event Deduplication**
```python
# Before: Every spin has these events
{"type": "reveal", "board": [...], "gameType": "basegame"}
{"type": "setFinalWin", "amount": 0}

# After: Skip redundant events
# Only include "reveal" if needed for frontend
# "setFinalWin" is implicit from payoutMultiplier
```

**Tasks:**
- [ ] Create `OutputFormatter` class with modes: compact/verbose
- [ ] Implement compact symbol serialization
- [ ] Implement compact position serialization
- [ ] Add config option to skip losing board reveals
- [ ] Add config option to skip implicit events
- [ ] Update books writing logic
- [ ] Update books parsing/analysis tools
- [ ] Benchmark file size improvements
- [ ] Test RGS compatibility with new format

**Expected Savings:**
- **Current**: 248k lines for 10k simulations (~25 lines/sim)
- **Target**: 120k lines for 10k simulations (~12 lines/sim)
- **Reduction**: ~50% file size

#### 3.2 Optimize Event Generation
**Priority**: Medium
**Effort**: 2 days

**Tasks:**
- [ ] Audit all event generation code
- [ ] Remove redundant events
- [ ] Make verbose events configurable
- [ ] Add event filtering system
- [ ] Document which events are required vs optional

---

### Phase 4: Documentation & Testing (Week 6)

#### 4.1 Update Documentation
**Priority**: High
**Effort**: 3 days

**Tasks:**
- [ ] Update CLAUDE.md with new architecture
- [ ] Update README.md with refactor notes
- [ ] Rewrite architecture section in docs
- [ ] Create "Migrating from Old Structure" guide
- [ ] Update all code examples in docs
- [ ] Create visual architecture diagrams
- [ ] Record video walkthrough (optional)

#### 4.2 Expand Test Coverage
**Priority**: High
**Effort**: 4 days

**Tasks:**
- [ ] Add unit tests for all refactored modules
- [ ] Add integration tests for simulation pipeline
- [ ] Test old games still work after refactor
- [ ] Add regression tests (compare old vs new output)
- [ ] Test books format changes
- [ ] Add performance benchmarks
- [ ] Achieve >80% code coverage

#### 4.3 Create Migration Tools
**Priority**: Medium
**Effort**: 2 days

**Tasks:**
- [ ] Script to convert old game structure → new structure
- [ ] Script to validate game configurations
- [ ] Script to convert old books → new format (if needed)
- [ ] Checklist for game developers

---

### Phase 5: Polish & Optimization (Weeks 7-8)

#### 5.1 Performance Optimization
**Priority**: Medium
**Effort**: 3 days

**Tasks:**
- [ ] Profile simulation performance
- [ ] Optimize hot paths
- [ ] Reduce memory allocations
- [ ] Optimize books writing (streaming vs buffering)
- [ ] Benchmark before/after performance

#### 5.2 Developer Experience Improvements
**Priority**: Medium
**Effort**: 3 days

**Tasks:**
- [ ] Improve error messages
- [ ] Add configuration validation with helpful errors
- [ ] Create game development CLI tool
- [ ] Add interactive game creation wizard
- [ ] Improve Makefile with more commands

#### 5.3 Code Cleanup
**Priority**: Low
**Effort**: 2 days

**Tasks:**
- [ ] Remove commented-out code
- [ ] Remove unused imports
- [ ] Remove unused methods
- [ ] Consolidate duplicate logic
- [ ] Format all code with black
- [ ] Sort imports with isort

#### 5.4 Final Review
**Priority**: High
**Effort**: 2 days

**Tasks:**
- [ ] Code review of all changes
- [ ] Run full test suite
- [ ] Test all example games
- [ ] Update version number
- [ ] Create CHANGELOG.md
- [ ] Tag release

---

## Success Metrics

### Code Quality Metrics
- [ ] 100% type hint coverage
- [ ] >80% test coverage
- [ ] 0 mypy errors with strict mode
- [ ] 0 flake8 warnings
- [ ] All files have docstrings

### Performance Metrics
- [ ] Books file size reduced by 40-50%
- [ ] Simulation performance maintained or improved
- [ ] No regression in RTP calculations

### Developer Experience Metrics
- [ ] New game creation time reduced by 30%
- [ ] Onboarding time for new developers reduced
- [ ] Fewer "how do I..." questions

---

## Risk Mitigation

### Risk 1: Breaking Existing Games
**Mitigation:**
- Keep old structure running in parallel initially
- Extensive regression testing
- Gradual migration game-by-game
- Maintain backward compatibility layer if needed

### Risk 2: RGS Compatibility
**Mitigation:**
- Verify books format with RGS team before finalizing
- Add format version field to books
- Support both old and new formats during transition
- Test with actual RGS integration

### Risk 3: Performance Regression
**Mitigation:**
- Benchmark before/after every major change
- Profile hot paths
- Keep optimization as separate phase
- Revert changes that cause slowdowns

### Risk 4: Incomplete Migration
**Mitigation:**
- Work in feature branches
- Complete one phase before starting next
- Have rollback plan for each phase
- Document all changes thoroughly

---

## Phase Dependencies

```
Phase 1 (Foundation)
  ↓
Phase 2 (Code Quality) ← depends on Phase 1 standards
  ↓
Phase 3 (Output Optimization) ← can run parallel with Phase 2
  ↓
Phase 4 (Documentation & Testing) ← depends on Phase 2 & 3
  ↓
Phase 5 (Polish) ← depends on all previous phases
```

---

## Rollout Strategy

### Week 1-2: Foundation
- Set up tooling and standards
- No game changes yet
- Safe, reversible changes

### Week 3-4: Core Refactor
- Flatten inheritance
- Rename everything
- Test extensively
- Keep games working

### Week 5: Output Changes
- Implement compact format
- Make it configurable
- Default to old format initially
- Gradual switchover

### Week 6: Documentation
- Update all docs
- Create migration guides
- Record videos/demos

### Week 7-8: Polish
- Performance tuning
- Developer experience
- Final testing
- Release!

---

## Post-Refactor Maintenance

### Code Review Standards
- All PRs require type hints
- All new methods need docstrings
- New features need tests
- Follow naming conventions

### Continuous Improvement
- Regular performance profiling
- Periodic dependency updates
- Documentation updates
- Community feedback integration

---

## Appendix

### A. File Renames

| Old Path | New Path | Reason |
|----------|----------|--------|
| `src/state/state.py` | `src/state/base_game_state.py` | Clearer name |
| `game_override.py` | Merged into `game_state.py` | Simplify structure |
| `game_executables.py` | Merged into `game_state.py` | Simplify structure |
| `game_config.py` | No change | Already clear |
| `gamestate.py` | `game_state.py` | PEP 8 compliance |

### B. Class Renames

| Old Name | New Name | Reason |
|----------|----------|--------|
| `GeneralGameState` | `BaseGameState` | Clearer purpose |
| `GameStateOverride` | Removed | Merged into GameImplementation |
| `GameExecutables` | Removed | Merged into GameImplementation |
| `GameState` | `GameImplementation` | More descriptive |

### C. Method Renames

See Phase 2.1 for comprehensive list.

### D. Configuration Schema Changes

```python
# Old
self.basegame_type = "basegame"
self.freegame_type = "freegame"

# New
self.base_game_mode = GameMode.BASE
self.free_spin_mode = GameMode.FREE_SPIN
```

---

## Questions & Decisions

### Q1: Should we maintain backward compatibility?
**Decision**: Yes, for books format. Support both old and new formats for 1 version cycle.

### Q2: Should we keep Rust optimization as-is?
**Decision**: Yes. Don't touch Rust code unless necessary. It works well.

### Q3: Should we rename files to snake_case?
**Decision**: Yes. Follow PEP 8 everywhere for consistency.

### Q4: Should we use dataclasses for configs?
**Decision**: Consider in Phase 5. Would improve type safety but requires significant refactor.

### Q5: Should we support Python 3.11?
**Decision**: No. Require Python 3.12+ for modern type features.

---

## Notes

- All code changes will be done by Claude Code
- Human review required at end of each phase
- Extensive testing throughout
- Focus on incremental, safe improvements
- Preserve all functionality while improving structure

---

**Last Updated**: 2026-01-10
**Next Review**: After Phase 1 completion
