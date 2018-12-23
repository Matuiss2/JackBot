"""Everything related to training ultralisks goes here"""
from sc2.constants import ULTRALISK, ZERGGROUNDARMORSLEVEL3


class TrainUltralisk:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Good for now but it might need to be changed vs particular
         enemy units compositions"""
        local_controller = self.controller
        if local_controller.time >= 1050 and not local_controller.already_pending_upgrade(ZERGGROUNDARMORSLEVEL3):
            return False
        return local_controller.can_train(ULTRALISK, local_controller.caverns.ready)

    async def handle(self):
        """Execute the action of training ultralisks"""
        local_controller = self.controller
        local_controller.add_action(local_controller.larvae.random.train(ULTRALISK))
        return True
