"""All situational data are here"""
from sc2.constants import UnitTypeId


class SituationalData:
    """This is the data container for all situational stuff"""

    def __init__(self):
        self.close_enemies_to_base = self.counter_attack_vs_flying = False
        self.basic_production_types = {UnitTypeId.BARRACKS, UnitTypeId.GATEWAY, UnitTypeId.HATCHERY}

    def check_for_floated_buildings(self):
        """Check if some terran wants to be funny with lifting up"""
        return (
            self.enemy_structures.flying
            and len(self.enemy_structures) == len(self.enemy_structures.flying)
            and self.time > 300
        )

    def check_for_proxy_buildings(self):
        """Check if there are any proxy buildings"""
        return bool(
            self.enemy_structures.filter(
                lambda building: building.type_id in self.basic_production_types
                and building.distance_to(self.start_location) < 75
            )
        )

    def prepare_enemy_data_points(self):
        """Prepare data related to enemy units"""
        if self.enemies:
            excluded_from_flying = {
                UnitTypeId.OVERLORD,
                UnitTypeId.OVERSEER,
                UnitTypeId.RAVEN,
                UnitTypeId.OBSERVER,
                UnitTypeId.WARPPRISM,
                UnitTypeId.MEDIVAC,
                UnitTypeId.VIPER,
                UnitTypeId.CORRUPTOR,
            }
            for hatch in self.townhalls:
                close_enemy = self.ground_enemies.closer_than(20, hatch.position)
                close_enemy_flying = self.flying_enemies.filter(
                    lambda unit: unit.type_id not in excluded_from_flying and unit.distance_to(hatch.position) < 30
                )
                if close_enemy and not self.close_enemies_to_base:
                    self.close_enemies_to_base = True
                if close_enemy_flying and not self.counter_attack_vs_flying:
                    self.counter_attack_vs_flying = True
