"""Everything related to army value tables go here"""
import numpy as np
from sc2.constants import UnitTypeId


def calculate_army_value(table, targets):
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
    enemy_army_value = 0
    for enemy in targets:
        table.setdefault(enemy.type_id, 1)
        enemy_army_value += table[enemy.type_id]
    return enemy_army_value


class ArmyValues:
    """Separate the enemy army values by unit and race
    (can be improved by tuning and considering upgrades, position, distance...might be a little to hard)"""

    big_counter = 2.5
    counter = 1.75
    enemy_advantage = 1.2
    even = 1
    countering = 0.5
    countering_a_lot = 0.2
    worker = 0.01

    def combatants_value(self, unit_position, zvalue, hvalue, uvalue):
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

    def enemy_protoss_value(self, unit, target_group):
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

    def enemy_terran_value(self, unit, target_group):
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

    def enemy_zerg_value(self, unit, target_group):
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
        hydralisks_vs_protoss_table = {
            UnitTypeId.PHOENIX: self.countering,
            UnitTypeId.ORACLE: self.countering,
            UnitTypeId.COLOSSUS: self.counter,
            UnitTypeId.ADEPT: self.even,
            UnitTypeId.ARCHON: self.enemy_advantage,
            UnitTypeId.STALKER: self.even,
            UnitTypeId.DARKTEMPLAR: self.countering,
            UnitTypeId.PHOTONCANNON: self.counter,
            UnitTypeId.ZEALOT: self.countering,
            UnitTypeId.SENTRY: self.countering_a_lot,
            UnitTypeId.PROBE: self.worker,
            UnitTypeId.HIGHTEMPLAR: self.countering,
            UnitTypeId.CARRIER: self.big_counter,
            UnitTypeId.DISRUPTOR: self.enemy_advantage,
            UnitTypeId.IMMORTAL: self.counter,
            UnitTypeId.TEMPEST: self.even,
            UnitTypeId.VOIDRAY: self.countering,
            UnitTypeId.MOTHERSHIP: self.even,
        }
        return calculate_army_value(hydralisks_vs_protoss_table, combined_enemies)

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
        ultralisks_vs_protoss_table = {
            UnitTypeId.COLOSSUS: self.countering,
            UnitTypeId.ADEPT: self.countering,
            UnitTypeId.ARCHON: self.enemy_advantage,
            UnitTypeId.STALKER: self.countering,
            UnitTypeId.DARKTEMPLAR: self.countering,
            UnitTypeId.PHOTONCANNON: self.even,
            UnitTypeId.ZEALOT: self.even,
            UnitTypeId.SENTRY: self.countering,
            UnitTypeId.PROBE: self.worker,
            UnitTypeId.HIGHTEMPLAR: self.countering_a_lot,
            UnitTypeId.DISRUPTOR: self.even,
            UnitTypeId.IMMORTAL: self.big_counter,
        }
        return calculate_army_value(ultralisks_vs_protoss_table, combined_enemies)

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
        zerglings_vs_protoss_table = {
            UnitTypeId.COLOSSUS: self.big_counter,
            UnitTypeId.ADEPT: self.enemy_advantage,
            UnitTypeId.ARCHON: self.counter,
            UnitTypeId.STALKER: self.countering,
            UnitTypeId.DARKTEMPLAR: self.even,
            UnitTypeId.PHOTONCANNON: self.counter,
            UnitTypeId.ZEALOT: self.enemy_advantage,
            UnitTypeId.SENTRY: self.countering,
            UnitTypeId.PROBE: self.worker,
            UnitTypeId.HIGHTEMPLAR: self.countering,
            UnitTypeId.DISRUPTOR: self.counter,
            UnitTypeId.IMMORTAL: self.enemy_advantage,
        }
        return calculate_army_value(zerglings_vs_protoss_table, combined_enemies)

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
        hydralisks_vs_terran_table = {
            UnitTypeId.BUNKER: self.even,
            UnitTypeId.HELLION: self.countering,
            UnitTypeId.HELLIONTANK: self.enemy_advantage,
            UnitTypeId.CYCLONE: self.even,
            UnitTypeId.GHOST: self.even,
            UnitTypeId.MARAUDER: self.counter,
            UnitTypeId.MARINE: self.countering,
            UnitTypeId.REAPER: self.countering,
            UnitTypeId.SCV: self.worker,
            UnitTypeId.SIEGETANKSIEGED: self.big_counter,
            UnitTypeId.SIEGETANK: self.enemy_advantage,
            UnitTypeId.THOR: self.even,
            UnitTypeId.VIKINGASSAULT: self.countering,
            UnitTypeId.BANSHEE: self.countering,
            UnitTypeId.BATTLECRUISER: self.even,
            UnitTypeId.LIBERATOR: self.counter,
            UnitTypeId.MEDIVAC: self.countering_a_lot,
            UnitTypeId.VIKINGFIGHTER: self.countering_a_lot,
        }
        return calculate_army_value(hydralisks_vs_terran_table, combined_enemies)

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
        ultralisks_vs_terran_table = {
            UnitTypeId.BUNKER: self.countering,
            UnitTypeId.HELLION: self.countering_a_lot,
            UnitTypeId.HELLIONTANK: self.countering,
            UnitTypeId.CYCLONE: self.countering,
            UnitTypeId.GHOST: self.counter,
            UnitTypeId.MARAUDER: self.enemy_advantage,
            UnitTypeId.MARINE: self.countering_a_lot,
            UnitTypeId.REAPER: self.countering_a_lot,
            UnitTypeId.SCV: self.worker,
            UnitTypeId.SIEGETANKSIEGED: self.counter,
            UnitTypeId.SIEGETANK: self.countering,
            UnitTypeId.THOR: self.counter,
            UnitTypeId.VIKINGASSAULT: self.countering,
        }
        return calculate_army_value(ultralisks_vs_terran_table, combined_enemies)

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
        zerglings_vs_terran_table = {
            UnitTypeId.BUNKER: self.counter,
            UnitTypeId.HELLION: self.counter,
            UnitTypeId.HELLIONTANK: self.big_counter,
            UnitTypeId.CYCLONE: self.countering,
            UnitTypeId.GHOST: self.countering,
            UnitTypeId.MARAUDER: self.countering,
            UnitTypeId.MARINE: self.even,
            UnitTypeId.REAPER: self.countering,
            UnitTypeId.SCV: self.worker,
            UnitTypeId.SIEGETANKSIEGED: self.big_counter,
            UnitTypeId.SIEGETANK: self.enemy_advantage,
            UnitTypeId.THOR: self.countering,
            UnitTypeId.VIKINGASSAULT: self.countering,
        }
        return calculate_army_value(zerglings_vs_terran_table, combined_enemies)

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
        hydralisks_vs_zerg_table = {
            UnitTypeId.LARVA: 0,
            UnitTypeId.QUEEN: self.even,
            UnitTypeId.ZERGLING: self.even,
            UnitTypeId.BANELING: self.counter,
            UnitTypeId.ROACH: self.even,
            UnitTypeId.RAVAGER: self.even,
            UnitTypeId.HYDRALISK: self.even,
            UnitTypeId.LURKERMP: self.countering,
            UnitTypeId.DRONE: self.worker,
            UnitTypeId.LURKERMPBURROWED: self.big_counter,
            UnitTypeId.INFESTOR: self.countering,
            UnitTypeId.INFESTEDTERRAN: self.countering,
            UnitTypeId.INFESTEDTERRANSEGG: self.countering_a_lot,
            UnitTypeId.SWARMHOSTMP: self.countering_a_lot,
            UnitTypeId.LOCUSTMP: self.even,
            UnitTypeId.ULTRALISK: self.big_counter,
            UnitTypeId.SPINECRAWLER: self.even,
            UnitTypeId.LOCUSTMPFLYING: self.countering,
            UnitTypeId.OVERLORD: 0,
            UnitTypeId.OVERSEER: 0,
            UnitTypeId.MUTALISK: self.countering,
            UnitTypeId.CORRUPTOR: 0,
            UnitTypeId.VIPER: self.countering,
            UnitTypeId.BROODLORD: self.even,
            UnitTypeId.BROODLING: self.countering,
        }
        return calculate_army_value(hydralisks_vs_zerg_table, combined_enemies)

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
        ultralisks_vs_zerg_table = {
            UnitTypeId.LARVA: 0,
            UnitTypeId.QUEEN: self.countering,
            UnitTypeId.ZERGLING: self.countering_a_lot,
            UnitTypeId.BANELING: self.countering_a_lot,
            UnitTypeId.ROACH: self.countering,
            UnitTypeId.RAVAGER: self.countering,
            UnitTypeId.HYDRALISK: self.countering,
            UnitTypeId.LURKERMP: self.countering,
            UnitTypeId.DRONE: self.worker,
            UnitTypeId.LURKERMPBURROWED: self.counter,
            UnitTypeId.INFESTOR: self.countering,
            UnitTypeId.INFESTEDTERRAN: self.countering,
            UnitTypeId.INFESTEDTERRANSEGG: self.countering_a_lot,
            UnitTypeId.SWARMHOSTMP: self.countering_a_lot,
            UnitTypeId.LOCUSTMP: self.counter,
            UnitTypeId.ULTRALISK: self.even,
            UnitTypeId.SPINECRAWLER: self.even,
            UnitTypeId.BROODLING: self.countering,
        }
        return calculate_army_value(ultralisks_vs_zerg_table, combined_enemies)

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
        zerglings_vs_zerg_table = {
            UnitTypeId.LARVA: 0,
            UnitTypeId.QUEEN: self.even,
            UnitTypeId.ZERGLING: self.even,
            UnitTypeId.BANELING: self.enemy_advantage,
            UnitTypeId.ROACH: self.even,
            UnitTypeId.RAVAGER: self.even,
            UnitTypeId.HYDRALISK: self.even,
            UnitTypeId.LURKERMP: self.even,
            UnitTypeId.DRONE: self.worker,
            UnitTypeId.LURKERMPBURROWED: self.big_counter,
            UnitTypeId.INFESTOR: self.countering,
            UnitTypeId.INFESTEDTERRAN: self.even,
            UnitTypeId.INFESTEDTERRANSEGG: self.countering_a_lot,
            UnitTypeId.SWARMHOSTMP: self.countering,
            UnitTypeId.LOCUSTMP: self.counter,
            UnitTypeId.ULTRALISK: self.big_counter,
            UnitTypeId.SPINECRAWLER: self.counter,
            UnitTypeId.BROODLING: self.even,
        }
        return calculate_army_value(zerglings_vs_zerg_table, combined_enemies)
