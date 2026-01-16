#!/usr/bin/env python3
"""
Analyze the win distribution from the books JSON file.

This script analyzes a books JSON file to provide:
1. Total number of spins analyzed
2. Number of spins that resulted in wins
3. Number of spins with wins excluding those that trigger free spins
4. Distribution of individual wins by symbol

Usage:
    python analyze_wins.py [filename]

If no filename is provided, it defaults to 'library/books/books_base.json'

Example:
    python analyze_wins.py my_books.json
"""

import json
import sys
from collections import defaultdict


def analyze_wins(filename):
    """Analyze win distribution from a books file."""
    import os

    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        print("Please provide a valid books JSON file path.")
        return None, 0, 0, 0, 0

    symbol_wins = defaultdict(int)
    total_wins = 0
    total_spins = 0
    spins_with_wins = 0
    spins_with_wins_no_fs = 0  # Spins with wins excluding free spin triggers

    with open(filename, "r") as f:
        content = f.read()

    try:
        # Try to parse as a proper JSON array first
        games = json.loads(content)
        if isinstance(games, list):
            # It's a proper JSON array, process directly
            for game in games:
                total_spins += 1
                has_win = False
                has_free_spin_trigger = False

                if "events" in game:
                    # First pass: check for free_spin triggers
                    for event in game["events"]:
                        if event.get("type") == "trigger_free_spins":
                            has_free_spin_trigger = True
                            break

                    # Second pass: analyze wins
                    for event in game["events"]:
                        if event.get("type") == "win" and "details" in event:
                            has_win = True
                            for win in event["details"]:
                                symbol = win.get("symbol", "unknown")
                                cluster_size = win.get("count", 0)
                                win_amount = win.get("amount", 0)

                                symbol_wins[symbol] += 1
                                total_wins += 1

                                # Show details for L4 and L5 wins
                                if symbol in ["L4", "L5"]:
                                    print(
                                        f"Found {symbol} win: cluster size {cluster_size}, win amount {win_amount}"
                                    )

                # Count spins with wins
                if has_win:
                    spins_with_wins += 1
                    if not has_free_spin_trigger:
                        spins_with_wins_no_fs += 1
        else:
            print("Error: JSON content is not an array")
            return None, 0, 0, 0, 0

    except json.JSONDecodeError:
        # Fall back to the old method for concatenated JSON objects
        print("Attempting to parse as concatenated JSON objects...")

        # Remove the bracket wrapping and split by '][' to get individual JSON objects
        content = content.strip()
        if content.startswith("[") and content.endswith("]"):
            content = content[1:-1]  # Remove outer brackets

        # Split by '][' to separate JSON objects
        json_objects = content.split("][")

        for i, json_str in enumerate(json_objects):
            # Add back the brackets if needed
            if not json_str.startswith("["):
                json_str = "[" + json_str
            if not json_str.endswith("]"):
                json_str = json_str + "]"

            try:
                games = json.loads(json_str)

                for game in games:
                    total_spins += 1
                    has_win = False
                    has_free_spin_trigger = False

                    if "events" in game:
                        # First pass: check for free_spin triggers
                        for event in game["events"]:
                            if event.get("type") == "trigger_free_spins":
                                has_free_spin_trigger = True
                                break

                        # Second pass: analyze wins
                        for event in game["events"]:
                            if event.get("type") == "win" and "details" in event:
                                has_win = True
                                for win in event["details"]:
                                    symbol = win.get("symbol", "unknown")
                                    cluster_size = win.get("count", 0)
                                    win_amount = win.get("amount", 0)

                                    symbol_wins[symbol] += 1
                                    total_wins += 1

                                    # Show details for L4 and L5 wins
                                    if symbol in ["L4", "L5"]:
                                        print(
                                            f"Found {symbol} win: cluster size {cluster_size}, win amount {win_amount}"
                                        )

                    # Count spins with wins
                    if has_win:
                        spins_with_wins += 1
                        if not has_free_spin_trigger:
                            spins_with_wins_no_fs += 1

            except json.JSONDecodeError as e:
                print(f"Error parsing JSON object {i}: {e}")
                continue

    print(f"\nWin Distribution Analysis:")
    print(f"Total spins analyzed: {total_spins}")
    print(
        f"Spins with wins: {spins_with_wins} ({(spins_with_wins/total_spins*100):.1f}%)"
    )
    print(
        f"Spins with wins (excluding free spin triggers): {spins_with_wins_no_fs} ({(spins_with_wins_no_fs/total_spins*100):.1f}%)"
    )
    print(f"Total individual wins found: {total_wins}")
    print(f"Symbol breakdown:")

    for symbol in sorted(symbol_wins.keys()):
        count = symbol_wins[symbol]
        percentage = (count / total_wins * 100) if total_wins > 0 else 0
        print(f"  {symbol}: {count} wins ({percentage:.1f}%)")

    return symbol_wins, total_wins, total_spins, spins_with_wins, spins_with_wins_no_fs


if __name__ == "__main__":
    filename = "library/books/books_base.json"
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    print(f"Analyzing {filename}...")
    analyze_wins(filename)
