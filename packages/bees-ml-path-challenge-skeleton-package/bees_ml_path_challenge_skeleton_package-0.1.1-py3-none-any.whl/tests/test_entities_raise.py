import pytest

from fuel_efficency.entities.down_hill import DownHill
from fuel_efficency.entities.node import Node
from fuel_efficency.entities.plateau import Plateau
from fuel_efficency.entities.up_hill import UpHill
from fuel_efficency.entities.valley import Valley


@pytest.mark.parametrize("node", [Valley, UpHill, DownHill, Plateau])
def test_eq_error_raised(node:Node):
    valley = node()
    other = int()

    with pytest.raises(NotImplementedError) as excinfo:
        valley == other
    assert "Missing `position` or `weight` attribute" in str(excinfo.value)

@pytest.mark.parametrize("node", [Valley, UpHill, DownHill, Plateau])
def test_lt_error_raised(node:Node):
    valley = node()
    other = int()

    with pytest.raises(NotImplementedError) as excinfo:
        valley < other
    assert "Missing `weight` attribute" in str(excinfo.value)
