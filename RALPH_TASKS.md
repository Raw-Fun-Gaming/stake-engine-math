# Ralph Monitor Tasks - Remaining Refactor Work

**Created**: 2026-01-15
**Status**: Ready for autonomous execution
**Mode**: Ralph Monitor (autonomous)

---

## Instructions for Claude

Work through these tasks sequentially. After completing each task:
1. ✅ Mark the task as complete
2. ✅ Run relevant tests to verify changes
3. ✅ Commit changes with descriptive commit messages
4. ✅ Update this file with progress notes

**Important Guidelines:**
- Test after every significant change
- Commit frequently with clear messages
- If a task blocks progress, document the blocker and move to next task
- Preserve all existing functionality
- Follow coding standards from CONTRIBUTING.md
- Use the custom exceptions from src/exceptions.py where appropriate

---

## Phase 2: Code Quality Improvements (REMAINING)

### Phase 2.1: Comprehensive Renaming Pass ⏸️ DEFERRED
**Status**: Skipped (breaking changes - requires stakeholder approval)
**Note**: This phase involves extensive breaking changes. Will be handled separately after Phases 3-5 complete.

---

## Phase 3: Output Optimization

### 3.1 Compress Books Format
**Priority**: High
**Estimated Effort**: 4 days

#### Task 3.1.1: Create OutputFormatter Class
- [ ] Create `src/output/output_formatter.py`
- [ ] Implement `OutputFormatter` class with modes: `compact`, `verbose`
- [ ] Add configuration properties:
  - `output_mode`: "compact" or "verbose"
  - `include_losing_boards`: bool (skip board reveal for 0-win spins)
  - `compress_positions`: bool (use arrays instead of objects)
  - `compress_symbols`: bool (use strings instead of objects)
- [ ] Add comprehensive type hints and docstrings
- [ ] Add unit tests for OutputFormatter

**Acceptance Criteria:**
- OutputFormatter class exists with all configuration options
- Can switch between compact and verbose modes
- All methods have type hints and docstrings

#### Task 3.1.2: Implement Compact Symbol Serialization
- [ ] Update `src/calculations/symbol.py` to support compact serialization
- [ ] Add `Symbol.to_compact()` method: returns `"L5"` instead of `{"name": "L5"}`
- [ ] Add `Symbol.to_verbose()` method: returns current format
- [ ] Update `OutputFormatter` to use appropriate serialization method
- [ ] Add tests comparing compact vs verbose output sizes

**Format Change:**
```python
# Before (verbose)
{"name": "L5"}

# After (compact)
"L5"

# Savings: ~15 bytes per symbol × 25 symbols per board × 10k sims = 3.75MB
```

#### Task 3.1.3: Implement Compact Position Serialization
- [ ] Update position serialization in events
- [ ] Add `position_to_compact()` helper: returns `[0, 2]` instead of `{"reel": 0, "row": 2}`
- [ ] Add `position_to_verbose()` helper: returns current format
- [ ] Update all event construction to use OutputFormatter
- [ ] Add tests for position serialization

**Format Change:**
```python
# Before (verbose)
{"reel": 0, "row": 2}

# After (compact)
[0, 2]

# Savings: ~20 bytes per position
```

#### Task 3.1.4: Add Config Options to Skip Losing Boards
- [ ] Add `include_losing_boards` config option to `src/config/config.py`
- [ ] Update reveal event logic in `src/events/events.py`
- [ ] Skip board reveal events when:
  - `include_losing_boards = False`
  - Final win amount = 0
- [ ] Update all games to respect this config
- [ ] Add tests for losing board filtering

#### Task 3.1.5: Add Config Options to Skip Implicit Events
- [ ] Add `skip_implicit_events` config option
- [ ] Identify implicit events that can be skipped:
  - `setFinalWin` when amount = 0
  - `reveal` for losing spins (if include_losing_boards = False)
  - Other redundant events
