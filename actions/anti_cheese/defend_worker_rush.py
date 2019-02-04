"""Everything related to defending a worker rush goes here"""
import heapq

from sc2.constants import DRONE, PROBE, SCV

from actions.micro.micro_helpers import Micro


class DefendWorkerRush(Micro):
    """Ok for now, but probably can be expanded to handle more than just worker rushes"""

    def __init__(self, main):
        self.controller = main
        self.base = self.enemy_units_close = self.defenders = self.defender_tags = None

    async def should_handle(self):
        """Requirements to run handle"""
        self.base = self.controller.hatcheries.ready
        if not self.base:
            return False
        self.enemy_units_close = self.controller.enemies.closer_than(8, self.base.first).of_type({PROBE, DRONE, SCV})
        return self.enemy_units_close or self.defender_tags

    async def handle(self):
        """It destroys every worker rush without losing more than 2 workers"""
        close_workers = self.enemy_units_close
        enemy_worker_force = len(close_workers)
        if self.defender_tags:
            if close_workers:
                self.refill_defense_force(enemy_worker_force)
                for drone in self.defenders:
                    if not self.save_lowhp_drone(drone, self.base):
                        if drone.weapon_cooldown <= 13.4:  # Wanted cd value * 22.4
                            self.attack_close_target(drone, close_workers)
                        elif not self.move_to_next_target(drone, close_workers):
                            self.move_lowhp(drone, close_workers)
            else:
                self.clear_defense_force(self.base)
        elif close_workers:
            self.defender_tags = self.defense_force(enemy_worker_force * 2)

    def save_lowhp_drone(self, drone, base):
        """Remove drones with less 6 hp(one worker hit) from the defending force"""
        if drone.health <= 6:
            if not drone.is_collecting:
                self.controller.add_action(
                    drone.gather(self.controller.state.mineral_field.closest_to(base.first.position))
                )
            else:
                self.defender_tags.remove(drone.tag)
            return True
        return False

    def refill_defense_force(self, enemy_count):
        """If there are less workers on the defenders force than the ideal refill it"""
        self.defenders = self.controller.drones.filter(
            lambda worker: worker.tag in self.defender_tags and worker.health > 0
        )
        defender_deficit = min(len(self.controller.drones) - 1, enemy_count + enemy_count) - len(self.defenders)
        if defender_deficit > 0:
            additional_drones = self.defense_force(defender_deficit)
            self.defender_tags = self.defender_tags + additional_drones

    def clear_defense_force(self, base):
        """If there is more workers on the defenders force than the ideal put it back to mining"""
        if self.defenders:
            for drone in self.defenders:
                self.controller.add_action(drone.gather(self.controller.state.mineral_field.closest_to(base.first)))
            self.defender_tags = []
            self.defenders = None

    def defense_force(self, count):
        """Put all drones needed on the defenders force - Order the drones based on health(highest first)"""
        return [
            unit.tag
            for unit in heapq.nlargest(count, self.controller.drones.collecting, key=lambda drones: drones.health)
        ]
