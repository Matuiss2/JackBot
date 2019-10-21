"""Everything related to training drones goes here"""
from sc2.constants import UnitTypeId


class DroneCreation:
    """Needs improvements, its very greedy sometimes"""

    def __init__(self, main):
        self.main = main
        self.workers_total = None

    async def should_handle(self):
        """Should this action be handled, needs more smart limitations, its very greedy sometimes"""
        self.workers_total = self.main.drone_amount
        if self.general_drone_requirements:
            if self.drone_building_on_beginning:
                return True
            extractors = self.main.extractors  # to save lines
            workers_optimal_amount = min(sum(mp.ideal_harvesters * 1.15 for mp in self.main.townhalls | extractors), 91)
            if self.workers_total + self.main.drones_in_queue < workers_optimal_amount:
                return self.main.zergling_amount >= 18 or (self.main.time >= 840 and self.main.drones_in_queue < 3)
        return False

    async def handle(self):
        """Execute the action of training drones"""
        self.main.do(self.main.larvae.random.train(UnitTypeId.DRONE))

    @property
    def drone_building_on_beginning(self):
        """Requirements for building drones on the early game"""
        if self.workers_total == 12 and not self.main.drones_in_queue:
            return True
        if self.workers_total in (13, 14, 15) and self.main.overlord_amount + self.main.ovs_in_queue > 1:
            return True
        return False

    @property
    def general_drone_requirements(self):
        """Constant requirements for building drones"""
        return (
            not self.main.close_enemies_to_base
            and self.main.can_train(UnitTypeId.DRONE)
            and not self.main.counter_attack_vs_flying
        )
