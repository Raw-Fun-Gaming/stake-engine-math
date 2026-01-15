#!/usr/bin/env python3
"""Benchmark event filtering impact on file sizes and event counts.

Runs simulations with different filtering configurations to measure:
- File size reduction
- Event count reduction
- Generation speed impact
- RTP accuracy (should be unchanged)
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

# Import game dynamically
import importlib.util

game_config_spec = importlib.util.spec_from_file_location(
    "game_config", "games/0_0_lines/game_config.py"
)
game_config_module = importlib.util.module_from_spec(game_config_spec)
game_config_spec.loader.exec_module(game_config_module)
GameConfig = game_config_module.GameConfig

gamestate_spec = importlib.util.spec_from_file_location(
    "gamestate", "games/0_0_lines/gamestate.py"
)
gamestate_module = importlib.util.module_from_spec(gamestate_spec)
gamestate_spec.loader.exec_module(gamestate_module)
GameState = gamestate_module.GameState

from src.output.output_formatter import OutputMode
from src.state.run_sims import create_books


def run_benchmark(
    config_name: str,
    skip_derived_wins: bool,
    skip_progress_updates: bool,
    verbose_event_level: str,
    num_sims: int = 500,
):
    """Run simulation with specific filtering configuration.

    Args:
        config_name: Descriptive name for this configuration
        skip_derived_wins: Whether to skip SET_WIN, SET_TOTAL_WIN
        skip_progress_updates: Whether to skip UPDATE_* events
        verbose_event_level: "minimal", "standard", or "full"
        num_sims: Number of simulations to run

    Returns:
        Dictionary with benchmark results
    """
    print(f"\n{'='*70}")
    print(f"Running benchmark: {config_name}")
    print(f"{'='*70}")
    print(f"  skip_derived_wins: {skip_derived_wins}")
    print(f"  skip_progress_updates: {skip_progress_updates}")
    print(f"  verbose_event_level: {verbose_event_level}")
    print(f"  simulations: {num_sims}")

    # Create config with filtering options
    config = GameConfig()
    config.output_mode = OutputMode.COMPACT  # Use compact for consistency
    config.skip_derived_wins = skip_derived_wins
    config.skip_progress_updates = skip_progress_updates
    config.verbose_event_level = verbose_event_level

    gamestate = GameState(config)

    # Run simulations
    num_sim_args = {"base": num_sims}

    start_time = time.time()
    create_books(
        gamestate,
        config,
        num_sim_args,
        batch_size=5000,
        threads=1,  # Single thread for consistent timing
        compress=False,  # No compression for raw size comparison
        profiling=False,
    )
    elapsed_time = time.time() - start_time

    # Get books file path
    books_file = f"games/{config.game_id}/library/books/books_base.json"

    # Measure file size
    file_size = os.path.getsize(books_file)

    # Count events and calculate RTP
    # Try loading as JSON array first
    try:
        with open(books_file, "r") as f:
            content = f.read()
            books_data = json.loads(content)
    except json.JSONDecodeError:
        # If that fails, try JSONL (newline-delimited)
        books_data = []
        with open(books_file, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        books_data.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue  # Skip malformed lines

    total_events = 0
    total_payout = 0
    event_type_counts = {}

    for book in books_data:
        total_events += len(book["events"])
        total_payout += book["payoutMultiplier"]

        # Count event types
        for event in book["events"]:
            event_type = event.get("type", "unknown")
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1

    avg_events_per_book = total_events / len(books_data)
    rtp = total_payout / (len(books_data) * 100)

    print(f"\n  Results:")
    print(f"    File size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    print(f"    Total events: {total_events:,}")
    print(f"    Avg events/book: {avg_events_per_book:.2f}")
    print(f"    RTP: {rtp:.6f}")
    print(f"    Generation time: {elapsed_time:.3f}s")
    print(f"\n  Event type counts:")
    for event_type, count in sorted(
        event_type_counts.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"    {event_type}: {count:,}")

    return {
        "config_name": config_name,
        "file_size": file_size,
        "total_events": total_events,
        "avg_events_per_book": avg_events_per_book,
        "rtp": rtp,
        "elapsed_time": elapsed_time,
        "event_type_counts": event_type_counts,
    }


def main():
    """Run all benchmark configurations."""
    print("=" * 70)
    print("EVENT FILTERING BENCHMARK")
    print("=" * 70)
    print("\nComparing file sizes and event counts with different filtering configs")
    print("Using compact output mode for all tests")

    num_sims = 500

    # Test configurations
    configs = [
        {
            "name": "Baseline (No Filtering)",
            "skip_derived_wins": False,
            "skip_progress_updates": False,
            "verbose_event_level": "full",
        },
        {
            "name": "Skip Derived Wins Only",
            "skip_derived_wins": True,
            "skip_progress_updates": False,
            "verbose_event_level": "full",
        },
        {
            "name": "Skip Progress Updates Only",
            "skip_derived_wins": False,
            "skip_progress_updates": True,
            "verbose_event_level": "full",
        },
        {
            "name": "Standard Verbosity",
            "skip_derived_wins": False,
            "skip_progress_updates": False,
            "verbose_event_level": "standard",
        },
        {
            "name": "Minimal Verbosity",
            "skip_derived_wins": False,
            "skip_progress_updates": False,
            "verbose_event_level": "minimal",
        },
        {
            "name": "All Optimizations",
            "skip_derived_wins": True,
            "skip_progress_updates": True,
            "verbose_event_level": "standard",
        },
    ]

    results = []
    for config in configs:
        result = run_benchmark(
            config["name"],
            config["skip_derived_wins"],
            config["skip_progress_updates"],
            config["verbose_event_level"],
            num_sims,
        )
        results.append(result)

    # Print comparison
    print(f"\n{'='*70}")
    print("COMPARISON SUMMARY")
    print(f"{'='*70}")

    baseline = results[0]
    baseline_size = baseline["file_size"]
    baseline_events = baseline["total_events"]

    print(f"\n{'Configuration':<30} {'File Size':<15} {'Savings':<12} {'Events':<12} {'Reduction':<12}")
    print("-" * 80)

    for result in results:
        size_savings = (baseline_size - result["file_size"]) / baseline_size * 100
        event_reduction = (
            (baseline_events - result["total_events"]) / baseline_events * 100
        )

        print(
            f"{result['config_name']:<30} "
            f"{result['file_size']/1024:>7.2f} KB    "
            f"{size_savings:>5.1f}%      "
            f"{result['total_events']:>7,}    "
            f"{event_reduction:>5.1f}%"
        )

    # RTP consistency check
    print(f"\n{'='*70}")
    print("RTP CONSISTENCY CHECK")
    print(f"{'='*70}")
    print(f"\n{'Configuration':<30} {'RTP':<12} {'Deviation':<12}")
    print("-" * 54)

    baseline_rtp = baseline["rtp"]
    for result in results:
        deviation = abs(result["rtp"] - baseline_rtp)
        print(
            f"{result['config_name']:<30} "
            f"{result['rtp']:.6f}    "
            f"{deviation:.6f}"
        )

    # Save results
    output_file = "event_filtering_benchmark_results.json"
    with open(output_file, "w") as f:
        json.dump(
            {
                "baseline": baseline,
                "configs": results,
                "summary": {
                    "num_simulations": num_sims,
                    "baseline_file_size": baseline_size,
                    "baseline_events": baseline_events,
                },
            },
            f,
            indent=2,
        )

    print(f"\n✅ Results saved to {output_file}")

    print(f"\n{'='*70}")
    print("BENCHMARK COMPLETE")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
