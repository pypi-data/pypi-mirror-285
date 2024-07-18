from dataclasses import dataclass

from fuel_efficency.entities.node import Node
from fuel_efficency.entities.position import Position


@dataclass(slots=True)
class UpHill(Node):
    weight: float = float(2)
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

    up_hill = UpHill()
    print(up_hill)
    print(up_hill.position)
    print(up_hill.weight)
    print(up_hill == UpHill())
    print(up_hill < UpHill(weight=float(2)))
    print(hash(up_hill))