- [ ] Update event emission logic
- [ ] Document which events are required vs optional
- [ ] Add tests for event filtering

#### Task 3.1.6: Update Books Writing Logic
- [ ] Update `src/write_data/books.py` to use OutputFormatter
- [ ] Add format version field to books: `"format_version": "2.0"`
- [ ] Support both old (verbose) and new (compact) formats
- [ ] Default to verbose for backward compatibility
- [ ] Add config option to enable compact format
- [ ] Test books writing with both formats

#### Task 3.1.7: Update Books Parsing/Analysis Tools
- [ ] Update `utils/game_analytics/` to support both formats
- [ ] Add auto-detection of books format version
- [ ] Ensure PAR sheet generation works with compact format
- [ ] Update `scripts/format_books_json.py` for compact format
- [ ] Test analysis tools with both old and new format books

#### Task 3.1.8: Benchmark File Size Improvements
- [ ] Run simulations with verbose format (baseline)
- [ ] Run same simulations with compact format
- [ ] Measure file size differences:
  - Symbol compression savings
  - Position compression savings
  - Event filtering savings
  - Total savings percentage
- [ ] Document results in benchmarking report
- [ ] Target: 40-50% file size reduction

**Expected Results:**
- Current: 248k lines for 10k simulations (~25 lines/sim)
- Target: 120k lines for 10k simulations (~12 lines/sim)
- Reduction: ~50% file size

#### Task 3.1.9: Test RGS Compatibility
- [ ] Run RGS verification tests with compact format
- [ ] Ensure frontend can parse compact format
- [ ] Add migration notes for RGS integration
- [ ] Test with actual game integration (if possible)
- [ ] Document any compatibility issues

**Deliverables:**
- [ ] OutputFormatter class with compact/verbose modes
- [ ] Compact symbol and position serialization
- [ ] Config options for output optimization
- [ ] Updated books writing and parsing
- [ ] Benchmark report showing 40-50% size reduction
- [ ] RGS compatibility verification

---

### 3.2 Optimize Event Generation
**Priority**: Medium
**Estimated Effort**: 2 days

#### Task 3.2.1: Audit All Event Generation Code
- [ ] Create inventory of all events generated across SDK
- [ ] List events by type and frequency
- [ ] Identify redundant events (emitted but never used)
- [ ] Identify optional events (only needed for debugging)
- [ ] Document findings in `EVENT_AUDIT.md`

#### Task 3.2.2: Remove Redundant Events
- [ ] Remove events that duplicate information
- [ ] Remove events that can be inferred from other data
- [ ] Update event emission code
- [ ] Ensure no breaking changes to RGS
- [ ] Test all games after removal

#### Task 3.2.3: Make Verbose Events Configurable
- [ ] Add `verbose_events` config option
- [ ] Classify events as:
  - Required (always emitted)
  - Standard (emitted by default)
  - Verbose (only emitted if verbose_events = True)
- [ ] Update event emission logic with conditionals
- [ ] Add tests for event filtering by verbosity level

#### Task 3.2.4: Add Event Filtering System
- [ ] Create `EventFilter` class in `src/events/event_filter.py`
- [ ] Add methods to filter events by:
  - Event type
  - Verbosity level
  - Win amount threshold
  - Custom predicates
- [ ] Integrate EventFilter with books writing
- [ ] Add configuration options for filtering
- [ ] Add tests for event filtering

#### Task 3.2.5: Document Required vs Optional Events
- [ ] Create `EVENTS.md` documentation
- [ ] List all event types with:
  - Description
  - When emitted
  - Required vs Optional
  - Data format
  - Usage notes
- [ ] Add examples for common event patterns
- [ ] Document event filtering configuration

**Deliverables:**
- [ ] EVENT_AUDIT.md with event inventory
- [ ] Redundant events removed
- [ ] EventFilter system implemented
- [ ] EVENTS.md documentation
- [ ] All games tested with optimized events

---

## Phase 4: Documentation & Testing

