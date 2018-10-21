"""Everything related to training ultralisks goes here"""
from sc2.constants import ULTRALISK, ZERGGROUNDARMORSLEVEL3


class TrainUltralisk:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Good for now but it might need to be changed vs particular
         enemy units compositions"""
        local_controller = self.ai
        if not local_controller.caverns.ready:
            return False

        if not local_controller.already_pending_upgrade(ZERGGROUNDARMORSLEVEL3) and local_controller.time > 780:
            return False

        if not local_controller.can_train(ULTRALISK):
            return False

        return True

    async def handle(self, iteration):
        """Execute the action of training ultralisks"""
        local_controller = self.ai
        local_controller.add_action(local_controller.larvae.random.train(ULTRALISK))
        return True
