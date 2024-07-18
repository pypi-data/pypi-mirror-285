import sys
from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Position:
    x: int = sys.maxsize
    y: int = sys.maxsize

    def __add__(self, other:'Position') -> Optional['Position']:
        """
        Add two Position objects together.

        Args:
            other (Position): The other Position object to add to this one.

        Returns:
            Position: The sum of the two Position objects.
        """
        if not isinstance(other, Position):
            raise NotImplementedError(f"Cannot add Position and {type(other)}")

        if self.x == sys.maxsize or self.y == sys.maxsize or other.x == sys.maxsize or other.y == sys.maxsize:
            return None
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other:'Position') -> Optional['Position']:
        """
        Subtract two Position objects.

        Args:
            other (Position): The other Position object to subtract from this one.

        Returns:
            Position: The difference of the two Position objects.
        """
        if not isinstance(other, Position):
            raise NotImplementedError(f"Cannot subtract Position and {type(other)}")

        if self.x == sys.maxsize or self.y == sys.maxsize or other.x == sys.maxsize or other.y == sys.maxsize:
            return None
        return Position(self.x - other.x, self.y - other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if not isinstance(other, Position):
            return NotImplemented
        return self.x == other.x and self.y == other.y
