"""Main file for generating results for expanding wilds game.

This script uses run_config.toml for execution settings.
To customize settings, edit run_config.toml instead of modifying this file.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from game_config import GameConfig
from game_optimization import OptimizationSetup
from game_state import GameState

from optimization_program.run_script import OptimizationExecution
from src.config.run_config import RunConfig
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests


def main() -> None:
    """Run the game pipeline based on run_config.toml settings."""
    # Load configuration from TOML file
    run_config = RunConfig.from_toml("run_config.toml")

    # Validate configuration
    run_config.validate()

    # Print configuration summary
    print(run_config)
    print()

    # Initialize game components
    game_config = GameConfig()
    game_state = GameState(game_config)

    # Initialize optimization setup if needed
    if run_config.pipeline.run_optimization or run_config.pipeline.run_analysis:
        _ = OptimizationSetup(game_config)  # Initializes optimization parameters

    # Run simulation
    if run_config.pipeline.run_sims:
        print("Running simulations...")
        create_books(
            game_state,
            game_config,
            run_config.simulation.to_dict(),
            run_config.execution.batching_size,
            run_config.execution.num_threads,
            run_config.execution.compression,
            run_config.execution.profiling,
        )
        print("Simulations complete.\n")

    # Generate configuration files
    print("Generating configuration files...")
    generate_configs(game_state)
    print("Configuration files generated.\n")

    # Run optimization
    if run_config.pipeline.run_optimization:
        print("Running optimization...")
        OptimizationExecution().run_all_modes(
            game_config,
            run_config.target_modes,
            run_config.execution.rust_threads,
        )
        generate_configs(game_state)
        print("Optimization complete.\n")

    # Run analysis
    if run_config.pipeline.run_analysis:
        print("Running analysis...")
        create_stat_sheet(
            game_state,
            custom_keys=run_config.analysis.custom_keys,
        )
        print("Analysis complete.\n")

    # Run format checks
    if run_config.pipeline.run_format_checks:
        if not run_config.execution.compression:
            print(
                "Skipping format checks: compression is disabled. "
                "Format checks require compressed files."
            )
        else:
            print("Running RGS verification tests...")
            execute_all_tests(game_config)
            print("Format checks complete.\n")

    print("Pipeline execution finished successfully!")


if __name__ == "__main__":
    main()