### 4.1 Update Documentation
**Priority**: High
**Estimated Effort**: 3 days

#### Task 4.1.1: Update CLAUDE.md with New Architecture
- [ ] Update inheritance hierarchy section (now 2 layers)
- [ ] Update file structure reference (new consolidated structure)
- [ ] Add section on OutputFormatter and compression
- [ ] Add section on event optimization
- [ ] Update code examples throughout
- [ ] Add Phase 3 improvements to overview

#### Task 4.1.2: Update README.md with Refactor Notes
- [ ] Add Phase 3 completion notes
- [ ] Document new compression features
- [ ] Add configuration examples for output optimization
- [ ] Update feature list with new capabilities
- [ ] Add benchmarking results

#### Task 4.1.3: Rewrite Architecture Section in Docs
- [ ] Update `docs/game-structure.md` with simplified architecture
- [ ] Add diagrams showing 2-layer inheritance
- [ ] Document BaseGameState → Board/Tumble → GameState flow
- [ ] Add examples of game implementation
- [ ] Update all outdated architecture references

#### Task 4.1.4: Create "Migrating from Old Structure" Guide
- [ ] Create `docs/migration-guide.md`
- [ ] Document changes from 6-layer to 2-layer structure
- [ ] Provide step-by-step migration instructions
- [ ] Add code comparison examples (before/after)
- [ ] Include troubleshooting section
- [ ] Add FAQ for common migration issues

#### Task 4.1.5: Update All Code Examples in Docs
- [ ] Audit all docs for code examples
- [ ] Update examples to use new structure
- [ ] Update examples to use OutputFormatter
- [ ] Update examples to use constants/enums
- [ ] Verify all examples run correctly
- [ ] Add missing examples where needed

#### Task 4.1.6: Create Visual Architecture Diagrams
- [ ] Create inheritance diagram (mermaid or ASCII art)
- [ ] Create simulation flow diagram
- [ ] Create event system diagram
- [ ] Create books generation flow diagram
- [ ] Add diagrams to documentation
- [ ] Export as images for README

**Deliverables:**
- [ ] Updated CLAUDE.md
- [ ] Updated README.md
- [ ] Rewritten architecture docs
- [ ] Migration guide
- [ ] Updated code examples
- [ ] Visual architecture diagrams

---

### 4.2 Expand Test Coverage
**Priority**: High
**Estimated Effort**: 4 days

#### Task 4.2.1: Add Unit Tests for All Refactored Modules
- [ ] Add tests for `src/state/base_game_state.py`
- [ ] Add tests for `src/output/output_formatter.py`
- [ ] Add tests for `src/events/event_filter.py`
- [ ] Add tests for compression features
- [ ] Add tests for event optimization
- [ ] Ensure all new code has >90% coverage

#### Task 4.2.2: Add Integration Tests for Simulation Pipeline
- [ ] Test full simulation flow: setup → run → books → analysis
- [ ] Test with different output modes (compact/verbose)
- [ ] Test with different event filtering options
- [ ] Test with compression enabled/disabled
- [ ] Test optimization pipeline
- [ ] Test PAR sheet generation

#### Task 4.2.3: Test Old Games Still Work After Refactor
- [ ] Run all 7 games with default settings
- [ ] Run all 7 games with compact output
- [ ] Run all 7 games with event filtering
- [ ] Compare output with previous versions
- [ ] Verify RTP calculations unchanged
- [ ] Verify PAR sheets match expectations

#### Task 4.2.4: Add Regression Tests
- [ ] Create baseline outputs for all games
- [ ] Add test that compares new output with baseline
- [ ] Test numeric equivalence (RTP, hit rates)
- [ ] Test format differences (compact vs verbose)
- [ ] Document acceptable deviations
- [ ] Add regression tests to CI

#### Task 4.2.5: Test Books Format Changes
- [ ] Test books with format_version field
- [ ] Test compact symbol serialization
- [ ] Test compact position serialization
- [ ] Test event filtering
- [ ] Test backward compatibility (old → new)
- [ ] Test forward compatibility (new → old if needed)

