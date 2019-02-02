"""Everything related to training ultralisks goes here"""
from sc2.constants import ULTRALISK


class TrainUltralisk:
    """Good for now but it might need to be changed vs particular enemy units compositions"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirement for training ultralisks"""
        local_controller = self.controller
        return local_controller.can_train(ULTRALISK, local_controller.caverns.ready)

    async def handle(self):
        """Execute the action of training ultralisks"""
        local_controller = self.controller
        local_controller.add_action(local_controller.larvae.random.train(ULTRALISK))
        return True
