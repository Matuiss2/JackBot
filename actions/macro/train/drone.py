"""Everything related to training drones goes here"""
from sc2.constants import UnitTypeId


class TrainDrone:
    """Needs improvements, its very greedy sometimes"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Should this action be handled, needs more smart limitations, its very greedy sometimes"""
        workers_total = self.main.drone_amount
        geysers = self.main.extractors
        if (
            not self.main.close_enemies_to_base
            and self.main.can_train(UnitTypeId.DRONE)
            and not self.main.counter_attack_vs_flying
        ):
            if workers_total == 12 and not self.main.drones_in_queue:
                return True
            if workers_total in (13, 14, 15) and self.main.overlord_amount + self.main.ovs_in_queue > 1:
                return True
            optimal_workers = min(
                sum(x.ideal_harvesters * 1.15 for x in self.main.townhalls | geysers), 91 - len(geysers)
            )
            return workers_total + self.main.drones_in_queue < optimal_workers and self.main.zergling_amount >= 18
        return False

    async def handle(self):
        """Execute the action of training drones"""
        self.main.add_action(self.main.larvae.random.train(UnitTypeId.DRONE))
