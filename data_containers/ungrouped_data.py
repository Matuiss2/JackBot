"""All data that couldn't be grouped(yet) are here"""
from sc2.constants import DRONE, PROBE, SCV


class OtherData:
    """This is the data container for all ungroupable data"""

    def __init__(self):
        self.enemies = self.flying_enemies = self.ground_enemies = self.enemy_structures = None
        self.furthest_townhall_to_map_center = None

    def initialize_enemies(self):
        """Initialize everything related to enemies"""
        excluded_from_ground = {DRONE, SCV, PROBE}
        self.enemies = self.known_enemy_units
        self.flying_enemies = self.enemies.flying
        self.ground_enemies = self.enemies.not_flying.not_structure.exclude_type(excluded_from_ground)
        self.enemy_structures = self.known_enemy_structures

    def prepare_bases_data(self):
        """Prepare data related to our bases"""
        if self.townhalls:
            self.furthest_townhall_to_map_center = self.townhalls.furthest_to(self.game_info.map_center)
