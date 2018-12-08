"""Groups all data from sc2 ->  ability, unit, upgrades, cost"""
from bisect import bisect_left
from functools import lru_cache, reduce
from typing import List, Optional

from .data import ATTRIBUTE, RACE
from .unit_command import UnitCommand

from .ids.unit_typeid import UnitTypeId
from .ids.ability_id import AbilityId

from .constants import ZERGLING

FREE_MORPH_ABILITY_CATEGORIES = ["Lower", "Raise", "Land", "Lift"]


def split_camel_case(text) -> list:
    """Splits words from CamelCase text."""
    return list(reduce(lambda a, b: (a + [b] if b.isupper() else a[:-1] + [a[-1] + b]), text, []))


class GameData:
    """Its the main class from this files, it groups and organizes all the others"""

    def __init__(self, data):
        ids = tuple(a.value for a in AbilityId if a.value != 0)
        self.abilities = {a.ability_id: AbilityData(self, a) for a in data.abilities if a.ability_id in ids}
        self.units = {u.unit_id: UnitTypeData(self, u) for u in data.units if u.available}
        self.upgrades = {u.upgrade_id: UpgradeData(self, u) for u in data.upgrades}
        self.effects = {e.effect_id: EffectRawData(self, e) for e in data.effects}

    @lru_cache(maxsize=256)
    def calculate_ability_cost(self, ability) -> "Cost":
        """Returns the resources cost for the abilities, units, upgrades"""
        if isinstance(ability, AbilityId):
            ability = self.abilities[ability.value]
        elif isinstance(ability, UnitCommand):
            ability = self.abilities[ability.ability.value]
        assert isinstance(ability, AbilityData), f"C: {ability}"
        for unit in self.units.values():
            if unit.creation_ability is None:
                continue
            if not AbilityData.id_exists(unit.creation_ability.id.value):
                continue
            if unit.creation_ability.is_free_morph:
                continue
            if unit.creation_ability == ability:
                if unit.id == ZERGLING:
                    return Cost(unit.cost.minerals * 2, unit.cost.vespene * 2, unit.cost.time)
                morph_cost = unit.morph_cost
                if morph_cost:  # can be None
                    return morph_cost
                return unit.cost_zerg_corrected
        for upgrade in self.upgrades.values():
            if upgrade.research_ability == ability:
                return upgrade.cost
        return Cost(0, 0)


class EffectRawData:
    """Group and work with all data related to effects"""

    def __init__(self, game_data, proto):
        self._game_data = game_data
        self.proto = proto

    @property
    def id(self) -> int:
        """Return the effect id"""
        return self.proto.effect_id

    @property
    def name(self) -> str:
        """Return the effect name"""
        return self.proto.name

    @property
    def friendly_name(self) -> str:
        """Check if the effect is friendly(from the player or an ally)"""
        return self.proto.friendly_name

    @property
    def radius(self) -> float:
        """Check the area of the effect"""
        return self.proto.radius


class AbilityData:
    """Group and work with all data related to abilities"""

    ability_ids: List[int] = []
    for ability_id in AbilityId:
        ability_ids.append(ability_id.value)
    ability_ids.remove(0)
    ability_ids.sort()

    @classmethod
    def id_exists(cls, ability_id):
        """Check if the ability id exists"""
        assert isinstance(ability_id, int), f"Wrong type: {ability_id} is not int"
        if ability_id == 0:
            return False
        i = bisect_left(cls.ability_ids, ability_id)  # quick binary search
        return i != len(cls.ability_ids) and cls.ability_ids[i] == ability_id

    def __init__(self, game_data, proto):
        self._game_data = game_data
        self.proto = proto
        assert self.id != 0

    def __repr__(self) -> str:
        return f"AbilityData(name={self.proto.button_name})"

    @property
    def id(self) -> AbilityId:
        """Returns the id numbers of the abilities"""
        if self.proto.remaps_to_ability_id:
            return AbilityId(self.proto.remaps_to_ability_id)
        return AbilityId(self.proto.ability_id)

    @property
    def link_name(self) -> str:
        """ For Stimpack this returns 'BarracksTechLabResearch' """
        return self.proto.button_name

    @property
    def button_name(self) -> str:
        """ For Stimpack this returns 'Stimpack' """
        return self.proto.button_name

    @property
    def friendly_name(self) -> str:
        """ For Stimpack this returns 'Research Stimpack' """
        return self.proto.friendly_name

    @property
    def is_free_morph(self) -> bool:
        """If morphing the unit is free it returns True"""
        parts = split_camel_case(self.proto.link_name)
        for part in parts:
            if part in FREE_MORPH_ABILITY_CATEGORIES:
                return True
        return False

    @property
    def cost(self) -> "Cost":
        """Returns the ability cost"""
        return self._game_data.calculate_ability_cost(self.id)


