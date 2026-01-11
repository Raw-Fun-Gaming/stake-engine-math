"""Symbol classes and storage for game board management.

This module handles symbol instantiation, storage, and attribute management
for slot game simulations. Symbols can have special properties (wild, scatter,
multiplier) and paytable information.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from src.config.config import Config


class SymbolStorage:
    """Storage and factory for symbol instances.

    Maintains a cache of Symbol objects to avoid repeated instantiation.
    Creates symbols from configuration and provides lookup by name.

    Attributes:
        config: Game configuration with paytable and special symbols
        symbols: Cache of instantiated Symbol objects by name
    """

    def __init__(self, config: Config, all_symbols: list[str]) -> None:
        """Initialize symbol storage with configuration.

        Args:
            config: Game configuration containing paytable and special symbols
            all_symbols: List of all valid symbol names in the game
        """
        self.config: Config = config
        self.symbols: dict[str, Symbol] = {}
        for symbol in all_symbols:
            self.symbols[symbol] = Symbol(self.config, symbol)

    def create_symbol_state(self, symbol_name: str) -> Symbol:
        """Create new symbol instance (without caching).

        Args:
            symbol_name: Name of the symbol to create

        Returns:
            New Symbol instance
        """
        return Symbol(self.config, symbol_name)

    def get_symbol(self, name: str) -> Symbol:
        """Retrieve or create symbol by name.

        Args:
            name: Symbol name to retrieve

        Returns:
            Symbol instance (cached or newly created)
        """
        if name not in self.symbols:
            self.symbols[name] = Symbol(self.config, name)
        return self.symbols[name]


class Symbol:
    """Symbol instance with properties and special functions.

    Represents a single symbol on the game board with:
    - Name identifier
    - Special properties (wild, scatter, multiplier, etc.)
    - Paytable information
    - Registered special functions to execute

    Attributes:
        name: Symbol identifier (e.g., "H1", "scatter", "wild")
        special: Whether symbol has any special properties
        is_paying: Whether symbol pays according to paytable
        paytable: List of pay values for different counts
        special_functions: List of functions to execute for this symbol
        explode: Whether symbol should explode/cascade (set during gameplay)

    Note:
        Special properties are dynamically added as attributes based on
        config.special_symbols (e.g., self.wild = True, self.scatter = True)
    """

    def __init__(self, config: Config, name: str) -> None:
        """Initialize symbol with name and configuration.

        Args:
            config: Game configuration with special_symbols and paytable
            name: Symbol identifier
        """
        self.name: str = name
        self.special_functions: list[Callable[[Symbol], None]] = []
        self.special: bool = False
        is_special = False
        for special_property in config.special_symbols.keys():
            if name in config.special_symbols[special_property]:
                setattr(self, special_property, True)
                is_special = True

        if is_special:
            setattr(self, "special", True)

        self.assign_paying_bool(config)

    def register_special_function(
        self, special_function: Callable[[Symbol], None]
    ) -> None:
        """Register a special function to execute when symbol appears.

        Args:
            special_function: Function that takes Symbol as parameter
        """
        self.special_functions.append(special_function)

    def apply_special_function(self) -> None:
        """Execute all registered special functions on this symbol."""
        for fun in self.special_functions:
            fun(self)

    def assign_paying_bool(self, config: Config) -> None:
        """Determine if symbol pays and extract its paytable values.

        Sets self.is_paying and self.paytable based on config.paytable.

        Args:
            config: Game configuration with paytable
        """
        paying_symbols: set[str] = set()
        pay_value: list[dict[str, float]] = []
        for tup, val in config.paytable.items():
            assert isinstance(
                tup[1], str
            ), "paytable expects string for symbol name, (kind, symbol): value"
            paying_symbols.add(tup[1])
            if self.name == tup[1]:
                pay_value.append({str(tup[0]): val})
        if self.name not in list(paying_symbols):
            self.is_paying: bool = False
            self.paytable: list[dict[str, float]] | None = None
        else:
            self.is_paying = True
            self.paytable = pay_value

    def is_special(self) -> bool:
        """Check if symbol has any special properties.

        Returns:
            True if symbol has special properties
        """
        return self.special

    def check_attribute(self, *args: str) -> bool:
        """Check if any of the given attributes exist and are truthy.

        Args:
            *args: Attribute names to check

        Returns:
            True if any attribute exists and is truthy
        """
        for arg in args:
            if hasattr(self, arg) and (
                not (isinstance(getattr(self, arg), bool)) or getattr(self, arg) is True
            ):
                return True
        return False

    def get_attribute(self, attribute: str) -> Any:
        """Get value of a symbol attribute.

        Args:
            attribute: Attribute name to retrieve

        Returns:
            Attribute value, or False if attribute doesn't exist
        """
        return getattr(self, attribute, False)

    def assign_attribute(self, attribute_dict: dict[str, Any]) -> None:
        """Assign attributes to symbol dynamically.

        Args:
            attribute_dict: Dictionary of {attribute_name: value} to set
        """
        for prop, value in attribute_dict.items():
            setattr(self, prop, value)

    def __eq__(self, other: object) -> bool:
        """Check equality based on symbol name.

        Args:
            other: Object to compare (usually a string or Symbol)

        Returns:
            True if names match
        """
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, Symbol):
            return self.name == other.name
        return False
