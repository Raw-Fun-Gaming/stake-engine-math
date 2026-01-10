"""Bet mode configuration for different game modes.

This module defines the BetMode class which represents different betting
configurations (base game, bonus modes, buy bonus, etc.) with their own
RTP targets, costs, and distribution settings.
"""

from __future__ import annotations

from typing import Any

from src.config.constants import *  # noqa: F403


class BetMode:
    """Configuration for a single bet mode (base game, bonus, etc.).

    Encapsulates all settings for a specific game mode including:
    - Cost and RTP targets
    - Win cap limits
    - Feature/buy-bonus flags
    - Distribution configurations
    - Force key tracking for optimization

    Attributes:
        _name: Mode identifier (e.g., "base", "bonus")
        _cost: Bet cost multiplier
        _wincap: Maximum win cap for this mode
        _auto_close_disabled: Whether to disable auto-close on 0x wins
        _is_feature: Whether this is a feature mode
        _is_buybonus: Whether this is a buy-bonus mode
        _distributions: List of distribution configurations
        _rtp: Target RTP for this mode
        _force_keys: Keys tracked for force/optimization

    Example:
        >>> base_mode = BetMode(
        ...     name="base",
        ...     cost=1.0,
        ...     rtp=0.97,
        ...     max_win=10000.0,
        ...     auto_close_disabled=False,
        ...     is_feature=False,
        ...     is_buybonus=False,
        ...     distributions=[dist1, dist2]
        ... )
    """

    def __init__(
        self,
        name: str,
        cost: float,
        rtp: float,
        max_win: float,
        auto_close_disabled: bool,
        is_feature: bool,
        is_buybonus: bool,
        distributions: list[Any],
    ) -> None:
        """Initialize bet mode with configuration parameters.

        Args:
            name: Mode identifier (e.g., "base", "bonus")
            cost: Bet cost multiplier
            rtp: Target RTP (must be < 1.0)
            max_win: Maximum win cap for this mode
            auto_close_disabled: Whether to disable auto-close on 0x wins
            is_feature: Whether this is a feature mode
            is_buybonus: Whether this is a buy-bonus mode
            distributions: List of distribution configurations
        """
        self._name: str = name
        self._cost: float = cost
        self._wincap: float = max_win
        self._auto_close_disabled: bool = auto_close_disabled
        self._is_feature: bool = is_feature
        self._is_buybonus: bool = is_buybonus
        self._distributions: list[Any] = distributions
        self.set_rtp(rtp)
        self.set_force_keys()

    def __repr__(self) -> str:
        """Return string representation of BetMode."""
        return (
            f"BetMode(name={self._name},"
            f"cost={self._cost}, max_win={self._wincap}, rtp={self._rtp}, auto_close_disabled={self._auto_close_disabled} "
            f"is_feature={self._is_feature}, is_buybonus={self._is_buybonus} "
        )

    def set_rtp(self, rtp: float) -> None:
        """Set mode RTP target.

        Args:
            rtp: Return to player percentage (must be < 1.0)

        Raises:
            Warning: If RTP is >= 1.0
        """
        if rtp >= 1.0:
            raise Warning(f"Return To Player is >=1.0!: {rtp}")
        self._rtp: float = rtp

    def set_force_keys(self) -> None:
        """Initialize empty force keys list for optimization tracking."""
        self._force_keys: list[str] = []

    def add_force_key(self, force_key: str) -> None:
        """Add a new force key for optimization tracking.

        Args:
            force_key: Key identifier to track
        """
        self._force_keys.append(str(force_key))

    def lock_force_keys(self) -> None:
        """Finalize force keys at end of betmode simulation.

        Converts the force keys list to a sorted immutable tuple.
        """
        self._force_keys = tuple(sorted(self._force_keys))  # type: ignore[assignment]

    def get_force_keys(self) -> list[str] | tuple[str, ...]:
        """Return current force keys.

        Returns:
            List or tuple of force key strings
        """
        return self._force_keys

    def get_name(self) -> str:
        """Return mode name identifier.

        Returns:
            Mode name (e.g., "base", "bonus")
        """
        return self._name

    def get_cost(self) -> float:
        """Return mode bet cost multiplier.

        Returns:
            Cost multiplier for this mode
        """
        return self._cost

    def get_feature(self) -> bool:
        """Return whether this is a feature mode.

        Returns:
            True if this is a feature mode
        """
        return self._is_feature

    def get_auto_close_disabled(self) -> bool:
        """Return auto-close setting for this mode.

        Auto-close tells RGS if a bet should be automatically closed
        (by calling /endround API) if the payout multiplier is 0x.
        Calling /endround prevents players from resuming interrupted bets.

        Returns:
            True if auto-close is disabled
        """
        return self._auto_close_disabled

    def get_buybonus(self) -> bool:
        """Return whether this is a buy-bonus mode.

        Returns:
            True if this mode is a buy-bonus
        """
        return self._is_buybonus

    def get_wincap(self) -> float:
        """Return maximum win amount for this mode.

        Returns:
            Win cap value
        """
        return self._wincap

    def get_rtp(self) -> float:
        """Return total BetMode RTP target.

        Returns:
            RTP value (e.g., 0.97 for 97%)
        """
        return self._rtp

    def get_distributions(self) -> list[Any]:
        """Return list of all BetMode distribution configurations.

        Returns:
            List of distribution objects
        """
        return self._distributions

    def get_distribution_conditions(self, targetCriteria: str) -> dict[str, Any]:
        """Return conditions for a specific distribution criteria.

        Args:
            targetCriteria: Criteria identifier to search for

        Returns:
            Dictionary of conditions for the target criteria

        Raises:
            RuntimeError: If target criteria not found in distributions
        """
        for d in self.get_distributions():
            if d._criteria == targetCriteria:
                return d._conditions  # type: ignore[no-any-return]
        raise RuntimeError(f"target criteria: {targetCriteria} not found in betmode-distributions.")
