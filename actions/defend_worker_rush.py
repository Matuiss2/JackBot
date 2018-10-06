import heapq
from .micro import micro
from sc2.constants import (
    HATCHERY,
    PROBE, DRONE, SCV
)

class DefendWorkerRush(micro):

    def __init__(self, ai):
        self.ai = ai
        self.base = None
        self.enemy_units_close = None
        self.defenders = None
        self.defender_tags = None

    async def should_handle(self, iteration):
        self.base = self.ai.hatcheries.ready
        if not self.base:
            return False

        self.enemy_units_close = self.ai.known_enemy_units.closer_than(8, self.base.first).of_type([PROBE, DRONE, SCV])
        return (
            self.enemy_units_close and not self.defender_tags
            or self.defender_tags and not self.enemy_units_close
            or self.defender_tags and self.enemy_units_close
        )

    async def handle(self, iteration):
        """It destroys every worker rush without losing more than 2 workers,
         it counter scouting worker rightfully now, its too big and can be split"""

        if self.enemy_units_close and not self.defender_tags:
            self.build_defense_force(len(self.enemy_units_close))

        if self.defender_tags and not self.enemy_units_close:
            self.clear_defense_force(self.base)

        if self.defender_tags and self.enemy_units_close:
            self.refill_defense_force(len(self.enemy_units_close))

            for drone in self.defenders:
                # 6 hp is the lowest you can take a hit and still survive
                if not self.save_lowhp_drone(drone, self.base):
                    if drone.weapon_cooldown <= 0.60:
                        self.attack_close_target(drone, self.enemy_units_close)
                    else:
                        if not self.move_to_next_target(drone, self.enemy_units_close):
                            self.move_lowhp(drone, self.enemy_units_close)

    def save_lowhp_drone(self, drone, base):
        if drone.health <= 6:
            if not drone.is_collecting:
                mineral_field = self.ai.state.mineral_field.closest_to(base.first.position)
                self.ai.actions.append(drone.gather(mineral_field))
            else:
                self.defender_tags.remove(drone.tag)
            return True
        return False

    def build_defense_force(self, enemy_count):
        self.defender_tags = self.defense_force(2 * enemy_count)

    def refill_defense_force(self, enemy_count):
        self.defenders = self.ai.drones.filter(lambda worker: worker.tag in self.defender_tags and worker.health > 0)
        defender_deficit = self.calculate_defender_deficit(enemy_count)

        if defender_deficit > 0:
            additional_drones = self.defense_force(defender_deficit)
            self.defender_tags = self.defender_tags + additional_drones

    def clear_defense_force(self, base):
        if self.defenders:
            for drone in self.defenders:
                self.ai.actions.append(drone.gather(self.ai.state.mineral_field.closest_to(base.first)))
                continue
        self.defender_tags = []
        self.defenders = None

    def defense_force(self, count):
        highest_hp_drones = self.highest_hp_drones(count)
        return [unit.tag for unit in highest_hp_drones]

    def highest_hp_drones(self, count):
        return heapq.nlargest(count, self.ai.drones.collecting, key=lambda drones: drones.health)

    def calculate_defender_deficit(self, enemy_count):
        return min(len(self.ai.drones) - 1, 2 * enemy_count) - len(self.defenders)
