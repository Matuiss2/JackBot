"""Everything related to training drones goes here"""
from sc2.constants import DRONE, OVERLORD


class TrainWorker:
    """Needs improvements, its very greedy sometimes"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Should this action be handled, needs more smart limitations, its very greedy sometimes"""
        workers_total = self.main.drone_amount
        geysers = self.main.extractors
        drones_in_queue = self.main.already_pending(DRONE)
        if (
            not self.main.close_enemies_to_base
            and self.main.can_train(DRONE)
            and not self.main.counter_attack_vs_flying
        ):
            if workers_total == 12 and not drones_in_queue:
                return True
            if workers_total in (13, 14, 15) and self.main.overlord_amount + self.main.already_pending(OVERLORD) > 1:
                return True
            optimal_workers = min(
                sum(x.ideal_harvesters * 1.25 for x in self.main.townhalls | geysers), 88 - len(geysers)
            )
            return workers_total + drones_in_queue < optimal_workers and self.main.zergling_amount > 15
        return False

    async def handle(self):
        """Execute the action of training drones"""
        self.main.add_action(self.main.larvae.random.train(DRONE))
        return True
