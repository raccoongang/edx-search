"""
Defines the dataclasses used in the search module.
"""
from dataclasses import dataclass


@dataclass
class SortField:
    """
    Represents a single sort entry in the search results.
    """
    name: str
    type_: str
    order: str = "asc"
