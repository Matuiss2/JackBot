"""All situational data are here"""
from sc2.constants import UnitTypeId

from sc2 import Race


class SituationalData:
    """This is the data container for all situational stuff"""

    def __init__(self):
        self.close_enemies_to_base = self.counter_attack_vs_flying = False

    def check_for_floating_buildings(self) -> bool:
        """Check if some terran wants to be funny with lifting up"""
        return bool(
            self.enemy_structures.flying
            and len(self.enemy_structures) == len(self.enemy_structures.flying)
            and self.time > 300
        )

    def check_for_proxy_buildings(self) -> bool:
        """Check if there are any proxy buildings"""
        return bool(
            self.enemy_structures.of_type({UnitTypeId.BARRACKS, UnitTypeId.GATEWAY, UnitTypeId.HATCHERY}).closer_than(
                75, self.start_location
            )
        )

    def check_for_rushes(self):
        """Got and adapted from SeeBot"""
        if self.enemy_race is Race.Terran:
            return (
                len(self.enemy_structures.of_type(UnitTypeId.BARRACKS)) > 2
                or not self.enemy_structures.of_type(UnitTypeId.REFINERY)
            ) and len(self.enemy_structures.of_type(UnitTypeId.COMMANDCENTER)) == 1
        if self.enemy_race is Race.Protoss:
            return (
                len(self.enemy_structures.of_type(UnitTypeId.GATEWAY)) != 1
                or not self.enemy_structures.of_type(UnitTypeId.ASSIMILATOR)
            ) and len(self.enemy_structures.of_type(UnitTypeId.NEXUS)) == 1
        return None

    def check_for_second_bases(self) -> bool:
        """Check if its a one base play"""
        return bool(
            self.overlords
            and not self.enemy_structures.of_type(
                {UnitTypeId.NEXUS, UnitTypeId.COMMANDCENTER, UnitTypeId.HATCHERY}
            ).closer_than(25, self.overlords.furthest_to(self.start_location))
            and self.time > 165
            and not self.check_for_proxy_buildings
        )

    def prepare_enemy_data_points(self):
        """Prepare data related to enemy units"""
        if self.enemies:
            excluded_from_flying = {
                UnitTypeId.DRONE,
                UnitTypeId.SCV,
                UnitTypeId.PROBE,
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
                close_enemy_flying = self.flying_enemies.exclude_type(excluded_from_flying).closer_than(
                    30, hatch.position
                )
                if close_enemy and not self.close_enemies_to_base:
                    self.close_enemies_to_base = True
                if close_enemy_flying and not self.counter_attack_vs_flying:
                    self.counter_attack_vs_flying = True
