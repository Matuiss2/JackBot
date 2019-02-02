"""Everything related to training mutalisks goes here"""
from sc2.constants import MUTALISK


class TrainMutalisk:
    """Untested"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirements to train mutalisks, maybe some locks are needed"""
        local_controller = self.controller
        return local_controller.can_train(MUTALISK, local_controller.spires.ready)

    async def handle(self):
        """Execute the action of training mutas"""
        local_controller = self.controller
        local_controller.add_action(local_controller.larvae.random.train(MUTALISK))
        return True
