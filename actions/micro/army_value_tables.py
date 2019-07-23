"""Everything related to army value tables go here"""
import numpy as np
from sc2.constants import UnitTypeId


def general_calculation(table, targets):
    """
    Returns the sum of all targets unit values, if the id is unknown, add it as value 1
    Parameters
    ----------
    table: Value table based on our unit type and their race
    targets: Close enemy threats

    Returns
    -------
    The final enemy army value
    """
    total = 0
    for enemy in targets:
        table.setdefault(enemy.type_id, 1)
        total += table[enemy.type_id]
    return total


class EnemyArmyValue:
    """Separate the enemy army values by unit and race
    (can be improved by tuning and considering upgrades, position, distance...might be a little to hard)"""

    massive_counter = 2.5
    counter = 1.75
    advantage = 1.2
    normal = 1
    countered = 0.5
    massive_countered = 0.2
    worker = 0.01

    def battling_force_value(self, unit_position, zvalue, hvalue, uvalue):
        """
        Calculate value for our army that is in battle
        Parameters
        ----------
        unit_position: The position of the unit in question
        zvalue: Chosen zergling value
        hvalue: Chosen hydras value
        uvalue: Chosen ultras value

        Returns
        -------
        The sum of all values(quantity * chosen values)
        """
        return np.sum(
            np.array(
                [
                    len(self.main.zerglings.closer_than(13, unit_position)),
                    len(self.main.hydras.closer_than(13, unit_position)),
                    len(self.main.ultralisks.closer_than(13, unit_position)),
                ]
            )
            * np.array([zvalue, hvalue, uvalue])
        )

    def enemy_value_protoss(self, unit, target_group):
        """
        Calculates the right enemy value based on our unit type vs protoss
        Parameters
        ----------
        unit: Our units
        target_group: Our targets

        Returns
        -------
        The sum of all values(quantity * chosen values) based on our unit type
        """
        if unit.type_id == UnitTypeId.ZERGLING:
            return self.protoss_value_for_zerglings(target_group)
        if unit.type_id == UnitTypeId.HYDRALISK:
            return self.protoss_value_for_hydralisks(target_group)
        return self.protoss_value_for_ultralisks(target_group)

    def enemy_value_terran(self, unit, target_group):
        """
        Calculates the right enemy value based on our unit type vs terran
        Parameters
        ----------
        unit: Our units
        target_group: Our targets

        Returns
        -------
        The sum of all values(quantity * chosen values) based on our unit type
        """
        if unit.type_id == UnitTypeId.ZERGLING:
            return self.terran_value_for_zerglings(target_group)
        if unit.type_id == UnitTypeId.HYDRALISK:
            return self.terran_value_for_hydralisks(target_group)
        return self.terran_value_for_ultralisks(target_group)

    def enemy_value_zerg(self, unit, target_group):
        """
        Calculates the right enemy value based on our unit type vs zerg
        Parameters
        ----------
        unit: Our units
        target_group: Our targets

        Returns
        -------
        The sum of all values(quantity * chosen values) based on our unit type
        """
        if unit.type_id == UnitTypeId.ZERGLING:
            return self.zerg_value_for_zerglings(target_group)
        if unit.type_id == UnitTypeId.HYDRALISK:
            return self.zerg_value_for_hydralisk(target_group)
        return self.zerg_value_for_ultralisks(target_group)

    def gathering_force_value(self, zvalue, hvalue, uvalue):
        """
        Calculate value for our army that is gathering on the rally point
        Parameters
        ----------
        zvalue: Chosen zergling value
        hvalue: Chosen hydras value
        uvalue: Chosen ultras value

        Returns
        -------
        The sum of all values(quantity * chosen values)
        """
        return np.sum(
            np.array([len(self.main.zerglings.ready), len(self.main.hydras.ready), len(self.main.ultralisks.ready)])
            * np.array([zvalue, hvalue, uvalue])
        )

    def protoss_value_for_hydralisks(self, combined_enemies):
        """
        Calculate the enemy army value for hydralisks vs protoss
        Parameters
        ----------
        combined_enemies: All enemies in range

        Returns
        -------
        The final enemy army value for hydralisks vs protoss after the calculations
        """
        protoss_as_hydralisks_table = {
            UnitTypeId.PHOENIX: self.countered,
            UnitTypeId.ORACLE: self.countered,
            UnitTypeId.COLOSSUS: self.counter,
            UnitTypeId.ADEPT: self.normal,
            UnitTypeId.ARCHON: self.advantage,
            UnitTypeId.STALKER: self.normal,
            UnitTypeId.DARKTEMPLAR: self.countered,
            UnitTypeId.PHOTONCANNON: self.counter,
            UnitTypeId.ZEALOT: self.countered,
            UnitTypeId.SENTRY: self.massive_countered,
            UnitTypeId.PROBE: self.worker,
            UnitTypeId.HIGHTEMPLAR: self.countered,
            UnitTypeId.CARRIER: self.massive_counter,
            UnitTypeId.DISRUPTOR: self.advantage,
            UnitTypeId.IMMORTAL: self.counter,
            UnitTypeId.TEMPEST: self.normal,
            UnitTypeId.VOIDRAY: self.countered,
            UnitTypeId.MOTHERSHIP: self.normal,
        }
        return general_calculation(protoss_as_hydralisks_table, combined_enemies)

    def protoss_value_for_ultralisks(self, combined_enemies):
        """
        Calculate the enemy army value for ultralisks vs protoss
        Parameters
        ----------
        combined_enemies: All enemies in range

        Returns
        -------
        The final enemy army value for ultralisks vs protoss after the calculations
        """
        protoss_as_ultralisks_table = {
            UnitTypeId.COLOSSUS: self.countered,
            UnitTypeId.ADEPT: self.countered,
            UnitTypeId.ARCHON: self.advantage,
            UnitTypeId.STALKER: self.countered,
            UnitTypeId.DARKTEMPLAR: self.countered,
            UnitTypeId.PHOTONCANNON: self.normal,
            UnitTypeId.ZEALOT: self.normal,
            UnitTypeId.SENTRY: self.countered,
            UnitTypeId.PROBE: self.worker,
            UnitTypeId.HIGHTEMPLAR: self.massive_countered,
            UnitTypeId.DISRUPTOR: self.normal,
            UnitTypeId.IMMORTAL: self.massive_counter,
        }
        return general_calculation(protoss_as_ultralisks_table, combined_enemies)

    def protoss_value_for_zerglings(self, combined_enemies):
        """
        Calculate the enemy army value for zerglings vs protoss
        Parameters
        ----------
        combined_enemies: All enemies in range

        Returns
        -------
        The final enemy army value for zerglings vs protoss after the calculations
        """
        protoss_as_zergling_table = {
            UnitTypeId.COLOSSUS: self.massive_counter,
            UnitTypeId.ADEPT: self.advantage,
            UnitTypeId.ARCHON: self.counter,
            UnitTypeId.STALKER: self.countered,
            UnitTypeId.DARKTEMPLAR: self.normal,
            UnitTypeId.PHOTONCANNON: self.counter,
            UnitTypeId.ZEALOT: self.advantage,
            UnitTypeId.SENTRY: self.countered,
            UnitTypeId.PROBE: self.worker,
            UnitTypeId.HIGHTEMPLAR: self.countered,
            UnitTypeId.DISRUPTOR: self.counter,
            UnitTypeId.IMMORTAL: self.advantage,
        }
        return general_calculation(protoss_as_zergling_table, combined_enemies)

    def terran_value_for_hydralisks(self, combined_enemies):
        """
        Calculate the enemy army value for hydralisks vs terran
        Parameters
        ----------
        combined_enemies: All enemies in range

        Returns
        -------
        The final enemy army value for hydralisks vs terran after the calculations
        """
        terran_as_hydralisk_table = {
            UnitTypeId.BUNKER: self.normal,
            UnitTypeId.HELLION: self.countered,
            UnitTypeId.HELLIONTANK: self.advantage,
            UnitTypeId.CYCLONE: self.normal,
            UnitTypeId.GHOST: self.normal,
            UnitTypeId.MARAUDER: self.counter,
            UnitTypeId.MARINE: self.countered,
            UnitTypeId.REAPER: self.countered,
            UnitTypeId.SCV: self.worker,
            UnitTypeId.SIEGETANKSIEGED: self.massive_counter,
            UnitTypeId.SIEGETANK: self.advantage,
            UnitTypeId.THOR: self.normal,
            UnitTypeId.VIKINGASSAULT: self.countered,
            UnitTypeId.BANSHEE: self.countered,
            UnitTypeId.BATTLECRUISER: self.normal,
            UnitTypeId.LIBERATOR: self.counter,
            UnitTypeId.MEDIVAC: self.massive_countered,
            UnitTypeId.VIKINGFIGHTER: self.massive_countered,
        }
        return general_calculation(terran_as_hydralisk_table, combined_enemies)

    def terran_value_for_ultralisks(self, combined_enemies):
        """
        Calculate the enemy army value for ultralisks vs terran
        Parameters
        ----------
        combined_enemies: All enemies in range

        Returns
        -------
        The final enemy army value for ultralisks vs terran after the calculations
        """
        terran_as_ultralisk_table = {
            UnitTypeId.BUNKER: self.countered,
            UnitTypeId.HELLION: self.massive_countered,
            UnitTypeId.HELLIONTANK: self.countered,
            UnitTypeId.CYCLONE: self.countered,
            UnitTypeId.GHOST: self.counter,
            UnitTypeId.MARAUDER: self.advantage,
            UnitTypeId.MARINE: self.massive_countered,
            UnitTypeId.REAPER: self.massive_countered,
            UnitTypeId.SCV: self.worker,
            UnitTypeId.SIEGETANKSIEGED: self.counter,
            UnitTypeId.SIEGETANK: self.countered,
            UnitTypeId.THOR: self.counter,
            UnitTypeId.VIKINGASSAULT: self.countered,
        }
        return general_calculation(terran_as_ultralisk_table, combined_enemies)

    def terran_value_for_zerglings(self, combined_enemies):
        """
        Calculate the enemy army value for zerglings vs terran
        Parameters
        ----------
        combined_enemies: All enemies in range

        Returns
        -------
        The final enemy army value for zerglings vs terran after the calculations
        """
        terran_as_zergling_table = {
            UnitTypeId.BUNKER: self.counter,
            UnitTypeId.HELLION: self.counter,
            UnitTypeId.HELLIONTANK: self.massive_counter,
            UnitTypeId.CYCLONE: self.countered,
            UnitTypeId.GHOST: self.countered,
            UnitTypeId.MARAUDER: self.countered,
            UnitTypeId.MARINE: self.normal,
            UnitTypeId.REAPER: self.countered,
            UnitTypeId.SCV: self.worker,
            UnitTypeId.SIEGETANKSIEGED: self.massive_counter,
            UnitTypeId.SIEGETANK: self.advantage,
            UnitTypeId.THOR: self.countered,
            UnitTypeId.VIKINGASSAULT: self.countered,
        }
        return general_calculation(terran_as_zergling_table, combined_enemies)

    def zerg_value_for_hydralisk(self, combined_enemies):
        """
        Calculate the enemy army value for hydralisks vs zerg
        Parameters
        ----------
        combined_enemies: All enemies in range

        Returns
        -------
        The final enemy army value for hydralisks vs zerg after the calculations
        """
        zerg_as_hydralisk_table = {
            UnitTypeId.LARVA: 0,
            UnitTypeId.QUEEN: self.normal,
            UnitTypeId.ZERGLING: self.normal,
            UnitTypeId.BANELING: self.counter,
            UnitTypeId.ROACH: self.normal,
            UnitTypeId.RAVAGER: self.normal,
            UnitTypeId.HYDRALISK: self.normal,
            UnitTypeId.LURKERMP: self.countered,
            UnitTypeId.DRONE: self.worker,
            UnitTypeId.LURKERMPBURROWED: self.massive_counter,
            UnitTypeId.INFESTOR: self.countered,
            UnitTypeId.INFESTEDTERRAN: self.countered,
            UnitTypeId.INFESTEDTERRANSEGG: self.massive_countered,
            UnitTypeId.SWARMHOSTMP: self.massive_countered,
            UnitTypeId.LOCUSTMP: self.normal,
            UnitTypeId.ULTRALISK: self.massive_counter,
            UnitTypeId.SPINECRAWLER: self.normal,
            UnitTypeId.LOCUSTMPFLYING: self.countered,
            UnitTypeId.OVERLORD: 0,
            UnitTypeId.OVERSEER: 0,
            UnitTypeId.MUTALISK: self.countered,
            UnitTypeId.CORRUPTOR: 0,
            UnitTypeId.VIPER: self.countered,
            UnitTypeId.BROODLORD: self.normal,
            UnitTypeId.BROODLING: self.countered,
        }
        return general_calculation(zerg_as_hydralisk_table, combined_enemies)

    def zerg_value_for_ultralisks(self, combined_enemies):
        """
        Calculate the enemy army value for ultralisks vs zerg
        Parameters
        ----------
        combined_enemies: All enemies in range

        Returns
        -------
        The final enemy army value for ultralisks vs zerg after the calculations
        """
        zerg_as_ultralisk_table = {
            UnitTypeId.LARVA: 0,
            UnitTypeId.QUEEN: self.countered,
            UnitTypeId.ZERGLING: self.massive_countered,
            UnitTypeId.BANELING: self.massive_countered,
            UnitTypeId.ROACH: self.countered,
            UnitTypeId.RAVAGER: self.countered,
            UnitTypeId.HYDRALISK: self.countered,
            UnitTypeId.LURKERMP: self.countered,
            UnitTypeId.DRONE: self.worker,
            UnitTypeId.LURKERMPBURROWED: self.counter,
            UnitTypeId.INFESTOR: self.countered,
            UnitTypeId.INFESTEDTERRAN: self.countered,
            UnitTypeId.INFESTEDTERRANSEGG: self.massive_countered,
            UnitTypeId.SWARMHOSTMP: self.massive_countered,
            UnitTypeId.LOCUSTMP: self.counter,
            UnitTypeId.ULTRALISK: self.normal,
            UnitTypeId.SPINECRAWLER: self.normal,
            UnitTypeId.BROODLING: self.countered,
        }
        return general_calculation(zerg_as_ultralisk_table, combined_enemies)

    def zerg_value_for_zerglings(self, combined_enemies):
        """
        Calculate the enemy army value for zerglings vs zerg
        Parameters
        ----------
        combined_enemies: All enemies in range

        Returns
        -------
        The final enemy army value for zerglings vs zerg after the calculations
        """
        zerg_as_zergling_table = {
            UnitTypeId.LARVA: 0,
            UnitTypeId.QUEEN: self.normal,
            UnitTypeId.ZERGLING: self.normal,
            UnitTypeId.BANELING: self.advantage,
            UnitTypeId.ROACH: self.normal,
            UnitTypeId.RAVAGER: self.normal,
            UnitTypeId.HYDRALISK: self.normal,
            UnitTypeId.LURKERMP: self.normal,
            UnitTypeId.DRONE: self.worker,
            UnitTypeId.LURKERMPBURROWED: self.massive_counter,
            UnitTypeId.INFESTOR: self.countered,
            UnitTypeId.INFESTEDTERRAN: self.normal,
            UnitTypeId.INFESTEDTERRANSEGG: self.massive_countered,
            UnitTypeId.SWARMHOSTMP: self.countered,
            UnitTypeId.LOCUSTMP: self.counter,
            UnitTypeId.ULTRALISK: self.massive_counter,
            UnitTypeId.SPINECRAWLER: self.counter,
            UnitTypeId.BROODLING: self.normal,
        }
        return general_calculation(zerg_as_zergling_table, combined_enemies)
