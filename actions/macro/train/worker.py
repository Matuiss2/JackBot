"""Everything related to training drones goes here"""
import numpy as np
from sc2.constants import DRONE, OVERLORD


class TrainWorker:
    """Needs improvements, its very greedy sometimes"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Should this action be handled, needs more smart limitations, its very greedy sometimes"""
        workers_total = len(self.controller.workers)
        geysers = self.controller.extractors
        drones_in_queue = self.controller.already_pending(DRONE)
        if (
            not self.controller.close_enemies_to_base
            and self.controller.can_train(DRONE)
            and not self.controller.counter_attack_vs_flying
        ):
            if workers_total == 12 and not drones_in_queue:
                return True
            if (
                workers_total in (13, 14, 15)
                and len(self.controller.overlords) + self.controller.already_pending(OVERLORD) > 1
            ):
                return True
            optimal_workers = min(
                sum(x.ideal_harvesters * 1.35 for x in self.controller.townhalls | geysers), 81 - len(geysers)
            )
            return (
                workers_total + drones_in_queue < optimal_workers
                and np.sum(
                    np.array(
                        [len(self.controller.zerglings), len(self.controller.hydras), len(self.controller.ultralisks)]
                    )
                    * np.array([1, 2, 3])
                )
                > 17
            )
        return False

    async def handle(self):
        """Execute the action of training drones"""
        self.controller.add_action(self.controller.larvae.random.train(DRONE))
        return True
