from __future__ import annotations
from typing import Union, TYPE_CHECKING

from . import unit as unit_module
from .ids.ability_id import AbilityId
from .position import Point2
from .constants import COMBINEABLE_ABILITIES


if TYPE_CHECKING:
    from .unit import Unit


class UnitCommand:
    def __init__(self, ability: AbilityId, unit: Unit, target: Union[Unit, Point2] = None, queue: bool = False):
        """
        :param ability:
        :param unit:
        :param target:
        :param queue:
        """
        if ability not in AbilityId:
            raise AssertionError(f"ability {ability} is not in AbilityId")
        if not isinstance(unit, unit_module.Unit):
            raise AssertionError(f"unit {unit} is of type {type(unit)}")
        if not (target is None or isinstance(target, (Point2, unit_module.Unit))):
            raise AssertionError(f"target {target} is of type {type(target)}")
        if not isinstance(queue, bool):
            raise AssertionError(f"queue flag {queue} is of type {type(queue)}")
        self.ability = ability
        self.unit = unit
        self.target = target
        self.queue = queue

    @property
    def combining_tuple(self):
        return self.ability, self.target, self.queue, self.ability in COMBINEABLE_ABILITIES

    def __repr__(self):
        return f"UnitCommand({self.ability}, {self.unit}, {self.target}, {self.queue})"
