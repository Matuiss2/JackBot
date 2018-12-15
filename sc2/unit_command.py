"""Unit commands are grouped here"""
from . import unit as unit_module
from .ids.ability_id import AbilityId
from .position import Point2


class UnitCommand:
    """Get the ability, target, queue and unit performing it"""

    def __init__(self, ability, unit, target=None, queue=False):
        assert ability in AbilityId
        assert isinstance(unit, unit_module.Unit)
        assert not target or isinstance(target, (Point2, unit_module.Unit))
        assert isinstance(queue, bool)
        self.ability = ability
        self.unit = unit
        self.target = target
        self.queue = queue

    @property
    def combining_tuple(self):
        """Returns the needed values for a successful commands as a tuple"""
        return self.ability, self.target, self.queue

    def __repr__(self):
        return f"UnitCommand({self.ability}, {self.unit}, {self.target}, {self.queue})"
