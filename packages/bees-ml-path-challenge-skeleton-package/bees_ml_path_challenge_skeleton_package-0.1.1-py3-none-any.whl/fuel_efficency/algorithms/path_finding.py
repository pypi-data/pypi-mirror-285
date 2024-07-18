from abc import ABC, abstractmethod
from typing import List

from fuel_efficency.entities.node import Node


class PathfindingStrategy(ABC):

    @abstractmethod
    def find_path(grid:List[List[Node]], start:Node, end:Node):
        pass # pragma: no cover

    @abstractmethod
    def get_neighbors(grid:List[List[Node]], node:Node) -> List[Node]:
        pass # pragma: no cover

    @abstractmethod
    def calculate_distance(node1:Node, node2: Node) -> float:
        pass # pragma: no cover
