from dataclasses import dataclass

from fuel_efficency.entities.node import Node
from fuel_efficency.entities.position import Position


@dataclass(slots=True)
class DownHill(Node):
    weight: float = float(0.5)
    position: 'Position' = Position()

    def __hash__(self) -> int:
        return hash((self.position, self.weight))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Node):
            raise NotImplementedError("Missing `position` or `weight` attribute")
        return self.position == other.position

    def __lt__(self, other) -> bool:
        if not isinstance(other, Node):
            raise NotImplementedError("Missing `weight` attribute")
        return self.weight < other.weight

if __name__ == "__main__":
    down_hill = DownHill()
    print(down_hill)
    print(down_hill.position)
    print(down_hill.weight)
    print(down_hill == DownHill())
    print(down_hill < DownHill(weight=float(2)))
    print(hash(down_hill))
    # eq
    print(down_hill == DownHill())
    print(down_hill == DownHill(weight=float(2)))
    # lt
    print(down_hill < DownHill())
    print(down_hill < DownHill(weight=float(2)))
