# Performance Analysis & Optimization Opportunities

**Date**: 2026-01-15
**Game**: template_lines (representative baseline)
**Simulations**: 1,000
**Total Time**: 4.899s
**Speed**: 204.1 sims/second
**Per Sim**: 4.899ms

---

## Executive Summary

Based on profiling data, the top 5 hot paths consuming ~70% of execution time are:

1. **symbol.py:122(assign_paying_bool)** - 0.895s (18.3%)
2. **copy.py:119(deepcopy)** - 0.968s cumulative (19.8%)
3. **posix.read (multiprocessing)** - 0.896s (18.3%)
4. **set.add operations** - 0.238s (4.9%)
5. **JSON encoding** - 0.225s (4.6%)

**Key Finding**: Current performance of **204 sims/second** is reasonable, but there are several optimization opportunities that could yield 20-30% improvements.

---

## Hot Path Analysis

### 1. Symbol.assign_paying_bool() - **CRITICAL**

**Impact**: 0.895s (18.3% of total time)
**Calls**: 99,811 times
**Per Call**: 8.96µs

**Current Implementation** (estimated from profiling):
```python
def assign_paying_bool(self):
    # Likely checking paytable for each symbol
    # Called once per symbol during board creation
    pass
```

**Problem**: Called for EVERY symbol on EVERY board (99K+ times for 1K sims)

**Optimization Opportunities**:
1. **Cache paytable lookups** - Paytable doesn't change during simulation
2. **Pre-compute paying symbols** - Create a set of paying symbol names at initialization
3. **Lazy evaluation** - Only compute when needed (not always needed)

**Estimated Impact**: **30-50% reduction** (0.3-0.4s savings)

**Priority**: 🔴 **HIGH**

---

### 2. Deep Copy Operations - **CRITICAL**

**Impact**: 0.968s cumulative (19.8% of total time)
**Calls**: 639,109 deepcopy calls

**Current Usage**:
- Board state copying
- Symbol copying
- Configuration copying

**Problem**: Excessive deepcopy usage (639K+ calls for 1K sims)

**Optimization Opportunities**:
1. **Reduce deepcopy usage** - Use shallow copy where safe
2. **Object pooling** - Reuse symbol objects instead of copying
3. **Immutable data structures** - Eliminate need for copying
4. **Manual copying** - Write custom __copy__ methods for specific cases

**Estimated Impact**: **40-60% reduction** (0.4-0.6s savings)

**Priority**: 🔴 **HIGH**

---

### 3. Multiprocessing Overhead - **CANNOT OPTIMIZE**

**Impact**: 0.896s (18.3% of total time)
**Calls**: 520 posix.read calls

**Analysis**: This is overhead from multiprocessing communication (Manager, Pipes). It's necessary for parallel execution and cannot be optimized without changing architecture.

**Trade-off**: Multiprocessing provides speedup for large simulations (threads > 1), but adds overhead for small batches.

**Recommendation**: Accept this overhead. For production use with 10K+ sims and multiple threads, the benefit outweighs the cost.

**Priority**: ⚪ **ACCEPT**

---

### 4. Set Operations - **MEDIUM PRIORITY**

**Impact**: 0.238s (4.9% of total time)
**Calls**: 2,995,341 set.add operations

**Current Usage**:
- Tracking winning positions
- Tracking special symbols
- Building line/cluster sets

**Optimization Opportunities**:
1. **Use lists where order matters** - Lists are faster for small collections
2. **Pre-allocate sets** - Reduce resizing overhead
3. **Batch operations** - Fewer, larger set operations

**Estimated Impact**: **10-20% reduction** (0.02-0.05s savings)

**Priority**: 🟡 **MEDIUM**

---

### 5. JSON Encoding - **LOW PRIORITY**

**Impact**: 0.225s (4.6% of total time)
**Calls**: 5,522 encoder.iterencode calls

**Analysis**: JSON encoding is necessary for output. Already optimized in Phase 3.1 (OutputFormatter).

**Additional Opportunities**:
1. **Use orjson library** - 2-3x faster than standard json
2. **Batch writes** - Write larger chunks less frequently
3. **Binary format** - Use msgpack or pickle for internal use

**Estimated Impact**: **30-50% reduction** (0.07-0.11s savings) with orjson

**Priority**: 🟢 **LOW** (already optimized in Phase 3.1)

---

## Optimization Recommendations

### Phase 5.1A: Quick Wins (1-2 hours)

#### 1. Cache Symbol Paytable Lookups ✅
**File**: src/calculations/symbol.py:122

**Change**:
```python
class Symbol:
    _paying_symbols_cache = {}  # Class-level cache

    def assign_paying_bool(self):
        # Use cached lookup instead of recalculating
        cache_key = (self.name, self.config_hash)
        if cache_key in Symbol._paying_symbols_cache:
            self.paying = Symbol._paying_symbols_cache[cache_key]
        else:
            # Original logic
            self.paying = self._check_paytable()
            Symbol._paying_symbols_cache[cache_key] = self.paying
```

