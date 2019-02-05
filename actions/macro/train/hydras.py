"""Everything related to training hydralisks goes here"""
from sc2.constants import HYDRALISK


class TrainHydralisk:
    """Ok for now"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirements to train the hydralisks"""
        if not self.main.can_train(HYDRALISK, self.main.hydradens.ready):
            return False
        if self.main.caverns.ready:
            return len(self.main.ultralisks) * 4 > self.main.hydra_amount
        return not self.main.floating_buildings_bm

    async def handle(self):
        """Execute the action of training hydras"""
        self.main.add_action(self.main.larvae.random.train(HYDRALISK))
        return True
