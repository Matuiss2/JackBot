"""Everything related to handling very close proxies with drones goes here"""
from sc2.constants import (
    BUNKER,
    DRONE,
    PHOTONCANNON,
    PLANETARYFORTRESS,
    PROBE,
    SCV,
    SPINECRAWLER,
    AUTOTURRET,
    BARRACKS,
    GATEWAY,
)


class DefendRushBuildings:
    """Needs improvements on the quantity"""

    def __init__(self, ai):
        self.ai = ai
        self.rush_buildings = None

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        if local_controller.bases:
            self.rush_buildings = local_controller.enemy_structures.exclude_type(
                {AUTOTURRET, BARRACKS, GATEWAY}
            ).closer_than(50, local_controller.bases.furthest_to(local_controller.game_info.map_center))
        return (
            self.rush_buildings
            and local_controller.time <= 270
            and len(local_controller.drones) >= 15
            and not local_controller.ground_enemies.exclude_type(PROBE)
        )

    def is_being_attacked(self, unit):
        """Only for enemy units, returns how often they are attacked"""
        attackers = 0
        near_units = self.ai.units.filter(lambda x: x.is_attacking)
        for attacker in near_units:
            if attacker.order_target == unit.tag:
                attackers += 1
        return attackers

    async def handle(self, iteration):
        """Send workers aggressively to handle the near proxy / cannon rush, need to learn how to get the max
         surface area possible when attacking the buildings"""
        local_controller = self.ai
        action = local_controller.add_action
        # self.rush_buildings = local_controller.known_enemy_structures.closer_than(20, self.bases.first)
        enemy_worker = local_controller.known_enemy_units.of_type({PROBE, DRONE, SCV}).filter(
            lambda unit: any([unit.distance_to(our_building) <= 50 for our_building in local_controller.structures])
        )
        for target in enemy_worker:
            available = local_controller.drones.filter(lambda x: x.is_collecting and not x.is_attacking)
            if not self.is_being_attacked(target) and available:
                attacker = available.closest_to(target)
                action(attacker.attack(target))
        attacking_buildings = self.rush_buildings.of_type({SPINECRAWLER, PHOTONCANNON, BUNKER, PLANETARYFORTRESS})
        not_attacking_buildings = self.rush_buildings - attacking_buildings
        if attacking_buildings:
            for target in attacking_buildings:
                attackers_needed = 3
                available = local_controller.drones.filter(
                    lambda x: x.order_target not in [y.tag for y in attacking_buildings]
                )  # filter x with not target order in attacking buildings
                if attackers_needed > self.is_being_attacked(target) and available:
                    attacker = available.closest_to(target)
                    action(attacker.attack(target))
        if not_attacking_buildings:
            for target in not_attacking_buildings:
                attackers_needed = 3
                available = local_controller.drones.filter(lambda x: x.is_collecting and not x.is_attacking)
                if attackers_needed > self.is_being_attacked(target) and available:
                    attacker = available.closest_to(target)
                    action(attacker.attack(target))
