"""Everything related to unit groups in the game goes here"""
import random
from typing import List, Dict, Set, Any, Optional, Union
from .unit import Unit
from .ids.unit_typeid import UnitTypeId
from .position import Point2, Point3


class Units(list):
    """A collection for units. Makes it easy to select units by selectors."""

    @classmethod
    def from_proto(cls, units, game_data):
        """Gets data from the sc2 protocol"""
        return cls((Unit(u, game_data) for u in units), game_data)

    def __init__(self, units, game_data):
        super().__init__(units)
        self.game_data = game_data

    def __call__(self, *args, **kwargs):
        return UnitSelection(self, *args, **kwargs)

    def select(self, *args, **kwargs):
        """Makes unit selections"""
        return UnitSelection(self, *args, **kwargs)

    def __or__(self, other: "Units") -> "Units":
        tags = {unit.tag for unit in self}
        units = self + [unit for unit in other if unit.tag not in tags]
        return Units(units, self.game_data)

    def __and__(self, other: "Units") -> "Units":
        tags = {unit.tag for unit in self}
        units = [unit for unit in other if unit.tag in tags]
        return Units(units, self.game_data)

    def __sub__(self, other: "Units") -> "Units":
        tags = {unit.tag for unit in other}
        units = [unit for unit in self if unit.tag not in tags]
        return Units(units, self.game_data)

    def find_by_tag(self, tag) -> Optional[Unit]:
        """Finds units in the group by tag"""
        for unit in self:
            if unit.tag == tag:
                return unit
        return None

    @property
    def first(self) -> Unit:
        """Returns the first unit on the units list"""
        assert self
        return self[0]

    def take(self, quantity: int, require_all: bool = True) -> "Units":
        """Returns the first units until the parameters quantity from the units list"""
        assert (not require_all) or len(self) >= quantity
        return self[:quantity]

    @property
    def random(self) -> Unit:
        """Returns a random unit on the units list"""
        assert self
        return random.choice(self)

    def random_or(self, other: any) -> Unit:
        """Returns a random unit on the units list or any other unit if the units list is empty"""
        if self:
            return random.choice(self)
        return other

    def random_group_of(self, quantity):
        """Returns a quantity of random units on the units list that are determined by the parameter value"""
        assert 0 <= quantity <= len(self)
        if not quantity:
            return self.subgroup([])
        if len(self) == quantity:
            return self
        return self.subgroup(random.sample(self, quantity))

    def in_attack_range_of(self, unit: Unit, bonus_distance: Union[int, float] = 0) -> "Units":
        """ Filters units that are in attack range of the unit in parameter """
        return self.filter(lambda x: unit.target_in_range(x, bonus_distance=bonus_distance))

    def closest_distance_to(self, position: Union[Unit, Point2, Point3]) -> Union[int, float]:
        """ Returns the distance between the closest unit from this group to the target unit """
        assert self
        if isinstance(position, Unit):
            position = position.position
        return position.distance_to_closest([u.position for u in self])

    def furthest_distance_to(self, position: Union[Unit, Point2, Point3]) -> Union[int, float]:
        """ Returns the distance between the furthest unit from this group to the target unit """
        assert self
        if isinstance(position, Unit):
            position = position.position
        return position.distance_to_furthest([u.position for u in self])

    def closest_to(self, position: Union[Unit, Point2, Point3]) -> Unit:
        """ Returns closest unit to the argument"""
        assert self
        if isinstance(position, Unit):
            position = position.position
        return position.closest(self)

    def furthest_to(self, position: Union[Unit, Point2, Point3]) -> Unit:
        """ Returns furthest unit to the argument"""
        assert self
        if isinstance(position, Unit):
            position = position.position
        return position.furthest(self)

    def closer_than(self, distance: Union[int, float], position: Union[Unit, Point2, Point3]) -> "Units":
        """ Returns units closer than the parameter distance value to the argument"""
        if isinstance(position, Unit):
            position = position.position
        return self.filter(lambda unit: unit.position.distance_to_point2(position.to2) < distance)

    def further_than(self, distance: Union[int, float], position: Union[Unit, Point2, Point3]) -> "Units":
        """ Returns units further than the parameter distance value to the argument"""
        if isinstance(position, Unit):
            position = position.position
        return self.filter(lambda unit: unit.position.distance_to_point2(position.to2) > distance)

    def subgroup(self, units):
        """Returns a subgroup of units from the main group"""
        return Units(list(units), self.game_data)

    def filter(self, pred: callable) -> "Units":
        """Filter out a subgroup of units from the main group"""
        return self.subgroup(filter(pred, self))

    def sorted(self, keyfn: callable, reverse: bool = False) -> "Units":
        """Sort units from the main group based on given key"""
        return self.subgroup(sorted(self, key=keyfn, reverse=reverse))

    def sorted_by_distance_to(self, position: Union[Unit, Point2], reverse: bool = False) -> "Units":
        """ This function should be a bit faster than using units.sorted(keyfn=lambda u: u.distance_to(position)) """
        position = position.position
        return self.sorted(keyfn=lambda unit: unit.position.distance_squared(position), reverse=reverse)

    def tags_in(self, other: Union[Set[int], List[int], Dict[int, Any]]) -> "Units":
        """ Filters all units that have their tags in the 'other' set/list/dict """
        if isinstance(other, list):
            other = set(other)
        return self.filter(lambda unit: unit.tag in other)

    def tags_not_in(self, other: Union[Set[int], List[int], Dict[int, Any]]) -> "Units":
        """ Filters all units that have their tags not in the 'other' set/list/dict """
        if isinstance(other, list):
            other = set(other)
        return self.filter(lambda unit: unit.tag not in other)

    def of_type(self, other: Union[UnitTypeId, Set[UnitTypeId], List[UnitTypeId], Dict[UnitTypeId, Any]]) -> "Units":
        """ Filters all units that are of a specific type """
        if isinstance(other, UnitTypeId):
            other = {other}
        if isinstance(other, list):
            other = set(other)
        return self.filter(lambda unit: unit.type_id in other)

    def exclude_type(
        self, other: Union[UnitTypeId, Set[UnitTypeId], List[UnitTypeId], Dict[UnitTypeId, Any]]
    ) -> "Units":
        """ Filters all units that are not of a specific type """
        if isinstance(other, UnitTypeId):
            other = {other}
        if isinstance(other, list):
            other = set(other)
        return self.filter(lambda unit: unit.type_id not in other)

    def same_tech(self, other: Union[UnitTypeId, Set[UnitTypeId], List[UnitTypeId], Dict[UnitTypeId, Any]]) -> "Units":
        """ Usage:
        'self.units.same_tech(UnitTypeId.COMMANDCENTER)' or 'self.units.same_tech(ORBITALCOMMAND)'
        returns all CommandCenter, CommandCenterFlying, OrbitalCommand, OrbitalCommandFlying, PlanetaryFortress
        This also works with a set/list/dict parameter, e.g. 'self.units.same_tech({COMMANDCENTER, SUPPLYDEPOT})'
        Untested: This should return the equivalents for Hatchery, WarpPrism, Observer, Overseer, SupplyDepot and others
        """
        if isinstance(other, UnitTypeId):
            other = {other}
        tech_alias_types = set(other)
        for unit_type in other:
            tech_alias = self.game_data.units[unit_type.value].tech_alias
            if tech_alias:
                for same in tech_alias:
                    tech_alias_types.add(same)
        return self.filter(
            lambda unit: unit.type_id in tech_alias_types
            or unit.type_data.tech_alias is not None
            and any(same in tech_alias_types for same in unit.type_data.tech_alias)
        )

    def same_unit(self, other: Union[UnitTypeId, Set[UnitTypeId], List[UnitTypeId], Dict[UnitTypeId, Any]]) -> "Units":
        """ Usage:
        'self.units.same_tech(UnitTypeId.COMMANDCENTER)'
        returns CommandCenter and CommandCenterFlying,
        'self.units.same_tech(UnitTypeId.ORBITALCOMMAND)'
        returns OrbitalCommand and OrbitalCommandFlying
        This also works with a set/list/dict parameter, e.g. 'self.units.same_tech({COMMANDCENTER, SUPPLYDEPOT})'
        Untested: This should return the equivalents for WarpPrism, Observer, Overseer, SupplyDepot and others
        """
        if isinstance(other, UnitTypeId):
            other = {other}
        unit_alias_types = set(other)
        for unit_type in other:
            unit_alias = self.game_data.units[unit_type.value].unit_alias
            if unit_alias:
                unit_alias_types.add(unit_alias)
        return self.filter(
            lambda unit: unit.type_id in unit_alias_types
            or unit.type_data.unit_alias is not None
            and unit.type_data.unit_alias in unit_alias_types
        )

    @property
    def center(self) -> Point2:
        """ Returns the central point of all units in this list """
        assert self
        pos = Point2(
            (sum([unit.position.x for unit in self]) / len(self), sum([unit.position.y for unit in self]) / len(self))
        )
        return pos

    @property
    def selected(self) -> "Units":
        """Returns the selected units"""
        return self.filter(lambda unit: unit.is_selected)

    @property
    def tags(self) -> Set[int]:
        """Returns the units tags"""
        return {unit.tag for unit in self}

    @property
    def ready(self) -> "Units":
        """Returns the units from the list that are not on the training queue"""
        return self.filter(lambda unit: unit.is_ready)

    @property
    def not_ready(self) -> "Units":
        """Returns the units from the list that are on the training queue"""
        return self.filter(lambda unit: not unit.is_ready)

    @property
    def noqueue(self) -> "Units":
        """Returns the units from the list that don't have a queue or if their queue is empty"""
        return self.filter(lambda unit: unit.noqueue)

    @property
    def idle(self) -> "Units":
        """Returns the units from the list that don't have order queue"""
        return self.filter(lambda unit: unit.is_idle)

    @property
    def owned(self) -> "Units":
        """Returns the units from the list that are owned by you(your bot)"""
        return self.filter(lambda unit: unit.is_mine)

    @property
    def enemy(self) -> "Units":
        """Returns the units from the list that are owned by you(your bot) opponent"""
        return self.filter(lambda unit: unit.is_enemy)

    @property
    def flying(self) -> "Units":
        """Returns the units from the list that are flying"""
        return self.filter(lambda unit: unit.is_flying)

    @property
    def not_flying(self) -> "Units":
        """Returns the units from the list that are not flying"""
        return self.filter(lambda unit: not unit.is_flying)

    @property
    def structure(self) -> "Units":
        """Returns the units from the list that are structures"""
        return self.filter(lambda unit: unit.is_structure)

    @property
    def not_structure(self) -> "Units":
        """Returns the units from the list that are not structures"""
        return self.filter(lambda unit: not unit.is_structure)

    @property
    def gathering(self) -> "Units":
        """Returns the units from the list that are gathering"""
        return self.filter(lambda unit: unit.is_gathering)

    @property
    def returning(self) -> "Units":
        """Returns the units from the list that are returning resources"""
        return self.filter(lambda unit: unit.is_returning)

    @property
    def collecting(self) -> "Units":
        """Unite both properties from above"""
        return self.filter(lambda unit: unit.is_collecting)

    @property
    def mineral_field(self) -> "Units":
        """Returns the mineral fields from the list"""
        return self.filter(lambda unit: unit.is_mineral_field)

    @property
    def vespene_geyser(self) -> "Units":
        """Returns the geysers from the list"""
        return self.filter(lambda unit: unit.is_vespene_geyser)

    @property
    def prefer_idle(self) -> "Units":
        """Sort the list putting the idle units first"""
        return self.sorted(lambda unit: unit.is_idle, reverse=True)

    def prefer_close_to(self, unit_or_point: Union[Unit, Point2, Point3]) -> "Units":
        """Sort the list putting the closer units to the parameter position first"""
        return self.sorted(lambda unit: unit.distance_to(unit_or_point))


class UnitSelection(Units):
    """Group requirement to select a group of units"""

    def __init__(self, parent, unit_type_id=None):
        assert unit_type_id is None or isinstance(unit_type_id, (UnitTypeId, set))
        if isinstance(unit_type_id, set):
            assert all(isinstance(t, UnitTypeId) for t in unit_type_id)

        self.unit_type_id = unit_type_id
        super().__init__([u for u in parent if self.matches(u)], parent.game_data)

    def matches(self, unit):
        """Group units that matches the parameter"""
        if not self.unit_type_id:
            return True
        if isinstance(self.unit_type_id, set):
            return unit.type_id in self.unit_type_id
        return self.unit_type_id == unit.type_id
