"""Everything related to training ultralisks goes here"""
from sc2.constants import ULTRALISK


class TrainUltralisk:
    """Good for now but it might need to be changed vs particular enemy units compositions"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirement for training ultralisks"""
        return self.controller.can_train(ULTRALISK, self.controller.caverns.ready)

    async def handle(self):
        """Execute the action of training ultralisks"""
        self.controller.add_action(self.controller.larvae.random.train(ULTRALISK))
        return True