#### Task 4.2.6: Add Performance Benchmarks
- [ ] Create benchmarking suite in `tests/benchmarks/`
- [ ] Benchmark simulation speed (sims/second)
- [ ] Benchmark memory usage
- [ ] Benchmark books writing speed
- [ ] Benchmark file size vs compression level
- [ ] Document baseline and targets
- [ ] Add benchmark tests to CI

#### Task 4.2.7: Achieve >80% Code Coverage
- [ ] Run coverage analysis: `pytest --cov=src tests/`
- [ ] Identify uncovered code paths
- [ ] Add tests for uncovered areas
- [ ] Focus on critical paths first
- [ ] Document any intentionally untested code
- [ ] Generate coverage report

**Deliverables:**
- [ ] Unit tests for all new modules
- [ ] Integration tests for simulation pipeline
- [ ] Regression tests with baselines
- [ ] Performance benchmarks
- [ ] >80% code coverage
- [ ] Coverage report

---

### 4.3 Create Migration Tools
**Priority**: Medium
**Estimated Effort**: 2 days

#### Task 4.3.1: Script to Convert Old Game Structure → New Structure
- [ ] Create `scripts/migrate_game.py`
- [ ] Detect old game structure (4 files)
- [ ] Merge files into single gamestate.py
- [ ] Preserve all functionality
- [ ] Update imports and inheritance
- [ ] Add section headers
- [ ] Test with example game
- [ ] Add usage documentation

#### Task 4.3.2: Script to Validate Game Configurations
- [ ] Create `scripts/validate_config.py`
- [ ] Check required config attributes
- [ ] Validate reel strip files exist
- [ ] Validate paytable completeness
- [ ] Check for common configuration errors
- [ ] Provide helpful error messages
- [ ] Add to Makefile: `make validate-config GAME=<game>`

#### Task 4.3.3: Script to Convert Old Books → New Format
- [ ] Create `scripts/convert_books_format.py`
- [ ] Read old format books
- [ ] Convert to new compact format
- [ ] Add format_version field
- [ ] Preserve all data
- [ ] Verify conversion correctness
- [ ] Add usage documentation

#### Task 4.3.4: Checklist for Game Developers
- [ ] Create `GAME_DEVELOPMENT_CHECKLIST.md`
- [ ] List all steps to create new game
- [ ] List all steps to migrate existing game
- [ ] Add troubleshooting section
- [ ] Add code review checklist
- [ ] Add testing checklist
- [ ] Add deployment checklist

**Deliverables:**
- [ ] migrate_game.py script
- [ ] validate_config.py script
- [ ] convert_books_format.py script
- [ ] GAME_DEVELOPMENT_CHECKLIST.md
- [ ] All scripts tested and documented

---

## Phase 5: Polish & Optimization

### 5.1 Performance Optimization
**Priority**: Medium
**Estimated Effort**: 3 days

#### Task 5.1.1: Profile Simulation Performance
- [ ] Install profiling tools: `pip install py-spy`
- [ ] Profile simulation with py-spy: `py-spy record -o profile.svg -- python games/<game>/run.py`
- [ ] Identify hot paths (functions consuming most time)
- [ ] Identify memory bottlenecks
- [ ] Document findings in `PERFORMANCE_PROFILE.md`

#### Task 5.1.2: Optimize Hot Paths
- [ ] Optimize top 5 hottest functions
- [ ] Consider:
  - Caching repeated calculations
  - Reducing function calls
  - Optimizing loops
  - Vectorizing operations (numpy)
  - Reducing object allocations
- [ ] Benchmark before/after each optimization
- [ ] Ensure no correctness regressions

#### Task 5.1.3: Reduce Memory Allocations
- [ ] Identify unnecessary object creations
- [ ] Reuse objects where possible
- [ ] Use generators instead of lists where appropriate
- [ ] Optimize Symbol storage
- [ ] Optimize board representation
- [ ] Benchmark memory usage improvements

