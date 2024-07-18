import sys
from typing import TypeVar

import pytest

from fuel_efficency.entities.down_hill import DownHill
from fuel_efficency.entities.node import Node
from fuel_efficency.entities.plateau import Plateau
from fuel_efficency.entities.position import Position
from fuel_efficency.entities.up_hill import UpHill
from fuel_efficency.entities.valley import Valley


@pytest.mark.parametrize("expected_x, expected_y", [
    (0, 0),
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4)
])
def test_position(expected_x: int, expected_y: int) -> None:
    """
    Test the Position class.

    Args:
        expected_x (int): The expected x coordinate.
        expected_y (int): The expected y coordinate.

    Returns:
        None: This function should not return anything.
    """
    position = Position(x=expected_x, y=expected_y)
    assert isinstance(position.x, int), "Position x is not an instance of int."
    assert isinstance(position.y, int), "Position y is not an instance of int."
    assert position.x == expected_x, "Position x is not as expected."
    assert position.y == expected_y, "Position y is not as expected."

@pytest.mark.parametrize("node_protocol, expected_weight", [
    (Valley, float(1)),
    (Plateau, float(1)),
    (UpHill, float(2)),
    (DownHill, float(0.5)),
    (Node, float("inf"))
])
def test_node_weights(node_protocol:Node, expected_weight:float) -> None:
    """
    Test that the weight property of each node class is correct.

    Args:
        node_protocol (Node): The node class to test.
        expected_weight (float): The expected weight of the node class.

    Returns:
        None: This function should not return anything.
    """
    if node_protocol is not Node:
        node_protocol:Node = node_protocol()
        assert node_protocol.weight == expected_weight, f"Incorrect weight for {node_protocol.__name__}"
    else:
        with pytest.raises(TypeError):
            node_protocol()

@pytest.mark.parametrize("node_protocol", [
    (Valley),
    (Plateau),
    (UpHill),
    (DownHill)
])
def test_node_equality(node_protocol:Node) -> None:
    """
    Test that the node protocol is equal to itself.

    Args:
        node_protocol (Node): The node protocol to test.

    Returns:
        None: This function should not return anything.
    """
    node_protocol:Node = node_protocol()
    assert node_protocol == node_protocol, f"{node_protocol.__name__} is not equal to itself."
    assert hash(node_protocol) == hash(node_protocol), f"{node_protocol.__name__} hash is not equal to itself."
    MockNode = TypeVar("MockNode")
    mock_node:MockNode = Valley(weight=sys.maxsize)
    assert node_protocol < mock_node

@pytest.mark.parametrize("node_protocol", [
    (Valley),
    (Plateau),
    (UpHill),
    (DownHill)
])
def test_node_hash(node_protocol:Node) -> None:
    """
    Test that the node protocol hash is equal to itself.

    Args:
        node_protocol (Node): The node protocol to test.

    Returns:
        None: This function should not return anything.
    """
    node_protocol:Node = node_protocol()
    assert hash(node_protocol) == hash(node_protocol), f"{node_protocol.__name__} hash is not equal to itself."

@pytest.mark.parametrize("node_protocol", [
(Valley),
(Plateau),
(UpHill),
(DownHill)
])
def test_node_less_than(node_protocol:Node) -> None:
    """
    Test that the node protocol is less than a mock node.

    Args:
        node_protocol (Node): The node protocol to test.

    Returns:
        None: This function should not return anything.
    """
    node_protocol:Node = node_protocol()
    MockNode = TypeVar("MockNode")
    mock_node:MockNode = Valley(weight=sys.maxsize)
    assert node_protocol < mock_node

@pytest.mark.parametrize("node_protocol, expected_position", [
    (Valley, Position(x=0, y=0)),
    (Plateau, Position(x=0, y=0)),
    (UpHill, Position(x=0, y=0)),
    (DownHill, Position(x=0, y=0)),
    (Node, Position())
])
def test_node_positions(node_protocol:Node, expected_position:Position) -> None:
    """
    Test that the position property of each node class is correct.

    Args:
        node_protocol (Node): The node class to test.
        expected_position (Position): The expected position of the node class.

    Returns:
        None: This function should not return anything.
    """
    if node_protocol is not Node:
        node_protocol = node_protocol(position=expected_position)
        assert node_protocol.position == expected_position, f"Incorrect position for {node_protocol.__name__}"
    else:
        with pytest.raises(TypeError):
            node_protocol()

def test_position_add_success() -> None:
    """
    Test that the position class can be added to another position class.

    Args:
        None

    Returns:
        None: This function should not return anything.
    """
    position1 = Position(x=10, y=20)
    position2 = Position(x=5, y=3)

    result = position1 + position2
    assert result.x == 15 and result.y == 23, "Addition should correctly add Position coordinates"

def test_position_add_invalid_type() -> None:
    """
    Test that the position class can be added to another position class.

    Args:
        None

    Returns:
        None: This function should not return anything.
    """
    position = Position(x=10, y=20)
    other = "not a position object"

    with pytest.raises(NotImplementedError) as excinfo:
        _ = position + other
    assert f"Cannot add Position and {type(other)}" in str(excinfo.value)

def test_position_sub_success() -> None:
    """
    Test that the position class can be subtracted from another position class.

    Args:
        None

    Returns:
        None: This function should not return anything.
    """
    position1 = Position(x=10, y=20)
    position2 = Position(x=5, y=3)

    result = position1 - position2
    assert result.x == 5 and result.y == 17, "Subtraction should correctly subtract Position coordinates"

def test_position_sub_invalid_type() -> None:
    """
    Test that the position class can be subtracted from another position class.

    Args:
        None

    Returns:
        None: This function should not return anything.
    """
    position = Position(x=10, y=20)
    other = "not a position object"

    with pytest.raises(NotImplementedError) as excinfo:
        _ = position - other
    assert f"Cannot subtract Position and {type(other)}" in str(excinfo.value)