class UnitTypeData:
    """Group and work with all data related to units"""

    def __init__(self, game_data, proto):
        self._game_data = game_data
        self.proto = proto

    def __repr__(self) -> str:
        return "UnitTypeData(name={})".format(self.name)

    @property
    def id(self) -> UnitTypeId:
        """Returns the id numbers of the units"""
        return UnitTypeId(self.proto.unit_id)

    @property
    def name(self) -> str:
        """Returns the names of the units"""
        return self.proto.name

    @property
    def creation_ability(self) -> Optional[AbilityData]:
        """Check if the unit has a creation ability"""
        if self.proto.ability_id and self.proto.ability_id in self._game_data.abilities:
            return self._game_data.abilities[self.proto.ability_id]
        return None

    @property
    def attributes(self) -> List[ATTRIBUTE]:
        """Return a list of attributes of the unit"""
        return self.proto.attributes

    def has_attribute(self, attr) -> bool:
        """Return True if the unit has specified attribute"""
        assert isinstance(attr, ATTRIBUTE)
        return attr in self.attributes

    @property
    def has_minerals(self) -> bool:
        """Return True if the unit has minerals(only useful for mineral patches)"""
        return self.proto.has_minerals

    @property
    def has_vespene(self) -> bool:
        """Return True if the unit has vespene(only useful for geysers)"""
        return self.proto.has_vespene

    @property
    def cargo_size(self) -> int:
        """ How much cargo this unit uses up in cargo_space """
        return self.proto.cargo_size

    @property
    def tech_requirement(self) -> Optional[UnitTypeId]:
        """ Tech-building requirement of buildings - may work for units but unreliably """
        if not self.proto.tech_requirement:
            return None
        if self.proto.tech_requirement not in self._game_data.units:
            return None
        return UnitTypeId(self.proto.tech_requirement)

    @property
    def tech_alias(self) -> Optional[List[UnitTypeId]]:
        """ Building tech equality, e.g. OrbitalCommand is the same as CommandCenter
        Building tech equality, e.g. Hive is the same as Lair and Hatchery """
        return_list = []
        for tech_alias in self.proto.tech_alias:
            if tech_alias in self._game_data.units:
                return_list.append(UnitTypeId(tech_alias))
        if return_list:
            return return_list
        return None

    @property
    def unit_alias(self) -> Optional[UnitTypeId]:
        """ Building type equality, e.g. FlyingOrbitalCommand is the same as OrbitalCommand """
        if not self.proto.unit_alias:
            return None
        if self.proto.unit_alias not in self._game_data.units:
            return None
        return UnitTypeId(self.proto.unit_alias)

    @property
    def race(self) -> RACE:
        """Returns the race which the unit belongs"""
        return RACE(self.proto.race)

    @property
    def cost(self) -> "Cost":
        """Returns the unit cost"""
        return Cost(self.proto.mineral_cost, self.proto.vespene_cost, self.proto.build_time)

    @property
    def cost_zerg_corrected(self) -> "Cost":
        """ This returns 25 for extractor and 200 for spawning pool instead of 75 and 250 respectively """
        if self.race == RACE.Zerg and ATTRIBUTE.Structure.value in self.attributes:
            return Cost(self.proto.mineral_cost - 50, self.proto.vespene_cost, self.proto.build_time)
        return self.cost

    @property
    def morph_cost(self) -> Optional["Cost"]:
        """ This returns 150 minerals for OrbitalCommand instead of 550 """
        if self.tech_alias is None or self.tech_alias[0] in {UnitTypeId.TECHLAB, UnitTypeId.REACTOR}:
            return None
        tech_alias_cost_minerals = max(
            [self._game_data.units[tech_alias.value].cost.minerals for tech_alias in self.tech_alias]
        )
        tech_alias_cost_vespene = max(
            [self._game_data.units[tech_alias.value].cost.vespene for tech_alias in self.tech_alias]
        )
        return Cost(
            self.proto.mineral_cost - tech_alias_cost_minerals,
            self.proto.vespene_cost - tech_alias_cost_vespene,
            self.proto.build_time,
        )


class UpgradeData:
    """Group and work with all data related to upgrades"""

    def __init__(self, game_data, proto):
        self._game_data = game_data
        self.proto = proto

    def __repr__(self):
        return "UpgradeData({} - research ability: {}, {})".format(self.name, self.research_ability, self.cost)

    @property
    def name(self) -> str:
        """Returns the names of the units"""
        return self.proto.name

    @property
    def research_ability(self) -> Optional[AbilityData]:
        """Research the ability if its available"""
        if self.proto.ability_id and self.proto.ability_id in self._game_data.abilities:
            return self._game_data.abilities[self.proto.ability_id]
        return None

    @property
    def cost(self) -> "Cost":
        """Return the cost of the upgrade"""
        return Cost(self.proto.mineral_cost, self.proto.vespene_cost, self.proto.research_time)


class Cost:
    """Initialize resources and time cost for cost functions"""

    def __init__(self, minerals, vespene, time=None):
        self.minerals = minerals
        self.vespene = vespene
        self.time = time

    def __repr__(self) -> str:
        return f"Cost({self.minerals}, {self.vespene})"

    def __eq__(self, other) -> bool:
        return self.minerals == other.minerals and self.vespene == other.vespene

    def __ne__(self, other) -> bool:
        return self.minerals != other.minerals or self.vespene != other.vespene
