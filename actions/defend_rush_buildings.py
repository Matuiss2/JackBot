from sc2.constants import BUNKER, DRONE, PHOTONCANNON, PLANETARYFORTRESS, PROBE, SCV, SPINECRAWLER


class DefendRushBuildings:
    def __init__(self, ai):
        self.ai = ai
        self.rush_buildings = None

    async def should_handle(self, iteration):
        self.rush_buildings = self.ai.known_enemy_structures.not_flying.filter(
            lambda building: any(
                [
                    building.distance_to(our_building) <= 30
                    for our_building in (self.ai.units.structure - self.ai.tumors)
                ]
            )
        )
        return self.rush_buildings and self.ai.bases

    def is_being_attacked(self, unit):
        # only for enemy units, returns how often they are attacked
        attackers = 0
        near_units = self.ai.units.filter(lambda x: x.is_attacking)
        for attacker in near_units:
            if attacker.order_target == unit.tag:
                attackers += 1
        return attackers

    async def handle(self, iteration):
        # self.rush_buildings = self.ai.known_enemy_structures.closer_than(20, self.bases.first)
        enemy_worker = self.ai.known_enemy_units.of_type([PROBE, DRONE, SCV]).filter(
            lambda unit: any([unit.distance_to(our_building) <= 30 for our_building in self.ai.units.structure])
        )
        for target in enemy_worker:
            available = self.ai.drones.filter(lambda x: x.is_collecting and not x.is_attacking)
            if not self.is_being_attacked(target) and available:
                attacker = available.closest_to(target)
                self.ai.actions.append(attacker.attack(target))
        attacking_buildings = self.rush_buildings.of_type({SPINECRAWLER, PHOTONCANNON, BUNKER, PLANETARYFORTRESS})
        not_attacking_buildings = self.rush_buildings - attacking_buildings
        if attacking_buildings:
            for target in attacking_buildings:
                attackers_needed = int(target.radius * 3)
                available = self.ai.drones.filter(
                    lambda x: x.order_target not in [y.tag for y in attacking_buildings]
                )  # filter x with not target order in attacking buildings
                if attackers_needed > self.is_being_attacked(target) and available:
                    attacker = available.closest_to(target)
                    self.ai.actions.append(attacker.attack(target))

        if not_attacking_buildings:
            for target in not_attacking_buildings:
                attackers_needed = int(target.radius * 3)
                available = self.ai.drones.filter(lambda x: x.is_collecting and not x.is_attacking)
                if attackers_needed > self.is_being_attacked(target) and available:
                    attacker = available.closest_to(target)
                    self.ai.actions.append(attacker.attack(target))
