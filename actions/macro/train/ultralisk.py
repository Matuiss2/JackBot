"""Everything related to training ultralisks goes here"""
from sc2.constants import ULTRALISK


class TrainUltralisk:
    """Good for now but it might need to be changed vs particular enemy units compositions"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirement for training ultralisks"""
        return self.main.can_train(ULTRALISK, self.main.caverns.ready)

    async def handle(self):
        """Execute the action of training ultralisks"""
        self.main.add_action(self.main.larvae.random.train(ULTRALISK))