**Impact**: -0.3s to -0.4s (6-8% total speedup)

#### 2. Reduce Unnecessary Deepcopy ✅
**Files**: board.py, game_state.py

**Change**: Identify where deepcopy is used unnecessarily and replace with:
- Shallow copy for simple dicts/lists
- Reference passing for read-only data
- Custom __copy__ methods for specific classes

**Impact**: -0.4s to -0.6s (8-12% total speedup)

**Combined Quick Wins**: **14-20% faster** (4.9s → 4.0-4.2s)

---

### Phase 5.1B: Medium Effort (2-3 hours)

#### 3. Object Pooling for Symbols 🔄
**File**: src/calculations/symbol.py

**Change**: Reuse Symbol objects instead of creating new ones

```python
class SymbolPool:
    def __init__(self, config):
        # Pre-create symbol objects for each type
        self.pool = {name: [] for name in config.symbols}

    def get_symbol(self, name):
        if self.pool[name]:
            return self.pool[name].pop()
        return Symbol(name)

    def return_symbol(self, symbol):
        symbol.reset()
        self.pool[symbol.name].append(symbol)
```

**Impact**: -0.2s to -0.3s (4-6% total speedup)

#### 4. Optimize Set Operations 🔄
**Files**: lines.py, cluster.py, ways.py

**Change**: Use lists for small collections, pre-allocate sets

**Impact**: -0.05s to -0.1s (1-2% total speedup)

**Combined Medium Effort**: **5-8% faster** (additional speedup)

---

### Phase 5.1C: Major Refactor (4-6 hours) - **NOT RECOMMENDED**

#### 5. Replace Multiprocessing with asyncio
**Benefit**: Eliminate 0.9s overhead
**Cost**: Major architecture change, potential correctness issues
**Recommendation**: **SKIP** - Multiprocessing is appropriate for CPU-bound work

#### 6. Binary Output Format
**Benefit**: Faster serialization
**Cost**: Breaking change, RGS compatibility issues
**Recommendation**: **DEFER** - Phase 3 compression is sufficient

---

## Target Performance Goals

### Baseline (Current)
- **Speed**: 204.1 sims/second
- **Time for 1K sims**: 4.9s
- **Time for 10K sims**: 49s
- **Time for 100K sims**: 490s (8.2 minutes)

### After Phase 5.1A Optimizations (Quick Wins)
- **Speed**: 240-250 sims/second (+18-23%)
- **Time for 1K sims**: 4.0-4.2s
- **Time for 10K sims**: 40-42s
- **Time for 100K sims**: 400-420s (6.7-7.0 minutes)

### After Phase 5.1A+B Optimizations (All Optimizations)
- **Speed**: 255-270 sims/second (+25-32%)
- **Time for 1K sims**: 3.7-3.9s
- **Time for 10K sims**: 37-39s
- **Time for 100K sims**: 370-390s (6.2-6.5 minutes)

---

## Memory Analysis

**To Be Completed**: Run memory profiling with tracemalloc

**Expected Findings**:
- High memory usage from symbol objects (99K+ instances)
- Board storage overhead
- Event list accumulation

**Optimization Opportunities**:
- Symbol object pooling (reuse objects)
- Streaming output (write events incrementally)
- Reduce intermediate data structures

---

## Conclusions

### What to Optimize Now (Phase 5.1)
1. ✅ **Symbol paytable caching** - 6-8% speedup, low risk
2. ✅ **Reduce deepcopy usage** - 8-12% speedup, medium risk
3. 🔄 **Symbol object pooling** - 4-6% speedup, medium risk (optional)

### What NOT to Optimize
1. ❌ **Multiprocessing overhead** - Necessary architecture
2. ❌ **JSON encoding** - Already optimized in Phase 3.1
3. ❌ **Line/cluster algorithms** - Already efficient

### Expected Results
- **Total speedup**: 18-23% (Phase 5.1A) to 25-32% (Phase 5.1A+B)
- **10K simulations**: 49s → 37-42s
- **100K simulations**: 8.2min → 6.2-7.0min
- **Risk level**: Low to medium
- **Breaking changes**: None

---

## Next Steps

1. ✅ Complete profiling analysis (this document)
2. ⏭️ Implement Symbol paytable caching
3. ⏭️ Audit and reduce deepcopy usage
4. ⏭️ Run benchmarks to measure improvements
5. ⏭️ Update RALPH_TASKS.md with results
6. ⏭️ Document optimizations in code comments

---

**Status**: Analysis complete, ready for implementation
**Estimated Implementation Time**: 3-5 hours
**Expected Benefit**: 18-32% faster simulations
**Risk Assessment**: Low (non-breaking changes)
