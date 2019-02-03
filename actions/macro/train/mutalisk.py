"""Everything related to training mutalisks goes here"""
from sc2.constants import MUTALISK


class TrainMutalisk:
    """Untested"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirements to train mutalisks, maybe some locks are needed"""
        return self.controller.can_train(MUTALISK, self.controller.spires.ready)

    async def handle(self):
        """Execute the action of training mutas"""
        self.controller.add_action(self.controller.larvae.random.train(MUTALISK))
        return True
