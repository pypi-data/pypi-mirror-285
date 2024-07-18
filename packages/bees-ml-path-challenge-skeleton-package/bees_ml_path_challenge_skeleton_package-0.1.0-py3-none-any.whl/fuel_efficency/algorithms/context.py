from dataclasses import dataclass, field
from typing import List

from fuel_efficency.algorithms.dijkstra import DijkstraStrategy
from fuel_efficency.algorithms.path_finding import PathfindingStrategy
from fuel_efficency.entities.node import Node
from fuel_efficency.entities.valley import Valley


@dataclass(slots=True)
class Context:
    _strategy: PathfindingStrategy = field(default_factory=DijkstraStrategy)
    _grid: List[List[Node]] = field(default_factory=lambda: [[Valley() for _ in range(3)] for _ in range(3)])
    _start: Node = field(default_factory=Valley)
    _end: Node = field(default_factory=Valley)

    @property
    def grid(self):
        return self._grid

    @grid.setter
    def grid(self, new_grid: List[List[Node]]):
        if not isinstance(new_grid, list):
            raise TypeError("Grid must be a list")
        if not all(isinstance(row, list) for row in new_grid):
            raise TypeError("Grid must be a list of lists")
        self._grid = new_grid

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, new_start: Node):
        self._start = new_start

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, new_end: Node):
        self._end = new_end

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, new_strategy: PathfindingStrategy):
        if not isinstance(new_strategy, PathfindingStrategy):
            raise TypeError("Strategy must be an instance of PathfindingStrategy")
        self._strategy = new_strategy

    def run(self):
        if not hasattr(self._strategy, 'find_path'):
            raise NotImplementedError("Strategy must implement the find_path method")
        return self._strategy.find_path(self.grid, self.start, self.end)
