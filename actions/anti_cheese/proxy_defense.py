"""Everything related to handling proxies are here"""
from sc2.constants import UnitTypeId


class ProxyDefense:
    """Needs improvements on the quantity, also on the follow up(its overly defensive)"""

    def __init__(self, main):
        self.main = main
        self.proxy_buildings = None
        self.atk_b = {UnitTypeId.BUNKER, UnitTypeId.PHOTONCANNON, UnitTypeId.PLANETARYFORTRESS, UnitTypeId.SPINECRAWLER}
        self.enemy_basic_production = {UnitTypeId.BARRACKS, UnitTypeId.GATEWAY}
        self.worker_types = {UnitTypeId.DRONE, UnitTypeId.PROBE, UnitTypeId.SCV}

    async def should_handle(self):
        """Requirements to run handle(can be improved, hard-coding the trigger distance is way to exploitable)"""
        if not self.main.iteration % 10:
            return False
        if self.main.townhalls:
            self.proxy_buildings = self.main.enemy_structures.exclude_type(self.enemy_basic_production).closer_than(
                50, self.main.furthest_townhall_to_center
            )
        return (
            self.proxy_buildings
            and self.main.time <= 270
            and self.main.drone_amount >= 15
            and not self.main.ground_enemies
        )

    async def handle(self):
        """Send workers aggressively to handle the near proxy / cannon rush, need to learn how to get the max
         surface area possible when attacking the buildings"""
        drone_force = self.main.drones.filter(lambda x: x.is_collecting and not x.is_attacking)
        if drone_force:
            for enemy_worker in self.main.enemies.of_type(self.worker_types).filter(
                lambda unit: any(unit.distance_to(our_building) <= 50 for our_building in self.main.structures)
            ):
                if not self.is_being_attacked(enemy_worker):
                    self.main.add_action(drone_force.closest_to(enemy_worker).attack(enemy_worker))
        shooter_buildings = self.proxy_buildings.of_type(self.atk_b)
        support_buildings = self.proxy_buildings - shooter_buildings  # like pylons
        if shooter_buildings:
            drone_force = self.main.drones.filter(lambda x: x.order_target not in [y.tag for y in shooter_buildings])
            self.pull_drones(shooter_buildings, drone_force)
        if support_buildings:
            self.pull_drones(support_buildings, drone_force)

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
            ["" for attacker in self.main.units.filter(lambda x: x.is_attacking) if attacker.order_target == unit.tag]
        )

    def pull_drones(self, selected_building_targets, available_drone_force):
        """Pull 3 drones to destroy the proxy building"""
        if available_drone_force:
            for target in selected_building_targets:
                if self.is_being_attacked(target) < 3:
                    self.main.add_action(available_drone_force.closest_to(target).attack(target))
