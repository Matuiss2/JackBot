"""Everything related to handling proxies are here"""
from sc2.constants import UnitTypeId


class DefendProxies:
    """Needs improvements on the quantity, also on the follow up(its overly defensive)"""

    def __init__(self, main):
        self.main = main
        self.rush_buildings = None

    async def should_handle(self):
        """Requirements to run handle(can be improved, hard-coding the trigger distance is way to exploitable)"""
        if self.main.townhalls:
            self.rush_buildings = self.main.enemy_structures.exclude_type(
                {UnitTypeId.AUTOTURRET, UnitTypeId.BARRACKS, UnitTypeId.GATEWAY}
            ).closer_than(50, self.main.furthest_townhall_to_center)
        return (
            self.rush_buildings
            and self.main.time <= 270
            and self.main.drone_amount >= 15
            and not self.main.ground_enemies
        )

    async def handle(self):
        """Send workers aggressively to handle the near proxy / cannon rush, need to learn how to get the max
         surface area possible when attacking the buildings"""
        available = self.main.drones.filter(lambda x: x.is_collecting and not x.is_attacking)
        for worker in self.main.enemies.of_type({UnitTypeId.PROBE, UnitTypeId.DRONE, UnitTypeId.SCV}).filter(
            lambda unit: any(unit.distance_to(our_building) <= 50 for our_building in self.main.structures)
        ):
            if not self.is_being_attacked(worker) and available:
                self.main.add_action(available.closest_to(worker).attack(worker))
        attacking_buildings = self.rush_buildings.of_type(
            {UnitTypeId.SPINECRAWLER, UnitTypeId.PHOTONCANNON, UnitTypeId.BUNKER, UnitTypeId.PLANETARYFORTRESS}
        )
        not_attacking_buildings = self.rush_buildings - attacking_buildings
        if attacking_buildings:
            available = self.main.drones.filter(lambda x: x.order_target not in [y.tag for y in attacking_buildings])
            self.pull_drones(attacking_buildings, available)
        if not_attacking_buildings:
            self.pull_drones(not_attacking_buildings, available)

    def is_being_attacked(self, unit):
        """
        Calculates how often our units are attacking the given enemy unit

        Parameters
        ----------
        unit: Enemy unit that is being targeted

        Returns
        -------
        An integer value that corresponds to how many of our units are attacking the given target
        """

        return len(
            [1 for attacker in self.main.units.filter(lambda x: x.is_attacking) if attacker.order_target == unit.tag]
        )

    def pull_drones(self, mode, available):
        """Pull 3 drones to destroy the proxy building"""
        for target in mode:
            if self.is_being_attacked(target) < 3 and available:
                self.main.add_action(available.closest_to(target).attack(target))
