"""Configuration loader for run.py execution settings.

This module provides a clean separation between game configuration (game_config.py)
and execution settings (run_config.toml). It loads and validates TOML configuration
files for simulation, optimization, and analysis pipelines.

Usage:
    from src.config.run_config import RunConfig

    # Load default config (run_config.toml in current directory)
    config = RunConfig.from_toml()

    # Load specific config file
    config = RunConfig.from_toml("custom_config.toml")

    # Or use environment variable (for Makefile integration)
    # CONFIG_FILE=custom.toml python run.py
    config = RunConfig.from_toml()  # Reads from CONFIG_FILE env var if set

    # Access settings
    print(config.execution.num_threads)
    print(config.simulation.base)
    print(config.pipeline.run_sims)
"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Python 3.11+ has built-in tomllib, fallback to tomli for older versions
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        raise ImportError(
            "Python < 3.11 requires 'tomli' package. Install with: pip install tomli"
        )


@dataclass
class ExecutionConfig:
    """Execution settings for simulation and optimization.

    Attributes:
        num_threads: Number of threads for parallel simulation
        rust_threads: Number of threads for Rust optimization
        batching_size: Number of simulations per batch
        compression: Enable zstd compression for output files
        profiling: Enable performance profiling
    """

    num_threads: int = 10
    rust_threads: int = 20
    batching_size: int = 50000
    compression: bool = False
    profiling: bool = False

    def __post_init__(self) -> None:
        """Validate execution settings."""
        if self.num_threads < 1:
            raise ValueError(f"num_threads must be >= 1, got {self.num_threads}")
        if self.rust_threads < 1:
            raise ValueError(f"rust_threads must be >= 1, got {self.rust_threads}")
        if self.batching_size < 1:
            raise ValueError(f"batching_size must be >= 1, got {self.batching_size}")


@dataclass
class SimulationConfig:
    """Simulation settings for different game modes.

    Attributes:
        base: Number of base game simulations
        bonus: Number of bonus game simulations (optional)
        free_spin: Number of free spin simulations (optional)
        super_spin: Number of super spin simulations (optional)
    """

    base: int = 10000
    bonus: int | None = None
    free_spin: int | None = None
    super_spin: int | None = None

    def to_dict(self) -> dict[str, int]:
        """Convert to dictionary format expected by create_books().

        Returns:
            Dictionary with mode names as keys and simulation counts as values.
            Only includes modes with non-None values.
        """
        result = {"base": self.base}
        if self.bonus is not None:
            result["bonus"] = self.bonus
        if self.free_spin is not None:
            result["free_spin"] = self.free_spin
        if self.super_spin is not None:
            result["super_spin"] = self.super_spin
        return result

    def __post_init__(self) -> None:
        """Validate simulation settings."""
        if self.base < 1:
            raise ValueError(f"base simulations must be >= 1, got {self.base}")
        if self.bonus is not None and self.bonus < 1:
            raise ValueError(f"bonus simulations must be >= 1, got {self.bonus}")
        if self.free_spin is not None and self.free_spin < 1:
            raise ValueError(
                f"free_spin simulations must be >= 1, got {self.free_spin}"
            )
        if self.super_spin is not None and self.super_spin < 1:
            raise ValueError(
                f"super_spin simulations must be >= 1, got {self.super_spin}"
            )


@dataclass
class PipelineConfig:
    """Pipeline execution flags.

    Attributes:
        run_sims: Run simulation to generate books files
        run_optimization: Run Rust optimization algorithm
        run_analysis: Run analytics and generate PAR sheets
        run_format_checks: Run RGS verification tests
    """

    run_sims: bool = True
    run_optimization: bool = False
    run_analysis: bool = False
    run_format_checks: bool = False


@dataclass
class AnalysisConfig:
    """Analysis settings for PAR sheet generation.

    Attributes:
        custom_keys: List of custom search keys for analysis
                     Example: [{"symbol": "scatter"}, {"event_type": "upgrade"}]
    """

    custom_keys: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class RunConfig:
    """Complete run configuration loaded from TOML file.

    Attributes:
        execution: Execution settings (threads, compression, etc.)
        simulation: Simulation counts per game mode
        pipeline: Pipeline execution flags
        analysis: Analysis settings
        target_modes: List of game modes to optimize (e.g., ["base", "bonus"])
    """

    execution: ExecutionConfig
    simulation: SimulationConfig
    pipeline: PipelineConfig
    analysis: AnalysisConfig
    target_modes: list[str] = field(default_factory=lambda: ["base"])

    @classmethod
    def from_toml(cls, path: str | Path | None = None) -> "RunConfig":
        """Load configuration from TOML file.

        Args:
            path: Path to TOML file. If None, checks CONFIG_FILE environment variable,
                  then falls back to "run_config.toml" in current directory.

        Returns:
            RunConfig instance with loaded settings.

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file has invalid format or values
            tomllib.TOMLDecodeError: If TOML syntax is invalid

        Example:
            >>> config = RunConfig.from_toml()  # Load ./run_config.toml
            >>> config = RunConfig.from_toml("custom_config.toml")
            >>> # Or use environment variable:
            >>> # CONFIG_FILE=custom.toml python run.py
            >>> print(config.execution.num_threads)
            10
        """
        if path is None:
            # Check for CONFIG_FILE environment variable first
            env_config = os.environ.get("CONFIG_FILE")
            if env_config:
                path = Path(env_config)
            else:
                path = Path("run_config.toml")
        else:
            path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {path}\n"
                f"Expected location: {path.absolute()}\n"
                "Create a run_config.toml file or specify a different path."
            )

        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML syntax in {path}: {e}") from e

        # Parse execution settings
        execution_data = data.get("execution", {})
        execution = ExecutionConfig(**execution_data)

        # Parse simulation settings
        simulation_data = data.get("simulation", {})
        simulation = SimulationConfig(**simulation_data)

        # Parse pipeline settings
        pipeline_data = data.get("pipeline", {})
        pipeline = PipelineConfig(**pipeline_data)

        # Parse analysis settings
        analysis_data = data.get("analysis", {})
        analysis = AnalysisConfig(**analysis_data)

        # Parse target modes
        target_modes = data.get("target_modes", ["base"])
        if not isinstance(target_modes, list):
            raise ValueError(f"target_modes must be a list, got {type(target_modes)}")

        return cls(
            execution=execution,
            simulation=simulation,
            pipeline=pipeline,
            analysis=analysis,
            target_modes=target_modes,
        )

    @classmethod
    def create_default(cls) -> "RunConfig":
        """Create configuration with default values.

        Returns:
            RunConfig instance with sensible defaults for development.

        Example:
            >>> config = RunConfig.create_default()
            >>> config.simulation.base
            10000
        """
        return cls(
            execution=ExecutionConfig(),
            simulation=SimulationConfig(),
            pipeline=PipelineConfig(),
            analysis=AnalysisConfig(),
            target_modes=["base"],
        )

    def validate(self) -> None:
        """Validate configuration consistency.

        Raises:
            ValueError: If configuration has inconsistent settings.

        Example:
            >>> config = RunConfig.from_toml()
            >>> config.validate()  # Raises if format_checks enabled but compression disabled
        """
        # Check if format checks require compression
        if self.pipeline.run_format_checks and not self.execution.compression:
            raise ValueError(
                "run_format_checks requires compression=true. "
                "Format checks validate compressed JSONL files. "
                "Either enable compression or disable format checks."
            )

        # Check if target_modes match simulation modes
        simulation_modes = set(self.simulation.to_dict().keys())
        for mode in self.target_modes:
            if mode not in simulation_modes:
                raise ValueError(
                    f"target_mode '{mode}' not found in simulation modes: {simulation_modes}"
                )

        # Check if optimization/analysis modes exist
        if self.pipeline.run_optimization or self.pipeline.run_analysis:
            if not any([self.simulation.base, self.simulation.bonus]):
                raise ValueError(
                    "Optimization/analysis requires at least one simulation mode configured"
                )

    def __str__(self) -> str:
        """Return human-readable configuration summary."""
        lines = [
            "Run Configuration:",
            f"  Execution:",
            f"    - Threads: {self.execution.num_threads} (Python), {self.execution.rust_threads} (Rust)",
            f"    - Batching: {self.execution.batching_size:,} sims/batch",
            f"    - Compression: {self.execution.compression}",
            f"    - Profiling: {self.execution.profiling}",
            f"  Simulation:",
        ]

        for mode, count in self.simulation.to_dict().items():
            lines.append(f"    - {mode}: {count:,} simulations")

        lines.extend(
            [
                f"  Pipeline:",
                f"    - Run simulations: {self.pipeline.run_sims}",
                f"    - Run optimization: {self.pipeline.run_optimization}",
                f"    - Run analysis: {self.pipeline.run_analysis}",
                f"    - Run format checks: {self.pipeline.run_format_checks}",
                f"  Target modes: {', '.join(self.target_modes)}",
            ]
        )

        if self.analysis.custom_keys:
            lines.append(
                f"  Analysis custom keys: {len(self.analysis.custom_keys)} defined"
            )

        return "\n".join(lines)
