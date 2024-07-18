import math
from typing import List

import pytest

from fuel_efficency.algorithms.a_star import AStarStrategy
from fuel_efficency.algorithms.context import Context
from fuel_efficency.algorithms.dijkstra import DijkstraStrategy
from fuel_efficency.algorithms.path_finding import PathfindingStrategy
from fuel_efficency.entities.node import Node
from fuel_efficency.entities.position import Position
from fuel_efficency.entities.valley import Valley


def create_3_by_3_flat_terrain_grid():
    return [[Valley(position=Position(x, y)) for y in range(3)] for x in range(3)]


test_data = [
    (Valley(position=Position(1, 1)), 8),  # Center
    (Valley(position=Position(0, 0)), 3),  # Top left corner
    (Valley(position=Position(0, 1)), 5),  # Top edge
    (Valley(position=Position(0, 2)), 3),  # Top right corner
    (Valley(position=Position(1, 0)), 5),  # Left edge
    (Valley(position=Position(1, 2)), 5),  # Right edge
    (Valley(position=Position(2, 0)), 3),  # Bottom left corner
    (Valley(position=Position(2, 1)), 5),  # Bottom edge
    (Valley(position=Position(2, 2)), 3),  # Bottom right corner
]

@pytest.mark.parametrize("start_node, expected_neighbors_count", test_data)
def test_get_neighbors(start_node:Node, expected_neighbors_count:int):
    grid = create_3_by_3_flat_terrain_grid()
    grid_width = len(grid)
    grid_height = len(grid[0])
    neighbors = DijkstraStrategy.get_neighbors(grid, start_node)
    assert len(neighbors) == expected_neighbors_count
    assert all(0 <= neighbor.position.x < grid_width and 0 <= neighbor.position.y < grid_height for neighbor in neighbors)


distance_test_data = [
    (Valley(position=Position(0, 0)), Valley(position=Position(1, 1)), math.sqrt(2)),  # Diagonal distance
    (Valley(position=Position(0, 0)), Valley(position=Position(0, 1)), 1),  # Vertical distance
    (Valley(position=Position(0, 0)), Valley(position=Position(1, 0)), 1),  # Horizontal distance
]

@pytest.mark.parametrize("node1, node2, expected_distance", distance_test_data)
def test_calculate_distance(node1: Node, node2: Node, expected_distance: float):
    calculated_distance = DijkstraStrategy.calculate_distance(node1, node2)
    assert math.isclose(calculated_distance, expected_distance, rel_tol=1e-9)

def test_dijkstra_find_path():
    grid = create_3_by_3_flat_terrain_grid()
    start = grid[0][0]  # Top-left corner
    end = grid[2][2]  # Bottom-right corner

    # Expected path: straight line from top-left to bottom-right ommitting the start position as there's no weight
    expected_path = [
        grid[x][x] for x in range(1, 3)
    ]

    path = DijkstraStrategy.find_path(grid, start, end)

    assert path == expected_path

def test_astar_find_path():
    grid = create_3_by_3_flat_terrain_grid()
    start = grid[0][0]  # Top-left corner
    end = grid[2][2]  # Bottom-right corner

    # Expected path: straight line from top-left to bottom-right ommitting the start position as there's no weight
    positions = [Position(0, 1), Position(0, 2), Position(1, 2), Position(2, 2)]

    expected_path = [Valley(position=position) for position in positions]

    path = AStarStrategy.find_path(grid, start, end)

    assert path == expected_path

grid = create_3_by_3_flat_terrain_grid()
start_node = grid[0][0]  # Top-left corner
end_node = grid[2][2]  # Bottom-right corner

test_cases = [
    (AStarStrategy(), grid, start_node, end_node),
    (DijkstraStrategy(), grid, start_node, end_node)
]

from unittest.mock import MagicMock


@pytest.mark.parametrize("strategy, grid, start, end", test_cases)
def test_context_run(strategy:PathfindingStrategy, grid:List[List[Node]], start:Node, end:Node):
    strategy.find_path = MagicMock(spec=PathfindingStrategy.find_path)
    context:Context = Context(_strategy=strategy, _grid=grid, _start=start, _end=end)
    _ = context.run()
    strategy.find_path.assert_called_once_with(grid, start, end)
    assert context.strategy == strategy
    assert context.grid == grid
    assert context.start == start
    assert context.end == end

def test_grid_setter_invalid_type() -> None:
    """
    Test that an error is raised when an invalid type is set for the grid attribute.

    Args:
        None

    Returns:
        None: This function should not return anything.
    """
    context = Context(_strategy=AStarStrategy(), _grid=[], _start=Valley(), _end=Valley())
    invalid_grid = "not a list"

    with pytest.raises(TypeError) as excinfo:
        context.grid = invalid_grid
    assert "Grid must be a list" in str(excinfo.value)

def test_grid_setter_invalid_row_type() -> None:
    """
    Test that an error is raised when the grid attribute is not a list of lists.

    Args:
        None

    Returns:
        None: This function should not return anything.
    """
    context = Context(_strategy=AStarStrategy(), _grid=[], _start=Valley(), _end=Valley())
    invalid_grid = [10, 20]  # Not a list of lists

    with pytest.raises(TypeError) as excinfo:
        context.grid = invalid_grid
    assert "Grid must be a list of lists" in str(excinfo.value)

def test_strategy_setter_invalid_type() -> None:
    """
    Test that an error is raised when an invalid type is set for the strategy attribute.

    Args:
        None

    Returns:
        None: This function should not return anything.
    """
    context = Context(_strategy=AStarStrategy(), _grid=[], _start=Valley(), _end=Valley())
    invalid_strategy = "not a PathfindingStrategy object"

    with pytest.raises(TypeError) as excinfo:
        context.strategy = invalid_strategy
    assert "Strategy must be an instance of PathfindingStrategy" in str(excinfo.value)

def test_run_method_missing_find_path() -> None:
    """
    Test that an error is raised when the strategy does not implement the find_path method.

    Args:
        None

    Returns:
        None: This function should not return anything.
    """
    context = Context(_strategy=object(), _grid=[], _start=Valley(), _end=Valley())

    with pytest.raises(NotImplementedError) as excinfo:
        context.run()
    assert "Strategy must implement the find_path method" in str(excinfo.value)


def test_context_run_success():
    """
    Test that the Context class successfully runs the pathfinding strategy.

    Args:
        None

    Returns:
        None: This function should not return anything.
    """

    class MockPathfindingStrategy(PathfindingStrategy):
        def find_path(self, grid, start:Node, end:Node):
            # Implement a simple path finding logic for testing,
            # or return a predefined path
            return [Valley(position=Position(x, y)) for x in range(start.position.x, end.position.x + 1) for y in range(start.position.y, end.position.y + 1)]
        def calculate_distance(self, node1, node2):
            pass
        def get_neighbors(self, grid, node):
            pass

    grid = [[Valley() for _ in range(3)] for _ in range(3)]
    start = Valley(position=Position(0, 0))  # Top-left corner
    end = Valley(position=Position(2, 2))    # Bottom-right corner
    strategy = MockPathfindingStrategy()

    context:Context = Context()
    context.grid = grid
    context.start = start
    context.end = end
    context.strategy = strategy

    # Define expected path based on the MockPathfindingStrategy's logic
    expected_path = [Valley(position=Position(x, y)) for x in range(start.position.x, end.position.x + 1) for y in range(start.position.y, end.position.y + 1)]

    path = context.run()

    assert path == expected_path, "The path should match the expected path"
