"""Utility functions for event construction."""

from __future__ import annotations

from typing import Any


def to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase.

    Args:
        snake_str: String in snake_case format (e.g., "base_game", "free_game")

    Returns:
        String in camelCase format (e.g., "baseGame", "freeGame")

    Examples:
        >>> to_camel_case("base_game")
        "baseGame"
        >>> to_camel_case("free_game")
        "freeGame"
        >>> to_camel_case("super_spin")
        "superSpin"
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def convert_symbol_json(symbol: Any, special_attributes: list[str]) -> dict[str, Any]:
    """Convert a symbol object to dictionary/JSON format.

    Args:
        symbol: Symbol object with name and optional special attributes
        special_attributes: List of attribute names to include if present

    Returns:
        Dictionary with symbol name and any special attributes
    """
    print_sym: dict[str, Any] = {"name": symbol.name}
    attrs = vars(symbol)
    for key, val in attrs.items():
        if key in special_attributes and symbol.get_attribute(key) is not False:
            print_sym[key] = val
    return print_sym
