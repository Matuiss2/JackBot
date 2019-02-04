"""Everything related to training hydralisks goes here"""
from sc2.constants import HYDRALISK


class TrainHydralisk:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirements to train the hydralisks"""
        cavern = self.controller.caverns
        if self.controller.hives and not cavern:
            return False
        if not self.controller.can_train(HYDRALISK, self.controller.hydradens.ready):
            return False
        if cavern.ready:
            return len(self.controller.ultralisks) * 3.5 > self.controller.hydra_amount
        return not self.controller.floating_buildings_bm

    async def handle(self):
        """Execute the action of training hydras"""
        self.controller.add_action(self.controller.larvae.random.train(HYDRALISK))
        return True