#### Task 5.1.4: Optimize Books Writing
- [ ] Compare streaming vs buffering approaches
- [ ] Implement buffered writing for better performance
- [ ] Add configurable buffer size
- [ ] Test with large simulations (100k+ spins)
- [ ] Benchmark writing speed improvements

#### Task 5.1.5: Benchmark Before/After Performance
- [ ] Run full benchmark suite on original code
- [ ] Run full benchmark suite on optimized code
- [ ] Compare:
  - Simulation speed (sims/second)
  - Memory usage (peak MB)
  - Books writing speed (MB/second)
  - Total runtime for 10k simulations
- [ ] Document improvements in PERFORMANCE_PROFILE.md

**Target Metrics:**
- [ ] Simulation speed: Maintain or improve
- [ ] Memory usage: Reduce by 10-20%
- [ ] Books writing: Improve by 20-30%
- [ ] No RTP calculation regressions

**Deliverables:**
- [ ] PERFORMANCE_PROFILE.md with profiling results
- [ ] Optimized hot paths
- [ ] Reduced memory allocations
- [ ] Optimized books writing
- [ ] Performance benchmark report

---

### 5.2 Developer Experience Improvements
**Priority**: Medium
**Estimated Effort**: 3 days

#### Task 5.2.1: Improve Error Messages
- [ ] Audit all error messages across SDK
- [ ] Make messages more helpful and actionable
- [ ] Add context to exceptions (file names, line numbers, config values)
- [ ] Add suggestions for fixes
- [ ] Test error messages for clarity
- [ ] Update documentation with common errors

#### Task 5.2.2: Add Configuration Validation with Helpful Errors
- [ ] Add `validate_config()` method to Config class
- [ ] Check required attributes
- [ ] Check attribute types
- [ ] Check value ranges
- [ ] Check file existence (reel strips)
- [ ] Use custom exceptions from src/exceptions.py
- [ ] Call validation in `__init__()`
- [ ] Add tests for validation

#### Task 5.2.3: Create Game Development CLI Tool
- [ ] Create `scripts/game_cli.py`
- [ ] Add commands:
  - `create`: Create new game from template
  - `validate`: Validate game configuration
  - `test`: Run game tests
  - `simulate`: Run simulation
  - `analyze`: Generate PAR sheet
  - `migrate`: Migrate old game structure
- [ ] Add to Makefile shortcuts
- [ ] Add CLI documentation

#### Task 5.2.4: Add Interactive Game Creation Wizard
- [ ] Create `scripts/create_game_wizard.py`
- [ ] Interactive prompts for:
  - Game ID and name
  - Win type (cluster/lines/ways/scatter)
  - Board dimensions
  - Number of symbols
  - RTP target
  - Special features
- [ ] Generate game files from template
- [ ] Create basic reel strips
- [ ] Add to game CLI as `create --interactive`

#### Task 5.2.5: Improve Makefile with More Commands
- [ ] Add `make validate GAME=<game>`: Validate configuration
- [ ] Add `make benchmark GAME=<game>`: Run benchmarks
- [ ] Add `make profile GAME=<game>`: Profile performance
- [ ] Add `make migrate GAME=<game>`: Migrate game structure
- [ ] Add `make create-game GAME=<game>`: Create new game
- [ ] Add `make coverage`: Run coverage report
- [ ] Update Makefile documentation

**Deliverables:**
- [ ] Improved error messages throughout SDK
- [ ] Configuration validation with helpful errors
- [ ] Game development CLI tool
- [ ] Interactive game creation wizard
- [ ] Enhanced Makefile
- [ ] CLI documentation

---

### 5.3 Code Cleanup
**Priority**: Low
**Estimated Effort**: 2 days

#### Task 5.3.1: Remove Commented-Out Code
- [ ] Search for commented code blocks across codebase
- [ ] Review each block:
  - Remove if no longer needed
  - Uncomment if should be active
  - Document if kept for reference
