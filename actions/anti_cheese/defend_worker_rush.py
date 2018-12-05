"""Everything related to defending a worker rush goes here"""
import heapq

from sc2.constants import DRONE, PROBE, SCV

from actions.micro.micro_helpers import Micro


class DefendWorkerRush(Micro):
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai
        self.base = None
        self.enemy_units_close = None
        self.defenders = None
        self.defender_tags = None

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        self.base = local_controller.hatcheries.ready
        if not self.base:
            return False

        self.enemy_units_close = local_controller.enemies.closer_than(8, self.base.first).of_type({PROBE, DRONE, SCV})
        return (
            self.enemy_units_close
            and not self.defender_tags
            or self.defender_tags
            and not self.enemy_units_close
            or self.defender_tags
            and self.enemy_units_close
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
                    if drone.weapon_cooldown <= 0.60 * 22.4:
                        self.attack_close_target(drone, self.enemy_units_close)
                    elif not self.move_to_next_target(drone, self.enemy_units_close):
                        self.move_lowhp(drone, self.enemy_units_close)

    def save_lowhp_drone(self, drone, base):
        """Remove drones with less 6 hp from the defending force"""
        local_controller = self.ai
        if drone.health <= 6:
            if not drone.is_collecting:
                local_controller.add_action(
                    drone.gather(local_controller.state.mineral_field.closest_to(base.first.position))
                )
            else:
                self.defender_tags.remove(drone.tag)
            return True
        return False

    def build_defense_force(self, enemy_count):
        """Finds the right amount for the defense force(max twice of the attacker number ideally)"""
        self.defender_tags = self.defense_force(enemy_count + enemy_count)

    def refill_defense_force(self, enemy_count):
        """If there is less workers on the defenders force than the ideal refill it"""
        self.defenders = self.ai.drones.filter(lambda worker: worker.tag in self.defender_tags and worker.health > 0)
        defender_deficit = self.calculate_defender_deficit(enemy_count)
        if defender_deficit > 0:
            additional_drones = self.defense_force(defender_deficit)
            self.defender_tags = self.defender_tags + additional_drones

    def clear_defense_force(self, base):
        """If there is more workers on the defenders force than the ideal put it back to mining"""
        local_controller = self.ai
        if self.defenders:
            for drone in self.defenders:
                local_controller.add_action(drone.gather(local_controller.state.mineral_field.closest_to(base.first)))
        self.defender_tags = []
        self.defenders = None

    def defense_force(self, count):
        """Put all drones needed on the defenders force - order based on health"""
        return [unit.tag for unit in self.highest_hp_drones(count)]

    def highest_hp_drones(self, count):
        """Order the drones based on health(highest first)"""
        return heapq.nlargest(count, self.ai.drones.collecting, key=lambda drones: drones.health)

    def calculate_defender_deficit(self, enemy_count):
        """Calculates the deficit on the defense force"""
        return min(len(self.ai.drones) - 1, enemy_count + enemy_count) - len(self.defenders)
