"""Everything related to handling very close proxies with drones goes here"""
from sc2.constants import (
    AUTOTURRET,
    BARRACKS,
    BUNKER,
    DRONE,
    GATEWAY,
    PHOTONCANNON,
    PLANETARYFORTRESS,
    PROBE,
    SCV,
    SPINECRAWLER,
)


class DefendProxies:
    """Needs improvements on the quantity"""

    def __init__(self, main):
        self.controller = main
        self.rush_buildings = None

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.controller
        if local_controller.townhalls:
            self.rush_buildings = local_controller.enemy_structures.exclude_type(
                {AUTOTURRET, BARRACKS, GATEWAY}
            ).closer_than(50, local_controller.townhalls.furthest_to(local_controller.game_info.map_center))
        return (
            self.rush_buildings
            and local_controller.time <= 270
            and len(local_controller.drones) >= 15
            and not local_controller.ground_enemies
        )

    def is_being_attacked(self, unit):
        """Only for enemy units, returns how often they are attacked"""
        return len(
            [
                "attacker"
                for attacker in self.controller.units.filter(lambda x: x.is_attacking)
                if attacker.order_target == unit.tag
            ]
        )

    def pull_drones(self, mode, available):
        """Pull 3 drones to destroy the proxy building"""
        for target in mode:
            if self.is_being_attacked(target) < 3 and available:
                self.controller.add_action(available.closest_to(target).attack(target))

    async def handle(self):
        """Send workers aggressively to handle the near proxy / cannon rush, need to learn how to get the max
         surface area possible when attacking the buildings"""
        local_controller = self.controller
        drones = local_controller.drones
        available = drones.filter(lambda x: x.is_collecting and not x.is_attacking)
        # self.rush_buildings = local_controller.enemy_structures.closer_than(20, self.townhalls.first)
        for worker in local_controller.enemies.of_type({PROBE, DRONE, SCV}).filter(
            lambda unit: any(unit.distance_to(our_building) <= 50 for our_building in local_controller.structures)
        ):
            if not self.is_being_attacked(worker) and available:
                local_controller.add_action(available.closest_to(worker).attack(worker))
        attacking_buildings = self.rush_buildings.of_type({SPINECRAWLER, PHOTONCANNON, BUNKER, PLANETARYFORTRESS})
        not_attacking_buildings = self.rush_buildings - attacking_buildings
        if attacking_buildings:
            available = drones.filter(
                lambda x: x.order_target not in [y.tag for y in attacking_buildings]
            )  # filter x with not target order in attacking buildings
            self.pull_drones(attacking_buildings, available)
        if not_attacking_buildings:
            self.pull_drones(not_attacking_buildings, available)
