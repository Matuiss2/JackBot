"""Everything related to army value tables go here"""
import numpy as np
from sc2.constants import (
    ADEPT,
    ARCHON,
    BANELING,
    BANSHEE,
    BATTLECRUISER,
    BROODLING,
    BROODLORD,
    BUNKER,
    CARRIER,
    CYCLONE,
    COLOSSUS,
    CORRUPTOR,
    DARKTEMPLAR,
    DISRUPTOR,
    DRONE,
    GHOST,
    HELLION,
    HELLIONTANK,
    HYDRALISK,
    HIGHTEMPLAR,
    IMMORTAL,
    LARVA,
    INFESTEDTERRAN,
    INFESTEDTERRANSEGG,
    INFESTOR,
    LIBERATOR,
    LOCUSTMP,
    LOCUSTMPFLYING,
    LURKERMP,
    LURKERMPBURROWED,
    MARAUDER,
    MARINE,
    MEDIVAC,
    MOTHERSHIP,
    MUTALISK,
    ORACLE,
    OVERLORD,
    OVERSEER,
    PHOENIX,
    PHOTONCANNON,
    PROBE,
    QUEEN,
    RAVAGER,
    REAPER,
    ROACH,
    SCV,
    SENTRY,
    SIEGETANK,
    SIEGETANKSIEGED,
    SPINECRAWLER,
    STALKER,
    SWARMHOSTMP,
    TEMPEST,
    THOR,
    ULTRALISK,
    VIKINGASSAULT,
    VIKINGFIGHTER,
    VIPER,
    VOIDRAY,
    ZEALOT,
    ZERGLING,
)


def general_calculation(table, targets):
    """Returns the sum of all targets unit values, if the id is unknown, add it as value 1"""
    total = 0
    for enemy in targets:
        table.setdefault(enemy.type_id, 1)
        total += table[enemy.type_id]
    return total


