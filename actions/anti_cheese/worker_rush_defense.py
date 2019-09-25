"""Everything related to defending a worker rush goes here"""
import heapq
from sc2.constants import UnitTypeId
from actions.micro.micro_helpers import MicroHelpers


class WorkerRushDefense(MicroHelpers):
    """Ok for now, but probably can be expanded to handle more than just worker rushes"""

    def __init__(self, main):
        self.main = main
        self.base = self.close_enemy_workers = self.defender_tags = self.defense_force = self.defense_force_size = None
        self.worker_types = {UnitTypeId.DRONE, UnitTypeId.PROBE, UnitTypeId.SCV}

    async def should_handle(self):
        """Requirements to run handle"""
        self.base = self.main.hatcheries.ready
        if not self.base:
            return False
        self.close_enemy_workers = self.main.enemies.closer_than(8, self.base.first).of_type(self.worker_types)
        return self.close_enemy_workers or self.defender_tags

    async def handle(self):
        """It destroys every worker rush without losing more than 2 workers"""
        self.defense_force_size = int(len(self.close_enemy_workers) * 1.25)
        if self.defender_tags:
            if self.close_enemy_workers:
                self.refill_defense_force()
                for drone in self.defense_force:
                    if not self.save_low_hp_drone(drone):
                        if drone.weapon_cooldown <= 13.4:  # Wanted cd value * 22.4
                            self.attack_close_target(drone, self.close_enemy_workers)
                        elif not self.move_to_next_target(drone, self.close_enemy_workers):
                            self.move_low_hp(drone, self.close_enemy_workers)
            else:
                self.clear_defense_force()
        elif self.close_enemy_workers:
            self.defender_tags = self.select_defense_force(self.defense_force_size)

    def clear_defense_force(self):
        """If there is more workers on the defenders force than the ideal put it back to mining"""
        if self.defense_force:
            selected_mineral_field = self.main.state.mineral_field.closest_to(self.base.first)
            for drone in self.defense_force:
                self.main.add_action(drone.gather(selected_mineral_field))
            self.defender_tags = []
            self.defense_force = None

    def refill_defense_force(self):
        """If there are less workers on the defenders force than the ideal refill it"""
        self.defense_force = self.main.drones.filter(lambda worker: worker.tag in self.defender_tags and worker.health)
        defender_deficit = min(self.main.drone_amount - 1, self.defense_force_size) - len(self.defense_force)
        if defender_deficit > 0:
            self.defender_tags += self.select_defense_force(defender_deficit)

    def save_low_hp_drone(self, drone):
        """
        Remove drones with less 6 hp(one worker hit) from the defending force
        Parameters
        ----------
        drone: A drone from the defenders force

        Returns
        -------
        True if the drone got removed from the force, False if the drone doesn't need to be removed
        """
        if drone.health <= 6:
            if not drone.is_collecting:
                self.main.add_action(drone.gather(self.main.state.mineral_field.closest_to(self.base.first.position)))
            else:
                self.defender_tags.remove(drone.tag)
            return True
        return False

    def select_defense_force(self, count):
        """
        Select all drones needed on the defenders force
        Parameters
        ----------
        count: The needed amount of drones to fill the defense force

        Returns
        -------
        A list with all drones that are part of the defense force, ordered by health(highest one prioritized)
        """
        return [unit.tag for unit in heapq.nlargest(count, self.main.drones.collecting, key=lambda dr: dr.health)]