- [ ] Remove commented imports
- [ ] Remove commented debug statements

#### Task 5.3.2: Remove Unused Imports
- [ ] Run `autoflake --remove-all-unused-imports -r src/ games/`
- [ ] Review changes
- [ ] Apply fixes
- [ ] Run tests to verify no breakage
- [ ] Commit changes

#### Task 5.3.3: Remove Unused Methods
- [ ] Use coverage report to find unused code
- [ ] Identify unused methods (0% coverage)
- [ ] Verify methods are truly unused (check all games)
- [ ] Remove unused methods
- [ ] Document any intentionally unused code
- [ ] Run tests after removal

#### Task 5.3.4: Consolidate Duplicate Logic
- [ ] Search for duplicate code patterns
- [ ] Extract common logic into helper functions
- [ ] Update callers to use helpers
- [ ] Reduce code duplication
- [ ] Test after consolidation

#### Task 5.3.5: Format All Code with Black
- [ ] Run `black src/ games/ tests/ utils/`
- [ ] Review formatting changes
- [ ] Commit formatting changes separately
- [ ] Update pre-commit hooks to enforce black

#### Task 5.3.6: Sort Imports with Isort
- [ ] Run `isort src/ games/ tests/ utils/`
- [ ] Review import sorting changes
- [ ] Commit import sorting changes separately
- [ ] Update pre-commit hooks to enforce isort

**Deliverables:**
- [ ] Codebase free of commented code
- [ ] No unused imports
- [ ] No unused methods
- [ ] Reduced code duplication
- [ ] Consistently formatted code
- [ ] Sorted imports throughout

---

### 5.4 Final Review
**Priority**: High
**Estimated Effort**: 2 days

#### Task 5.4.1: Code Review of All Changes
- [ ] Review all commits since refactor start
- [ ] Check for:
  - Code quality issues
  - Missing documentation
  - Incomplete features
  - Security issues
  - Performance regressions
- [ ] Document review findings
- [ ] Fix any issues found

#### Task 5.4.2: Run Full Test Suite
- [ ] Run `make test`: Main test suite
- [ ] Run `pytest tests/`: All tests with verbose output
- [ ] Run tests for all 7 games: `make unit-test GAME=<game>`
- [ ] Run full simulations for all games: `make run GAME=<game>`
- [ ] Verify all tests pass
- [ ] Fix any failing tests

#### Task 5.4.3: Test All Example Games
- [ ] Test 0_0_lines: Run simulation, generate PAR sheet
- [ ] Test 0_0_cluster: Run simulation, generate PAR sheet
- [ ] Test 0_0_ways: Run simulation, generate PAR sheet
- [ ] Test 0_0_scatter: Run simulation, generate PAR sheet
- [ ] Test 0_0_expwilds: Run simulation, generate PAR sheet
- [ ] Test tower_treasures: Run simulation, generate PAR sheet
- [ ] Test template: Verify template works for new games
- [ ] Verify all games produce expected output
- [ ] Verify RTP calculations are correct

#### Task 5.4.4: Update Version Number
- [ ] Update version in `setup.py` (if exists)
- [ ] Update version in `__init__.py` (if exists)
- [ ] Update version in documentation
- [ ] Use semantic versioning (2.0.0 for major refactor)

#### Task 5.4.5: Create CHANGELOG.md
- [ ] Create comprehensive CHANGELOG.md
- [ ] Document all changes by phase:
  - Phase 1: Foundation
  - Phase 2: Code Quality
  - Phase 3: Output Optimization
  - Phase 4: Documentation & Testing
  - Phase 5: Polish & Optimization
- [ ] List breaking changes
- [ ] List new features
- [ ] List improvements
- [ ] List bug fixes
- [ ] Add migration guide reference