class EnemyArmyValue:
    """Separate the enemy army values by unit and race"""

    massive_counter = 2.5
    counter = 1.75
    advantage = 1.2
    normal = 1
    countered = 0.5
    massive_countered = 0.2
    worker = 0.05

    def protoss_value_for_zerglings(self, combined_enemies):
        """Calculate the enemy army value for zerglings vs protoss"""
        protoss_as_zergling_table = {
            COLOSSUS: self.massive_counter,
            ADEPT: self.advantage,
            ARCHON: self.counter,
            STALKER: self.countered,
            DARKTEMPLAR: self.normal,
            PHOTONCANNON: self.counter,
            ZEALOT: self.advantage,
            SENTRY: self.countered,
            PROBE: self.worker,
            HIGHTEMPLAR: self.countered,
            DISRUPTOR: self.counter,
            IMMORTAL: self.advantage,
        }
        return general_calculation(protoss_as_zergling_table, combined_enemies)

    def protoss_value_for_hydralisks(self, combined_enemies):
        """Calculate the enemy army value for hydralisks vs protoss"""
        protoss_as_hydralisks_table = {
            PHOENIX: self.countered,
            ORACLE: self.countered,
            COLOSSUS: self.counter,
            ADEPT: self.normal,
            ARCHON: self.advantage,
            STALKER: self.normal,
            DARKTEMPLAR: self.countered,
            PHOTONCANNON: self.counter,
            ZEALOT: self.countered,
            SENTRY: self.massive_countered,
            PROBE: self.worker,
            HIGHTEMPLAR: self.countered,
            CARRIER: self.massive_counter,
            DISRUPTOR: self.advantage,
            IMMORTAL: self.counter,
            TEMPEST: self.normal,
            VOIDRAY: self.countered,
            MOTHERSHIP: self.normal,
        }
        return general_calculation(protoss_as_hydralisks_table, combined_enemies)

    def protoss_value_for_ultralisks(self, combined_enemies):
        """Calculate the enemy army value for ultralisks vs protoss"""
        protoss_as_ultralisks_table = {
            COLOSSUS: self.countered,
            ADEPT: self.countered,
            ARCHON: self.advantage,
            STALKER: self.countered,
            DARKTEMPLAR: self.countered,
            PHOTONCANNON: self.normal,
            ZEALOT: self.normal,
            SENTRY: self.countered,
            PROBE: self.worker,
            HIGHTEMPLAR: self.massive_countered,
            DISRUPTOR: self.normal,
            IMMORTAL: self.massive_counter,
        }
        return general_calculation(protoss_as_ultralisks_table, combined_enemies)

    def terran_value_for_zerglings(self, combined_enemies):
        """Calculate the enemy army value for zerglings vs terran"""
        terran_as_zergling_table = {
            BUNKER: self.counter,
            HELLION: self.counter,
            HELLIONTANK: self.massive_counter,
            CYCLONE: self.countered,
            GHOST: self.countered,
            MARAUDER: self.countered,
            MARINE: self.normal,
            REAPER: self.countered,
            SCV: self.worker,
            SIEGETANKSIEGED: self.massive_counter,
            SIEGETANK: self.advantage,
            THOR: self.countered,
            VIKINGASSAULT: self.countered,
        }
        return general_calculation(terran_as_zergling_table, combined_enemies)

    def terran_value_for_hydralisks(self, combined_enemies):
        """Calculate the enemy army value for hydralisks vs terran"""
        terran_as_hydralisk_table = {
            BUNKER: self.normal,
            HELLION: self.countered,
            HELLIONTANK: self.advantage,
            CYCLONE: self.normal,
            GHOST: self.normal,
            MARAUDER: self.counter,
            MARINE: self.countered,
            REAPER: self.countered,
            SCV: self.worker,
            SIEGETANKSIEGED: self.massive_counter,
            SIEGETANK: self.advantage,
            THOR: self.normal,
            VIKINGASSAULT: self.countered,
            BANSHEE: self.countered,
            BATTLECRUISER: self.normal,
            LIBERATOR: self.counter,
            MEDIVAC: self.massive_countered,
            VIKINGFIGHTER: self.massive_countered,
        }
        return general_calculation(terran_as_hydralisk_table, combined_enemies)

    def terran_value_for_ultralisks(self, combined_enemies):
        """Calculate the enemy army value for ultralisks vs terran"""
        terran_as_ultralisk_table = {
            BUNKER: self.countered,
            HELLION: self.massive_countered,
            HELLIONTANK: self.countered,
            CYCLONE: self.countered,
            GHOST: self.counter,
            MARAUDER: self.advantage,
            MARINE: self.massive_countered,
            REAPER: self.massive_countered,
            SCV: self.worker,
            SIEGETANKSIEGED: self.counter,
            SIEGETANK: self.countered,
            THOR: self.counter,
            VIKINGASSAULT: self.countered,
        }
        return general_calculation(terran_as_ultralisk_table, combined_enemies)

    def zerg_value_for_zerglings(self, combined_enemies):
        """Calculate the enemy army value for zerglings vs zerg"""
        zerg_as_zergling_table = {
            LARVA: 0,
            QUEEN: self.normal,
            ZERGLING: self.normal,
            BANELING: self.advantage,
            ROACH: self.normal,
            RAVAGER: self.normal,
            HYDRALISK: self.normal,
            LURKERMP: self.normal,
            DRONE: self.worker,
            LURKERMPBURROWED: self.massive_counter,
            INFESTOR: self.countered,
            INFESTEDTERRAN: self.normal,
            INFESTEDTERRANSEGG: self.massive_countered,
            SWARMHOSTMP: self.countered,
            LOCUSTMP: self.counter,
            ULTRALISK: self.massive_counter,
            SPINECRAWLER: self.counter,
            BROODLING: self.normal,
        }
        return general_calculation(zerg_as_zergling_table, combined_enemies)

    def zerg_value_for_hydralisk(self, combined_enemies):
        """Calculate the enemy army value for hydralisks vs zerg"""
        zerg_as_hydralisk_table = {
            LARVA: 0,
            QUEEN: self.normal,
            ZERGLING: self.normal,
            BANELING: self.counter,
            ROACH: self.normal,
            RAVAGER: self.normal,
            HYDRALISK: self.normal,
            LURKERMP: self.countered,
            DRONE: self.worker,
            LURKERMPBURROWED: self.massive_counter,
            INFESTOR: self.countered,
            INFESTEDTERRAN: self.countered,
            INFESTEDTERRANSEGG: self.massive_countered,
            SWARMHOSTMP: self.massive_countered,
            LOCUSTMP: self.normal,
            ULTRALISK: self.massive_counter,
            SPINECRAWLER: self.normal,
            LOCUSTMPFLYING: self.countered,
            OVERLORD: 0,
            OVERSEER: 0,
            MUTALISK: self.countered,
            CORRUPTOR: 0,
            VIPER: self.countered,
            BROODLORD: self.normal,
            BROODLING: self.countered,
        }
        return general_calculation(zerg_as_hydralisk_table, combined_enemies)

    def zerg_value_for_ultralisks(self, combined_enemies):
        """Calculate the enemy army value for ultralisks vs zerg"""
        zerg_as_ultralisk_table = {
            LARVA: 0,
            QUEEN: self.countered,
            ZERGLING: self.massive_countered,
            BANELING: self.massive_countered,
            ROACH: self.countered,
            RAVAGER: self.countered,
            HYDRALISK: self.countered,
            LURKERMP: self.countered,
            DRONE: self.worker,
            LURKERMPBURROWED: self.counter,
            INFESTOR: self.countered,
            INFESTEDTERRAN: self.countered,
            INFESTEDTERRANSEGG: self.massive_countered,
            SWARMHOSTMP: self.massive_countered,
            LOCUSTMP: self.counter,
            ULTRALISK: self.normal,
            SPINECRAWLER: self.normal,
            BROODLING: self.countered,
        }
        return general_calculation(zerg_as_ultralisk_table, combined_enemies)

    def enemy_value_terran(self, unit, target_group):
        """Returns the right enemy value based on the unit vs terran"""
        if unit.type_id == ZERGLING:
            return self.terran_value_for_zerglings(target_group)
        if unit.type_id == HYDRALISK:
            return self.terran_value_for_hydralisks(target_group)
        return self.terran_value_for_ultralisks(target_group)

    def enemy_value_protoss(self, unit, target_group):
        """Returns the right enemy value based on the unit vs protoss"""
        if unit.type_id == ZERGLING:
            return self.protoss_value_for_zerglings(target_group)
        if unit.type_id == HYDRALISK:
            return self.protoss_value_for_hydralisks(target_group)
        return self.protoss_value_for_ultralisks(target_group)

    def enemy_value_zerg(self, unit, target_group):
        """Returns the right enemy value based on the unit vs zerg"""
        if unit.type_id == ZERGLING:
            return self.zerg_value_for_zerglings(target_group)
        if unit.type_id == HYDRALISK:
            return self.zerg_value_for_hydralisk(target_group)
        return self.zerg_value_for_ultralisks(target_group)

    def battling_force_value(self, unit_position, zvalue, hvalue, uvalue):
        """Returns the right value for our army that is in battle"""
        local_controller = self.controller
        return np.sum(
            np.array(
                [
                    len(local_controller.zerglings.closer_than(13, unit_position)),
                    len(local_controller.ultralisks.closer_than(13, unit_position)),
                    len(local_controller.hydras.closer_than(13, unit_position)),
                ]
            )
            * np.array([zvalue, hvalue, uvalue])
        )

    def gathering_force_value(self, zvalue, hvalue, uvalue):
        """Returns the right value for our army that is gathering"""
        local_controller = self.controller
        return np.sum(
            np.array(
                [
                    len(local_controller.zerglings.ready),
                    len(local_controller.hydras.ready),
                    len(local_controller.ultralisks.ready),
                ]
            )
            * np.array([zvalue, hvalue, uvalue])
        )
