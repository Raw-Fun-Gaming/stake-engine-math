# Instructions for Creating GitHub Release

Go to: https://github.com/Raw-Fun-Gaming/stake-engine-math/releases/new

## Fill in the form:

### 1. Tag Selection
- **Choose a tag:** Select `v2.0.0` from dropdown (or type `v2.0.0`)
- **Target:** `main` branch

### 2. Release Title
```
v2.0.0 - Major Architecture Refactoring
```

### 3. Release Description
Copy the content below:

---

## 🎯 Release Highlights

This is a major refactoring release representing a complete architecture overhaul of the Stake Engine Math SDK, improving maintainability, performance, and developer experience while maintaining full backward compatibility.

**Key Improvements:**
- 🏗️ **67% reduction** in inheritance complexity (6 → 2 layers)
- 📄 **75% reduction** in game file count (4 → 1 file per game)
- ⚡ **35-47% simulation performance improvement** via paytable caching
- 📦 **35-40% output file size reduction** via compression + event filtering
- 🏢 Modern project structure with `build/` directory
- ✅ Full PEP 8 compliance across entire codebase
- 📚 Comprehensive documentation updates
- 🧪 **54 tests passing**, production ready

---

## 🚀 What's New

### Architecture Simplification
- New unified `BaseGameState` class merging multiple base classes
- Simplified inheritance: `GameState → Board/Tumble → BaseGameState`
- Single file per game (`gamestate.py`) vs old 4-file structure
- Clear section organization for game logic

### Performance Optimization
- **Paytable caching:** 35-47% speedup (204 → 287 sims/sec average)
- **Output compression:** 35-40% file size reduction
- **13% faster generation** with compact mode
- Zero accuracy regression

### Developer Experience
- Config validation CLI tool
- Enhanced Makefile commands (validate, profile, benchmark)
- Improved error messages with actionable suggestions
- Performance profiling tools

### Project Structure
- **`library/` → `build/`** directory for modern conventions
- Clear separation: `reels/` (source) vs `build/` (generated)
- PEP 8 compliant naming (`UPPER_SNAKE_CASE`)
- Standardized reel file naming

### Documentation
- Complete rewrite of architecture docs
- Updated all paths to use `build/`
- Migration guides included
- Comprehensive reference documentation

---

## 📦 Installation

### New Installation
```bash
git clone https://github.com/Raw-Fun-Gaming/stake-engine-math.git
cd stake-engine-math
git checkout v2.0.0
make setup
source env/bin/activate
make run GAME=template_cluster
```

### Upgrading from v1.x
```bash
git pull origin main
git checkout v2.0.0
make setup
source env/bin/activate
# Your existing games continue to work!
```

---

## 🔄 Migration

All changes are **backward compatible**. Games using the old structure continue to work.

For new games:
1. Use single `gamestate.py` file instead of multiple files
2. Output goes to `build/` directory automatically
3. Use `UPPER_SNAKE_CASE` for constants
4. Enable output optimization in `game_config.py` (optional)

---

## 📚 Documentation

- [README.md](https://github.com/Raw-Fun-Gaming/stake-engine-math/blob/v2.0.0/README.md) - Quick start
- [CLAUDE.md](https://github.com/Raw-Fun-Gaming/stake-engine-math/blob/v2.0.0/CLAUDE.md) - Complete reference
- [docs/game-structure.md](https://github.com/Raw-Fun-Gaming/stake-engine-math/blob/v2.0.0/docs/game-structure.md) - Architecture guide
- [docs/running-games.md](https://github.com/Raw-Fun-Gaming/stake-engine-math/blob/v2.0.0/docs/running-games.md) - Running simulations
- [CHANGELOG.md](https://github.com/Raw-Fun-Gaming/stake-engine-math/blob/v2.0.0/CHANGELOG.md) - Full changelog

---

## 🎓 Quick Example

```bash
# Copy template
cp -r games/template/ games/my_new_game/

# Edit configuration
# games/my_new_game/game_config.py

# Implement game logic
# games/my_new_game/gamestate.py

# Run simulation
make run GAME=my_new_game
```

Output automatically goes to `games/my_new_game/build/books/`

---

## 🧪 Testing

- 54 tests passing (21 OutputFormatter + 15 EventFilter + 8 integration + 10 win calculations)
- Full RGS verification passing
- Production ready and deployed

---

**Full Release Notes:** See [RELEASE_NOTES_v2.0.0.md](https://github.com/Raw-Fun-Gaming/stake-engine-math/blob/v2.0.0/RELEASE_NOTES_v2.0.0.md) and [CHANGELOG.md](https://github.com/Raw-Fun-Gaming/stake-engine-math/blob/v2.0.0/CHANGELOG.md)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---

### 4. Options
- ✅ Check "Set as the latest release"
- ✅ Check "Create a discussion for this release" (optional)

### 5. Click "Publish release"
