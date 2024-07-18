from dataclasses import dataclass
from typing import Protocol

from fuel_efficency.entities.position import Position


@dataclass(slots=True)
class Node():
    weight: float
    position: 'Position' = Position()

    def __eq__(self, other: 'Node') -> bool:
        if not isinstance(other, Node):
            raise NotImplementedError("Missing `position` or `weight` attribute")
        return self.position == other.position

    def __lt__(self, other: 'Node') -> bool:
        if not isinstance(other, Node):
            raise NotImplementedError("Missing `weight` attribute")
        return self.weight < other.weight

    def __hash__(self) -> int:
        return hash((self.position, self.weight))


if __name__ == "__main__":
    node = Node(weight=float(1))
    print(node)
    print(node.position)
    print(node.weight)
    print(node == Node(weight=float(1)))
    print(node < Node(weight=float(2)))
    print(hash(node))
    print(node == Node(weight=float(2)))
    #print(node == 2)
