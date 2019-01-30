"""All situational data are here"""
from sc2.constants import (
    ASSIMILATOR,
    BARRACKS,
    COMMANDCENTER,
    CORRUPTOR,
    DRONE,
    GATEWAY,
    HATCHERY,
    MEDIVAC,
    NEXUS,
    OBSERVER,
    OVERLORD,
    OVERSEER,
    PROBE,
    RAVEN,
    REFINERY,
    SCV,
    VIPER,
    WARPPRISM,
)

from sc2 import Race


class SituationalData:
    """This is the data container for all situational stuff"""

    def __init__(self):
        self.close_enemies_to_base = self.counter_attack_vs_flying = False

    def check_for_second_bases(self) -> bool:
        """Check if its a one base play"""
        return bool(
            self.overlords
            and not self.enemy_structures.of_type({NEXUS, COMMANDCENTER, HATCHERY}).closer_than(
                25, self.overlords.furthest_to(self.start_location)
            )
            and self.time > 165
            and not self.check_for_proxy_buildings
        )

    def check_for_proxy_buildings(self) -> bool:
        """Check if there are any proxy buildings"""
        return bool(self.enemy_structures.of_type({BARRACKS, GATEWAY, HATCHERY}).closer_than(75, self.start_location))

    def check_for_floating_buildings(self) -> bool:
        """Check if some terran wants to be funny with lifting up"""
        return bool(
            self.enemy_structures.flying
            and len(self.enemy_structures) == len(self.enemy_structures.flying)
            and self.time > 300
        )

    def prepare_enemy_data_points(self):
        """Prepare data related to enemy units"""
        if self.enemies:
            excluded_from_flying = {
                DRONE,
                SCV,
                PROBE,
                OVERLORD,
                OVERSEER,
                RAVEN,
                OBSERVER,
                WARPPRISM,
                MEDIVAC,
                VIPER,
                CORRUPTOR,
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

    def check_for_rushes(self):
        """Got and adapted from SeeBot"""
        if self.enemy_race is Race.Terran:
            return len(self.enemy_structures.of_type(BARRACKS)) not in (1, 2) or not self.enemy_structures.of_type(
                REFINERY
            )
        if self.enemy_race is Race.Protoss:
            return len(self.enemy_structures.of_type(GATEWAY)) != 1 or not self.enemy_structures.of_type(ASSIMILATOR)
        return None
