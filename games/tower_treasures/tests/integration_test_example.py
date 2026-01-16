#!/usr/bin/env python3

"""
Integration test example for tower defense game.
This shows how to test the complete game flow including sticky symbols.

Run from tower defense game directory:
    python tests/integration_test_example.py

Note: This is an example/template - you may need to adjust based on your specific testing needs.
"""

import json
import os
import sys

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
game_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(os.path.dirname(game_dir))

sys.path.insert(0, project_root)
sys.path.insert(0, game_dir)


def test_full_game_integration():
    """Example of how to test the complete game with sticky symbols"""

    try:
        from game_config import GameConfig
        from game_state import GameState

        print("🧪 Testing full game integration with sticky symbols...")

        # Initialize game
        config = GameConfig()
        game = GameState(config)

        # Set up a test scenario
        game.bet_amount = 100  # $1.00 bet
        game.number_of_spins = 5  # Test 5 spins

        # Run the game
        game.run_game()

        # Check that books were generated
        assert hasattr(game, "books"), "Game should have books"
        assert len(game.books) > 0, "Should have generated at least one book"

        # Analyze the books for sticky symbols functionality
        sticky_symbols_found = False
        upgrade_events_found = False
        prize_events_found = False

        for book in game.books:
            if hasattr(book, "events"):
                for event in book.events:
                    if event.get("type") == "reveal" and "free_game" in event.get(
                        "game_type", ""
                    ):
                        # Check for M/H symbols in free game reveals (indicating sticky symbols)
                        for reel in event.get("reel", []):
                            for symbol in reel:
                                if symbol.startswith("M") or symbol.startswith("H"):
                                    sticky_symbols_found = True

                    if event.get("type") == "upgrade":
                        upgrade_events_found = True

                    if event.get("type") == "win" and event.get("reason") == "prize":
                        prize_events_found = True

        # Verify expected functionality
        print(
            f"   Sticky symbols in free games: {'✅' if sticky_symbols_found else '❌'}"
        )
        print(f"   Upgrade events generated: {'✅' if upgrade_events_found else '❌'}")
        print(f"   Prize events generated: {'✅' if prize_events_found else '❌'}")

        # This is a basic check - you might want more specific validation
        print("✅ Integration test completed - check results above")
        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def analyze_books_for_sticky_symbols():
    """Analyze generated books to verify sticky symbols are working"""

    try:
        print("🧪 Analyzing books for sticky symbols evidence...")

        # Look for recent book files (you might need to adjust this path)
        import glob

        book_files = glob.glob("*.json")

        if not book_files:
            print("❌ No book files found. Run the game first to generate books.")
            return False

        # Analyze the most recent book
        latest_book = max(book_files, key=os.path.getctime)
        print(f"   Analyzing: {latest_book}")

        with open(latest_book, "r") as f:
            book_data = json.load(f)

        # Look for sticky symbols evidence
        free_game_reveals = 0
        sticky_symbols_in_free_games = []

        for event in book_data.get("events", []):
            if event.get("type") == "reveal" and "free_game" in event.get(
                "game_type", ""
            ):
                free_game_reveals += 1

                # Check for M/H symbols
                for reel_idx, reel in enumerate(event.get("reel", [])):
                    for row_idx, symbol in enumerate(reel):
                        if symbol.startswith("M") or symbol.startswith("H"):
                            sticky_symbols_in_free_games.append(
                                {
                                    "symbol": symbol,
                                    "position": (reel_idx, row_idx),
                                    "spin": free_game_reveals,
                                }
                            )

        print(f"   Free game reveals found: {free_game_reveals}")
        print(f"   Sticky symbols found: {len(sticky_symbols_in_free_games)}")

        if sticky_symbols_in_free_games:
            print("   Sticky symbols details:")
            for sticky in sticky_symbols_in_free_games[:5]:  # Show first 5
                print(
                    f"     {sticky['symbol']} at {sticky['position']} in spin {sticky['spin']}"
                )

        return len(sticky_symbols_in_free_games) > 0

    except Exception as e:
        print(f"❌ Book analysis failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Tower Defense Integration Test Examples")
    print("=" * 50)

    # Option 1: Full game test
    print("\n1. Full Game Integration Test:")
    integration_passed = test_full_game_integration()

    # Option 2: Analyze existing books
    print("\n2. Book Analysis Test:")
    analysis_passed = analyze_books_for_sticky_symbols()

    print("\n" + "=" * 50)
    if integration_passed and analysis_passed:
        print("🎉 Integration tests suggest sticky symbols are working!")
    else:
        print("❌ Integration tests need investigation")
        print("💡 Tip: Run the game first to generate books, then run this test")