#### Task 5.4.6: Tag Release
- [ ] Commit CHANGELOG.md and version updates
- [ ] Create git tag: `git tag v2.0.0`
- [ ] Push tag: `git push origin v2.0.0`
- [ ] Create GitHub release with:
  - Release notes from CHANGELOG
  - Highlights of major improvements
  - Migration guide link
  - Breaking changes notice

**Deliverables:**
- [ ] Code review completed and issues fixed
- [ ] All tests passing
- [ ] All example games verified working
- [ ] Version updated to 2.0.0
- [ ] CHANGELOG.md created
- [ ] Release tagged and published

---

## Success Metrics (Final Verification)

### Code Quality Metrics
- [ ] 100% type hint coverage (or document exceptions)
- [ ] >80% test coverage achieved
- [ ] 0 mypy errors with strict mode (or document exceptions)
- [ ] 0 flake8 warnings
- [ ] All public methods/classes have docstrings

### Performance Metrics
- [ ] Books file size reduced by 40-50%
- [ ] Simulation performance maintained or improved
- [ ] Memory usage reduced by 10-20%
- [ ] No regression in RTP calculations

### Developer Experience Metrics
- [ ] New game creation time reduced (measure with template)
- [ ] Documentation comprehensive and up-to-date
- [ ] CLI tools available for common tasks
- [ ] Clear error messages throughout
- [ ] Migration tools available and tested

---

## Completion Checklist

- [ ] Phase 3.1: Compress Books Format
- [ ] Phase 3.2: Optimize Event Generation
- [ ] Phase 4.1: Update Documentation
- [ ] Phase 4.2: Expand Test Coverage
- [ ] Phase 4.3: Create Migration Tools
- [ ] Phase 5.1: Performance Optimization
- [ ] Phase 5.2: Developer Experience Improvements
- [ ] Phase 5.3: Code Cleanup
- [ ] Phase 5.4: Final Review
- [ ] All success metrics achieved
- [ ] CHANGELOG.md created
- [ ] Release tagged (v2.0.0)

---

## Notes and Progress Log

### Session Log
_Claude will update this section as work progresses_

#### 2026-01-15 - Ralph Monitor Session Started
- Created RALPH_TASKS.md with all remaining refactor work
- Ready to begin autonomous execution
- Starting with Phase 3.1: Compress Books Format

#### 2026-01-15 - Phase 3.1 Progress (PARTIAL COMPLETION)
**Tasks 3.1.1-3.1.5 Complete ✅**
- ✅ Created OutputFormatter class (280 lines, full-featured)
- ✅ Implemented compact symbol serialization ({"name": "L5"} → "L5")
- ✅ Implemented compact position serialization ({reel, row} → [reel, row])
- ✅ Added 21 unit tests for OutputFormatter, all passing
- ✅ Integrated with Config class (5 new config options)
- ✅ Updated reveal_event() to use OutputFormatter
- ✅ Updated trigger_free_spins_event() to format positions
- ✅ Verified 61% size savings on board formatting (simple test)
- ✅ Added format versioning to Book.to_json() ("2.0-compact" or "2.0-verbose")
- ✅ BaseGameState creates formatter from config in reset_book()
- ✅ All 31 tests passing after integration
- ✅ Committed to git (2 commits: 14edbfa, dd3da25)

**Achievements:**
- Core infrastructure complete and tested
- Backward compatible (defaults to verbose mode)
- Format version field automatically added to all books
- Games automatically inherit formatter through super().reset_book()

**Remaining Work in Phase 3.1:**
- [ ] Task 3.1.6: Update books writing logic to respect compression settings
- [ ] Task 3.1.7: Update books parsing/analysis tools for both formats
- [ ] Task 3.1.8: Run full game simulations and benchmark real file sizes
- [ ] Task 3.1.9: Test RGS compatibility with compact format

**Status:** Phase 3.1 is 60% complete. Core formatting infrastructure is done.
Remaining tasks are integration, testing, and validation.

---

**Last Updated**: 2026-01-15
**Next Update**: After each major task completion
