"""All data that couldn't be grouped(yet) are here"""
from sc2.constants import UnitTypeId


class OtherData:
    """This is the data container for all not grouped stuff"""

    def __init__(self):
        self.enemies = self.enemy_buildings = self.flying_enemies = self.flying_enemy_structures = None
        self.furthest_townhall_to_center = self.ground_enemies = None
        self.worker_types = {UnitTypeId.DRONE, UnitTypeId.PROBE, UnitTypeId.SCV}

    def initialize_enemies(self):
        """Initialize everything related to enemies"""
        self.enemies = self.enemy_units
        self.enemy_buildings = self.enemy_structures.exclude_type(UnitTypeId.AUTOTURRET)
        self.flying_enemies = self.enemies.flying
        self.flying_enemy_structures = self.enemy_buildings.flying
        self.ground_enemies = self.enemies.not_flying.not_structure.exclude_type(self.worker_types)

    def prepare_bases_data(self):
        """Global variable for the furthest townhall to center"""
        if self.townhalls:
            self.furthest_townhall_to_center = self.townhalls.furthest_to(self.game_info.map_center)
