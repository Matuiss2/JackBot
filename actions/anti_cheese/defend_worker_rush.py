"""Everything related to defending a worker rush goes here"""
import heapq
from sc2.constants import DRONE, PROBE, SCV
from actions.micro.micro_helpers import Micro


class DefendWorkerRush(Micro):
    """Ok for now, but probably can be expanded to handle more than just worker rushes"""

    def __init__(self, main):
        self.main = main
        self.base = self.enemy_units_close = self.defenders = self.defender_tags = self.pulling_force = None

    async def should_handle(self):
        """Requirements to run handle"""
        self.base = self.main.hatcheries.ready
        if not self.base:
            return False
        self.enemy_units_close = self.main.enemies.closer_than(8, self.base.first).of_type({PROBE, DRONE, SCV})
        return self.enemy_units_close or self.defender_tags

    async def handle(self):
        """It destroys every worker rush without losing more than 2 workers"""
        close_workers = self.enemy_units_close
        self.pulling_force = int(len(close_workers) * 1.25)
        if self.defender_tags:
            if close_workers:
                self.refill_defense_force()
                for drone in self.defenders:
                    if not self.save_lowhp_drone(drone):
                        if drone.weapon_cooldown <= 13.4:  # Wanted cd value * 22.4
                            self.attack_close_target(drone, close_workers)
                        elif not self.move_to_next_target(drone, close_workers):
                            self.move_lowhp(drone, close_workers)
            else:
                self.clear_defense_force()
        elif close_workers:
            self.defender_tags = self.defense_force(self.pulling_force)

    def clear_defense_force(self):
        """If there is more workers on the defenders force than the ideal put it back to mining"""
        if self.defenders:
            for drone in self.defenders:
                self.main.add_action(drone.gather(self.main.state.mineral_field.closest_to(self.base.first)))
            self.defender_tags = []
            self.defenders = None

    def defense_force(self, count):
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

    def refill_defense_force(self):
        """If there are less workers on the defenders force than the ideal refill it"""
        self.defenders = self.main.drones.filter(lambda worker: worker.tag in self.defender_tags and worker.health > 0)
        defender_deficit = min(self.main.drone_amount - 1, self.pulling_force) - len(self.defenders)
        if defender_deficit > 0:
            self.defender_tags += self.defense_force(defender_deficit)

    def save_lowhp_drone(self, drone):
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
