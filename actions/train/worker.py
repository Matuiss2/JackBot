"""Everything related to training drones goes here"""
import numpy as np
from sc2.constants import DRONE, OVERLORD


class TrainWorker:
    """Needs improvements, its very greedy sometimes"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Should this action be handled, needs more smart limitations, its very greedy sometimes"""
        local_controller = self.ai
        workers_total = len(local_controller.workers)
        geysirs = local_controller.extractors
        drones_in_queue = local_controller.already_pending(DRONE)
        if (
            not local_controller.close_enemies_to_base
            and local_controller.can_train(DRONE)
            and not local_controller.counter_attack_vs_flying
        ):
            if workers_total == 12 and not drones_in_queue and local_controller.time < 200:
                return True
            if (
                workers_total in (13, 14, 15)
                and len(local_controller.overlords) + local_controller.already_pending(OVERLORD) > 1
            ):
                return True
            optimal_workers = min(
                sum(x.ideal_harvesters for x in local_controller.townhalls | geysirs), 90 - len(geysirs)
            )
            return (
                workers_total + drones_in_queue < optimal_workers
                and np.sum(
                    np.array(
                        [
                            len(local_controller.zerglings),
                            len(local_controller.hydras),
                            len(local_controller.ultralisks),
                        ]
                    )
                    * np.array([1, 2, 3])
                )
                > 15
            )
        return False

    async def handle(self, iteration):
        """Execute the action of training drones"""
        local_controller = self.ai
        local_controller.add_action(local_controller.larvae.random.train(DRONE))
        return True
