#!/usr/bin/env python
"""Profile simulation performance and identify optimization opportunities.

This script runs performance profiling on game simulations to identify:
- Hot paths (functions consuming the most time)
- Memory bottlenecks
- Optimization opportunities

Usage:
    python scripts/profile_performance.py [--game GAME_NAME] [--sims NUM_SIMS]
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def profile_with_cprofile(game_name: str, num_sims: int) -> dict[str, Any]:
    """Profile game simulation using cProfile.

    Args:
        game_name: Name of the game to profile
        num_sims: Number of simulations to run

    Returns:
        Dictionary with profiling results
    """
    import cProfile
    import pstats

    # Create profiler
    profiler = cProfile.Profile()

    # Profile the simulation
    print(f"Profiling {num_sims} simulations of {game_name} with cProfile...")

    # Setup game path
    game_dir = project_root / "games" / game_name
    if str(game_dir) not in sys.path:
        sys.path.insert(0, str(game_dir))

    profiler.enable()
    start_time = time.time()

    # Run simulations (simplified - adjust based on game structure)
    try:
        from game_config import GameConfig
        from gamestate import GameState

        from src.state.run_sims import create_books

        config = GameConfig()
        num_sim_args = {"base": num_sims}
        game_state = GameState(config)
        create_books(
            game_state,
            config,
            num_sim_args,
            batch_size=100,
            threads=1,
            compress=False,
            profiling=False,
        )

    except Exception as e:
        print(f"Error running simulations: {e}")
        profiler.disable()
        return {"error": str(e)}

    end_time = time.time()
    profiler.disable()

    # Get statistics
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("cumulative")

    print("\n" + "=" * 80)
    print(f"PROFILING RESULTS - {game_name}")
    print("=" * 80)
    print(f"Total time: {end_time - start_time:.3f}s")
    print(f"Simulations: {num_sims}")
    print(f"Speed: {num_sims / (end_time - start_time):.1f} sims/second")
    print("=" * 80 + "\n")

    print("Top 30 functions by cumulative time:")
    print("-" * 80)
    stats.print_stats(30)

    print("\nTop 30 functions by total time:")
    print("-" * 80)
    stats.sort_stats("time")
    stats.print_stats(30)

    print("\nCallers of hot functions:")
    print("-" * 80)
    stats.sort_stats("cumulative")
    stats.print_callers(10)

    return {
        "total_time": end_time - start_time,
        "num_sims": num_sims,
        "sims_per_second": num_sims / (end_time - start_time),
        "stats": stats,
    }


def profile_memory(game_name: str, num_sims: int) -> dict[str, Any]:
    """Profile memory usage.

    Args:
        game_name: Name of the game to profile
        num_sims: Number of simulations to run

    Returns:
        Dictionary with memory profiling results
    """
    import tracemalloc

    print(f"\nProfiling memory usage for {num_sims} simulations of {game_name}...")

    # Setup game path
    game_dir = project_root / "games" / game_name
    if str(game_dir) not in sys.path:
        sys.path.insert(0, str(game_dir))

    # Start memory tracking
    tracemalloc.start()

    try:
        from game_config import GameConfig
        from gamestate import GameState

        from src.state.run_sims import create_books

        config = GameConfig()
        num_sim_args = {"base": num_sims}
        game_state = GameState(config)

        # Take snapshot before
        snapshot_before = tracemalloc.take_snapshot()

        # Run simulations
        create_books(
            game_state,
            config,
            num_sim_args,
            batch_size=100,
            threads=1,
            compress=False,
            profiling=False,
        )

        # Take snapshot after
        snapshot_after = tracemalloc.take_snapshot()

        # Compare snapshots
        top_stats = snapshot_after.compare_to(snapshot_before, "lineno")

        print("\n" + "=" * 80)
        print("TOP 10 MEMORY ALLOCATIONS")
        print("=" * 80)

        for stat in top_stats[:10]:
            print(stat)

        # Get current and peak memory
        current, peak = tracemalloc.get_traced_memory()

        print("\n" + "=" * 80)
        print("MEMORY SUMMARY")
        print("=" * 80)
        print(f"Current memory: {current / 1024 / 1024:.2f} MB")
        print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
        print(f"Memory per sim: {peak / num_sims / 1024:.2f} KB")
        print("=" * 80 + "\n")

        tracemalloc.stop()

        return {
            "current_mb": current / 1024 / 1024,
            "peak_mb": peak / 1024 / 1024,
            "per_sim_kb": peak / num_sims / 1024,
        }

    except Exception as e:
        tracemalloc.stop()
        print(f"Error during memory profiling: {e}")
        return {"error": str(e)}


def main() -> dict[str, Any]:
    """Run performance profiling and save results."""
    parser = argparse.ArgumentParser(description="Profile game simulation performance")
    parser.add_argument(
        "--game", default="0_0_lines", help="Game name to profile (default: 0_0_lines)"
    )
    parser.add_argument(
        "--sims", type=int, default=1000, help="Number of simulations (default: 1000)"
    )
    parser.add_argument(
        "--profile-type",
        choices=["cpu", "memory", "both"],
        default="both",
        help="Type of profiling to run (default: both)",
    )

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("PERFORMANCE PROFILING")
    print("=" * 80)
    print(f"Game: {args.game}")
    print(f"Simulations: {args.sims}")
    print(f"Profile Type: {args.profile_type}")
    print("=" * 80 + "\n")

    results = {}

    if args.profile_type in ["cpu", "both"]:
        results["cpu"] = profile_with_cprofile(args.game, args.sims)

    if args.profile_type in ["memory", "both"]:
        results["memory"] = profile_memory(args.game, args.sims)

    # Save results to file
    output_file = project_root / f"PERFORMANCE_PROFILE_{args.game}.md"

    with open(output_file, "w") as f:
        f.write(f"# Performance Profile: {args.game}\n\n")
        f.write(f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Simulations**: {args.sims}\n\n")

        if "cpu" in results and "error" not in results["cpu"]:
            f.write("## CPU Performance\n\n")
            f.write(f"- **Total Time**: {results['cpu']['total_time']:.3f}s\n")
            speed_val = results["cpu"]["sims_per_second"]
            f.write(f"- **Speed**: {speed_val:.1f} sims/second\n")
            per_sim_ms = results["cpu"]["total_time"] / args.sims * 1000
            f.write(f"- **Per Sim**: {per_sim_ms:.2f}ms\n\n")

        if "memory" in results and "error" not in results["memory"]:
            f.write("## Memory Usage\n\n")
            f.write(f"- **Peak Memory**: {results['memory']['peak_mb']:.2f} MB\n")
            f.write(f"- **Per Sim**: {results['memory']['per_sim_kb']:.2f} KB\n\n")

        f.write("\n## Recommendations\n\n")
        f.write("Based on profiling results, consider:\n")
        f.write("- Optimizing hot paths with high cumulative time\n")
        f.write("- Reducing memory allocations in frequently called functions\n")
        f.write("- Caching repeated calculations\n")
        f.write("- Using generators instead of lists where appropriate\n")

    print(f"\nProfile saved to: {output_file}")
    return results


if __name__ == "__main__":
    main()
